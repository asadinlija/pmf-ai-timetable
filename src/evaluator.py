from config import HARD_PENAL, REDOVNO_ZAPOSLENI, TEZINE, DANI
from math import ceil

def provjeri_redovno_zaposlenje(nastavnik):
    return any(r.lower() in nastavnik.lower() for r in REDOVNO_ZAPOSLENI)

def termin_u_broj(termin):
    return DANI.index(termin[0]) * 12 + termin[1]

def procijeni_dane_i_sate(dani_profesora, dozvoljeni_dani=None, zabranjeni_dani=None, min_slot=None, max_slot=None):
    prekrsaji = 0
    for dan, slotovi in dani_profesora.items():
        if dozvoljeni_dani and dan not in dozvoljeni_dani:
            prekrsaji += len(slotovi)
            continue
        if zabranjeni_dani and dan in zabranjeni_dani:
            prekrsaji += len(slotovi)
            continue
        for slot in slotovi:
            if min_slot and slot < min_slot:
                prekrsaji += 1
            if max_slot and slot > max_slot:
                prekrsaji += 1
    return prekrsaji

def procijeni_broj_radnih_dana(dani_profesora, max_dana):
    radni_dani = sum(1 for s in dani_profesora.values() if s)
    return max(0, radni_dani - max_dana)

def procijeni_rad_u_bloku(dani_profesora):
    prekrsaji = 0
    for dan, jedinstveni_slotovi in dani_profesora.items():
        if not jedinstveni_slotovi:
            continue
        slotovi = sorted(list(jedinstveni_slotovi))
        for i in range(len(slotovi)-1):
            razlika = slotovi[i+1] - slotovi[i]
            if razlika > 1:
                prekrsaji += (razlika - 1)
    return prekrsaji


def evaluiraj_raspored(raspored, zaduzenja, ucionice):
    debug_h1 = 0
    debug_h2 = 0
    debug_h3 = 0
    debug_h4 = 0
    debug_h5 = 0
    debug_h6 = 0
    debug_h7 = 0
    debug_h8 = 0
    debug_h9 = 0
    max_kapacitet_nastava = max(u["kapacitet_nastave"] for u in ucionice.values() if u["tip_ucionice"] != "racunarski_kabinet")
    max_kapacitet_lv = max(u["kapacitet_lv_vjezbi"] for u in ucionice.values() if u["tip_ucionice"] == "racunarski_kabinet")

    ukupna_tvrda_kazna = 0
    ukupna_meka_kazna = 0

    po_terminima = {}      
    po_predmetima = {}     # (predmet_id, tip) -> lista stavki
    po_grupama_danima = {} # (grupa, dan) -> set slotova
    po_grupama_s3 = {}     # grupa -> {dan: broj_sati}
    termini_s5 = {}        # (grupa, predmet_id) -> {"P": [], "AV_LV": []}
    raspored_nastavnici = {} # (nastavnik, dan) -> set slotova
    raspored_profesora = {}  # prof -> {dan: set(slotovi)}
    casovi_profesora = {}    # prof -> lista stavki
    brojac_h7 = {}         # (predmet_id, tip) -> int

    GRANICA_POPODNE = 7
    RANIJI_SLOTOVI = {1, 2, 3, 4, 5, 6, 7, 8}

    # === JEDAN JEDINI PROLAZ KROZ RESPODRED ===
    for d in raspored:
        termin = d["termin"]
        dan, slot = termin[0], termin[1]
        nastavnik = d["nastavnik"]
        tip = d["tip"]
        pid = d["predmet_id"]
        ucionica_id = d["ucionica"]["id"]
        broj_stud = d["broj_studenata"]
        grupe = d["grupe"]

        # --- H5 ---
        if tip == "LV":
            if d["ucionica"]["kapacitet_lv_vjezbi"] < broj_stud:
                ukupna_tvrda_kazna += HARD_PENAL
                debug_h5 += 1
        else:
            if d["ucionica"]["kapacitet_nastave"] < broj_stud:
                ukupna_tvrda_kazna += HARD_PENAL
                debug_h5 += 1
        # --- H8 ---
        if tip == "LV" and d["ucionica"]["tip_ucionice"] != "racunarski_kabinet":
            ukupna_tvrda_kazna += HARD_PENAL
            debug_h8 += 1

        # --- H9 ---
        if dan == "Četvrtak" and slot == 6:
            if provjeri_redovno_zaposlenje(d["zvanje_nastavnika"]):
                ukupna_tvrda_kazna += HARD_PENAL
                debug_h9 += 1

        # --- S4 ---
        for (smjer, godina) in grupe:
            if godina >= 4 and slot < GRANICA_POPODNE:
                ukupna_meka_kazna += TEZINE["S4"]
                break

        # --- S7 ---
        is_redovni = provjeri_redovno_zaposlenje(nastavnik)
        if not is_redovni and slot in RANIJI_SLOTOVI:
            ukupna_meka_kazna += TEZINE["S7"]

        # --- S8 ---
        if d["predmet"] == "Programiranje I" and tip == "LV" and ucionica_id != "A1":
            ukupna_meka_kazna += TEZINE["S8"]

        # --- Punjenje indeksa za grupne provjere ---
        po_terminima.setdefault(termin, []).append(d)
        po_predmetima.setdefault((pid, tip), []).append(d)
        brojac_h7[(d["predmet_id_orig"], tip)] = brojac_h7.get((d["predmet_id_orig"], tip), 0) + 1

        for g in grupe:
            po_grupama_danima.setdefault((g, dan), set()).add(slot)
            
            dani_g = po_grupama_s3.setdefault(g, {dn: 0 for dn in DANI})
            if dan in dani_g:
                dani_g[dan] += 1
                
            t_s5 = termini_s5.setdefault((g, pid), {"P": [], "AV_LV": []})
            if tip == "P":
                t_s5["P"].append(termin)
            elif tip in ("AV", "LV"):
                t_s5["AV_LV"].append(termin)

        if is_redovni:
            raspored_nastavnici.setdefault((nastavnik, dan), set()).add(slot)

        raspored_profesora.setdefault(nastavnik, {dn: set() for dn in DANI})
        if dan in DANI:
            raspored_profesora[nastavnik][dan].add(slot)
            casovi_profesora.setdefault(nastavnik, []).append(d)


    # === PROVJERA GRUPNIH KONFLIKATA (UMJESTO SVE SA SVAKIM) ===

    # Optimizacija za H1, H2, H3 (Gledamo samo unutar ISTOG TERMINA)
    for termin, stavke in po_terminima.items():
        n = len(stavke)
        if n < 2:
            continue
        for i in range(n):
            a = stavke[i]
            for j in range(i + 1, n):
                b = stavke[j]
                
                # H1
                if a["nastavnik"] == b["nastavnik"]:
                    ukupna_tvrda_kazna += HARD_PENAL
                    debug_h1 += 1
                # H2
                if a["ucionica"]["id"] == b["ucionica"]["id"]:
                    ukupna_tvrda_kazna += HARD_PENAL
                    debug_h2 += 1
                # H3
                if any(g in b["grupe"] for g in a["grupe"]):
                    ukupna_tvrda_kazna += HARD_PENAL
                    debug_h3 += 1

    # Optimizacija za H4 i H6 (Gledamo samo unutar ISTOG PREDMETA I TIPA)
    for (pid, tip), stavke in po_predmetima.items():
        n = len(stavke)
        if n < 2:
            continue
        
        # Unaprijed pretvaramo grupe u setove radi brže komparacije u H4
        setovi_grupa = [set(x["grupe"]) for x in stavke]
        max_kap = max_kapacitet_lv if tip == "LV" else max_kapacitet_nastava

        for i in range(n):
            a = stavke[i]
            set_a = setovi_grupa[i]
            for j in range(i + 1, n):
                b = stavke[j]
                set_b = setovi_grupa[j]
                
                # H4
                if a["termin"] != b["termin"] and set_a != setovi_grupa[j]:
                    ukupna_tvrda_kazna += HARD_PENAL
                    debug_h4 += 1
                
                # H6
                if a["termin"] != b["termin"] and set_a != set_b:
                    # Da li su te dve grupe mogle da stanu zajedno u najveću učionicu?
                    if a["broj_studenata"] + b["broj_studenata"] <= max_kap:
                        ukupna_tvrda_kazna += HARD_PENAL
                        debug_h6 += 1

    # --- H7 ---
    for z in zaduzenja:
        ukupno = brojac_h7.get((z["predmet_id"], z["tip_nastave"]), 0)
    # Izračunaj broj grupa za ovaj predmet
        if z["tip_nastave"] == "LV":
            max_kap_lv = max(u["kapacitet_lv_vjezbi"] for u in ucionice.values() 
                        if u["tip_ucionice"] == "racunarski_kabinet")
            broj_grupa = ceil(z["broj_studenata"] / max_kap_lv) if max_kap_lv > 0 else 1
        else:
            broj_grupa = 1
    
        if ukupno != z["trajanje"] * broj_grupa:
            ukupna_tvrda_kazna += HARD_PENAL

    # --- S1 i S2 (Sve u jednoj iteraciji kroz grupe-dane) ---
    s1_tezina = TEZINE["S1"]
    s2_tezina = TEZINE["S2"]
    for kljuc, jedinstveni_slotovi in po_grupama_danima.items():
        slotovi = sorted(list(jedinstveni_slotovi))
        trenutna_duzina_niza = 1
        
        for i in range(len(slotovi) - 1):
            razlika = slotovi[i+1] - slotovi[i]
            # S1
            if razlika > 1:
                ukupna_meka_kazna += (razlika - 1) * s1_tezina
            # S2 proračun niza
            if razlika == 1:
                trenutna_duzina_niza += 1
            else:
                if trenutna_duzina_niza > 5:
                    ukupna_meka_kazna += (trenutna_duzina_niza - 5) * s2_tezina
                trenutna_duzina_niza = 1
        if trenutna_duzina_niza > 5:
            ukupna_meka_kazna += (trenutna_duzina_niza - 5) * s2_tezina

    # --- S3 ---
    s3_tezina = TEZINE["S3"]
    for grupa, dani_r in po_grupama_s3.items():
        idealno = sum(dani_r.values()) / 5.0
        for dan in DANI:
            ukupna_meka_kazna += abs(dani_r[dan] - idealno) * s3_tezina

    # --- S5 ---
    s5_tezina = TEZINE["S5"]
    for kljuc, tipovi in termini_s5.items():
        if tipovi["P"] and tipovi["AV_LV"]:
            p_brojevi = [termin_u_broj(pt) for pt in tipovi["P"]]
            v_brojevi = [termin_u_broj(vt) for vt in tipovi["AV_LV"]]
            for pb in p_brojevi:
                for vb in v_brojevi:
                    if pb > vb:
                        ukupna_meka_kazna += s5_tezina

    # --- S6 ---
    s6_tezina = TEZINE["S6"]
    for kljuc, jedinstveni_slotovi in raspored_nastavnici.items():
        slotovi = sorted(list(jedinstveni_slotovi))
        for i in range(len(slotovi)-1):
            razlika = slotovi[i+1] - slotovi[i]
            if razlika > 1:
                ukupna_meka_kazna += (razlika - 1) * s6_tezina

    # --- S9 ---
    s9_tezina = TEZINE["S9"]
    for prof, dani in raspored_profesora.items():
        prekrsaji = 0

        if prof == "Senada Kalabušić":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Utorak", "Srijeda"], max_slot=4)
        elif prof == "Amela Muratović-Ribić":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Ponedjeljak", "Utorak", "Srijeda"])
        elif prof == "Esmir Pilav":
            prekrsaji += procijeni_dane_i_sate(dani, zabranjeni_dani=["Petak"], max_slot=6)
        elif prof == "Almasa Odžak":
            prekrsaji += procijeni_broj_radnih_dana(dani, max_dana=2) + procijeni_dane_i_sate(dani, min_slot=3, max_slot=9)
        elif prof == "Dženan Gušić":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Ponedjeljak", "Utorak", "Srijeda"], max_slot=4)
        elif prof == "Hasnija Nurković":
            prekrsaji += procijeni_broj_radnih_dana(dani, max_dana=2) + procijeni_rad_u_bloku(dani)
        elif prof == "Adis Alihodžić":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Utorak", "Srijeda", "Četvrtak"])
        elif prof == "Fikret Čunjalo":
            prekrsaji += procijeni_dane_i_sate(dani, zabranjeni_dani=["Petak"], max_slot=5)
        elif prof == "Elmedin Selmanović":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Ponedjeljak", "Četvrtak"], min_slot=2)
            dani_ciklusa = {} 
            for d in casovi_profesora.get(prof, []):
                dan_casa, slot_casa = d["termin"][0], d["termin"][1]
                if d["predmet_id"] == "77" and dan_casa != "Četvrtak":
                    prekrsaji += 1
                if d["ucionica"]["id"] == "R2":
                    prekrsaji += 0.5 
                
                dani_ciklusa.setdefault(dan_casa, set())
                for grupa in d["grupe"]:
                    dani_ciklusa[dan_casa].add(2 if grupa[1] >= 4 else 1)
            
            for dan_ime, ciklusi in dani_ciklusa.items():
                if len(ciklusi) > 1:
                    prekrsaji += 2
        elif prof == "Zenan Šabanac":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Srijeda", "Četvrtak"], min_slot=2)
        elif prof == "Manuela Muzika Dizdarević":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Utorak", "Petak"])
        elif prof == "Damir Hasić":
            prekrsaji += procijeni_broj_radnih_dana(dani, max_dana=2)
        elif prof == "Dina Kamber Hamzić":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Utorak", "Srijeda", "Četvrtak"], max_slot=5)
        elif prof == "Amil Pečenkovic":
            prekrsaji += procijeni_dane_i_sate(dani, zabranjeni_dani=["Petak"], min_slot=3, max_slot=8)
        elif prof == "Medina Zubača":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Ponedjeljak", "Utorak", "Srijeda"])
        elif prof == "Franjo Šarčević":
            prekrsaji += procijeni_dane_i_sate(dani, zabranjeni_dani=["Ponedjeljak"], max_slot=8)
        elif prof == "Emin Bešo":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Utorak", "Četvrtak"], min_slot=2)
        elif prof == "Sead Delalić":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Ponedjeljak"], min_slot=5)
            for d in casovi_profesora.get(prof, []):
                if d["ucionica"]["id"] not in ["A1", "R2"]: 
                    prekrsaji += 0.5
        elif prof == "Aleksandra Kostić":
            prekrsaji += procijeni_broj_radnih_dana(dani, max_dana=1)
        elif prof == "Lejla Smajlović":
            prekrsaji += procijeni_broj_radnih_dana(dani, max_dana=2) + procijeni_rad_u_bloku(dani)
        elif prof == "Samir Ribić":
            prekrsaji += procijeni_broj_radnih_dana(dani, max_dana=2) + procijeni_rad_u_bloku(dani)
        elif prof == "Emil Ilić-Georgijević":
            prekrsaji += procijeni_broj_radnih_dana(dani, max_dana=1)
        elif prof == "Vedad Letić":
            prekrsaji += procijeni_dane_i_sate(dani, min_slot=9)
        elif prof == "Eldina Delalić":
            prekrsaji += procijeni_dane_i_sate(dani, min_slot=7)
        elif prof == "Imrana Ridžal":
            prekrsaji += procijeni_dane_i_sate(dani, min_slot=8)
        elif prof == "Kemal Altwlkany":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Utorak"], min_slot=7)

        ukupna_meka_kazna += prekrsaji * s9_tezina

    return ukupna_tvrda_kazna + ukupna_meka_kazna

def debug_hard(raspored, zaduzenja, ucionice):
    from config import HARD_PENAL
    from math import ceil
    d_h1=d_h2=d_h3=d_h4=d_h5=d_h6=d_h7=d_h8=d_h9=0
    
    # Osiguravamo ispravno čitanje učionica bez obzira da li je dict ili list
    sve_ucionice = ucionice.values() if isinstance(ucionice, dict) else ucionice
    
    max_kap_nastava = max(u["kapacitet_nastave"] for u in sve_ucionice if u["tip_ucionice"] != "racunarski_kabinet")
    max_kap_lv = max(u["kapacitet_lv_vjezbi"] for u in sve_ucionice if u["tip_ucionice"] == "racunarski_kabinet")
    
    po_terminima = {}
    po_predmetima = {}  # Ovdje grupišemo po SPECIFIČNOJ GRUPI (predmet_id sa sufiksom)
    brojac_h7 = {}      # Ovdje brojim fond po ORIGINALNOM id-ju
    
    for d in raspored:
        dan, slot = d["termin"]
        tip = d["tip"]
        pid_novi = d["predmet_id"] # ID sa sufiksom grupe (npr. 101_G1)
        pid_orig = d.get("predmet_id_orig", d["predmet_id"]) # Originalni ID iz zaduženja
        
        # --- H5 ---
        if tip == "LV":
            if d["ucionica"]["kapacitet_lv_vjezbi"] < d["broj_studenata"]: d_h5 += 1
        else:
            if d["ucionica"]["kapacitet_nastave"] < d["broj_studenata"]: d_h5 += 1
        
        # --- H8 ---
        if tip == "LV" and d["ucionica"]["tip_ucionice"] != "racunarski_kabinet": d_h8 += 1
        
        # --- H9 ---
        if dan == "Četvrtak" and slot == 6 and provjeri_redovno_zaposlenje(d["zvanje_nastavnika"]): d_h9 += 1
        
        # Brojanje fonda radimo preko ORIGINALNOG ID-ja
        brojac_h7[(pid_orig, tip)] = brojac_h7.get((pid_orig, tip), 0) + 1
        
        po_terminima.setdefault(d["termin"], []).append(d)
        
        # Za H4 i H6 grupišemo po NOVOM ID-ju (svaka grupa je predmet za sebe)
        po_predmetima.setdefault((pid_novi, tip), []).append(d)
    
    # --- H1, H2, H3 ---
    for termin, stavke in po_terminima.items():
        for i in range(len(stavke)):
            for j in range(i+1, len(stavke)):
                a, b = stavke[i], stavke[j]
                if a["nastavnik"] == b["nastavnik"]: d_h1 += 1
                if a["ucionica"]["id"] == b["ucionica"]["id"]: d_h2 += 1
                if any(g in b["grupe"] for g in a["grupe"]): d_h3 += 1
    
    # --- H4, H6 ---
    for (pid, tip), stavke in po_predmetima.items():
        n = len(stavke)
        setovi_grupa = [set(x["grupe"]) for x in stavke]
        max_kap = max_kap_lv if tip == "LV" else max_kap_nastava
        
        for i in range(n):
            a = stavke[i]
            set_a = setovi_grupa[i]
            for j in range(i + 1, n):
                b = stavke[j]
                set_b = setovi_grupa[j]
                
                if a["termin"] != b["termin"] and set_a != set_b: 
                    d_h4 += 1
                
                if a["termin"] != b["termin"] and set_a != set_b:
                    if a["broj_studenata"] + b["broj_studenata"] <= max_kap: 
                        d_h6 += 1
    
    # --- H7 ---
    for z in zaduzenja:
        ukupno = brojac_h7.get((z["predmet_id"], z["tip_nastave"]), 0)
        if z["tip_nastave"] == "LV":
            broj_grupa = ceil(z["broj_studenata"] / max_kap_lv) if max_kap_lv > 0 else 1
        else:
            broj_grupa = 1
            
        ocekivano = z["trajanje"] * broj_grupa
        if ukupno != ocekivano:
            d_h7 += 1
            print(f"H7: {z['predmet']} {z['tip_nastave']}: treba {z['trajanje'] * broj_grupa}, ima {ukupno}")
    print(f"H1:{d_h1} H2:{d_h2} H3:{d_h3} H4:{d_h4} H5:{d_h5} H6:{d_h6} H7:{d_h7} H8:{d_h8} H9:{d_h9}")