from config import HARD_PENAL, REDOVNO_ZAPOSLENI, TEZINE, DANI

def provjeri_konflikt(raspored, polje):
    kazna = 0
    for i in range(len(raspored)):
        for j in range(i+1, len(raspored)):
            a = raspored[i]
            b = raspored[j]

            if polje == "ucionica":
                vrijednost_a = a["ucionica"]["id"]
                vrijednost_b = b["ucionica"]["id"]
            else:
                vrijednost_a = a[polje]
                vrijednost_b = b[polje]

            if a[polje] == b[polje] and a["termin"] == b["termin"]:
                kazna += HARD_PENAL
    return kazna

def provjeri_h1(raspored):
    return provjeri_konflikt(raspored, "nastavnik")
def provjeri_h2(raspored):
    return provjeri_konflikt(raspored, "ucionica")

def provjeri_h3(raspored):
    kazna = 0
    for i in range(len(raspored)):
        for j in range(i+1, len(raspored)):
            a = raspored[i]
            b = raspored[j]
            if (set(a["grupe"]) & set(b["grupe"])) and a["termin"] == b["termin"]:
                kazna += HARD_PENAL
    return kazna

def provjeri_h4(raspored, max_kapacitet_ucionice):
    kazna = 0
    for i in range(len(raspored)):
        for j in range(i+1, len(raspored)):
            a = raspored[i]
            b = raspored[j]
            if(
                a["predmet_id"] == b["predmet_id"]
                and a["tip"] == b["tip"]
                and a["termin"] != b["termin"]
                and set(a["grupe"]) != set(b["grupe"])
            ):
                kazna += HARD_PENAL
    return kazna

def provjeri_h5(raspored, ucionice):
    kazna = 0
    for i in range(len(raspored)):
        a = raspored[i]
        if a["tip"] == "LV":
            if a["ucionica"]["kapacitet_lv_vjezbi"] < a["broj_studenata"]:
                kazna += HARD_PENAL
        else:
            if a["ucionica"]["kapacitet_nastave"] < a["broj_studenata"]:
                kazna += HARD_PENAL
    return kazna

def provjeri_h6(raspored, max_kapacitet_nastava, max_kapacitet_lv):
    kazna = 0
    for i in range(len(raspored)):
        for j in range(i+1, len(raspored)):
            a = raspored[i]
            b = raspored[j]
            # provjera: nastala je grupa, a nije bilo potrebe
            # moze bit da su u razlicitim terminima, ista ucionica
            # ili isti termin razlicite ucionice...uglavnom nastale su grupe
            if(
                a["predmet_id"] == b["predmet_id"]
                and a["tip"] == b["tip"]
                and not (a["termin"] == b["termin"] and a["ucionica"]["id"] == b["ucionica"]["id"])
            ):
                if a["tip"] == "LV":
                    max_kap = max_kapacitet_lv
                else:
                    max_kap = max_kapacitet_nastava
                if a["broj_studenata"] + b["broj_studenata"] <= max_kap:
                    kazna += HARD_PENAL     
    return kazna

def provjeri_h7(raspored, zaduzenja):
    kazna = 0 
    brojac = {}
    for d in raspored:
        kljuc = (d["predmet_id"], d["tip"])
        if kljuc not in brojac:
            brojac[kljuc] = 0
        brojac[kljuc] += 1
    for z in zaduzenja:
        kljuc = (z["predmet_id"], z["tip_nastave"])
        stvarni_broj = brojac.get(kljuc, 0)
        if stvarni_broj != z["trajanje"]:
            kazna += HARD_PENAL
    return kazna

def provjeri_h8(raspored):
    kazna = 0
    for d in raspored:
        if d["tip"] == "LV" and d["ucionica"]["tip_ucionice"] != "racunarski_kabinet":
            kazna += HARD_PENAL
    return kazna

def provjeri_h9(raspored):
    kazna = 0
    for d in raspored:
        if d["termin"] == ("Četvrtak", 6):
            if any(r.lower() in d["zvanje_nastavnika"].lower() for r in REDOVNO_ZAPOSLENI):
                kazna += HARD_PENAL
    return kazna

def provjeri_s1(raspored):
    kazna = 0
    raspored_grupe = {}
    for d in raspored:
        dan = d["termin"][0]
        slot = d["termin"][1]
        
        for grupa in d["grupe"]:
            kljuc = (grupa, dan)
            if kljuc not in raspored_grupe:
                raspored_grupe[kljuc] = set()  
            raspored_grupe[kljuc].add(slot)

    for kljuc, jedinstveni_slotovi in raspored_grupe.items():
        slotovi = sorted(list(jedinstveni_slotovi))
        for i in range(len(slotovi) - 1):
            razlika = slotovi[i+1] - slotovi[i]
            if razlika > 1:
                broj_praznih_sati = razlika - 1
                kazna += broj_praznih_sati * TEZINE["S1"]
    return kazna

def provjeri_s2(raspored):
    kazna = 0
    raspored_grupe = {}
    for d in raspored:
        dan = d["termin"][0]
        slot = d["termin"][1]

        for grupa in d["grupe"]:
            kljuc = (grupa, dan)
            if kljuc not in raspored_grupe:
                raspored_grupe[kljuc] = set()
            raspored_grupe[kljuc].add(slot)
    for kljuc, jedinstveni_slotovi in raspored_grupe.items():
        slotovi = sorted(list(jedinstveni_slotovi))
        if not slotovi:
            continue
        trenutna_duzina_niza = 1
        for i in range(len(slotovi)-1):
            if slotovi[i+1] - slotovi[i] == 1:
                trenutna_duzina_niza += 1
            else:
                if trenutna_duzina_niza > 5:
                    prekoracenje = trenutna_duzina_niza - 5
                    kazna += prekoracenje * TEZINE["S2"]
                trenutna_duzina_niza = 1
        # provjera za zadnji niz      
        if trenutna_duzina_niza > 5:
            prekoracenje = trenutna_duzina_niza - 5
            kazna += prekoracenje * TEZINE["S2"]
    return kazna

def provjeri_s3(raspored):
    kazna = 0
    opterecenje_grupa = {}
    for d in raspored:
        dan = d["termin"][0]
        for grupa in d["grupe"]:
            if grupa not in opterecenje_grupa:
                opterecenje_grupa[grupa] = {dan: 0 for dan in DANI}
            if dan in opterecenje_grupa[grupa]:
                opterecenje_grupa[grupa][dan] += 1
    for grupa, dani_r in opterecenje_grupa.items():
        ukupan_fond = sum(dani_r.values())
        idealno = ukupan_fond / 5.0
        for dan in DANI:
            stvarno_sati = dani_r[dan]
            odstupanje = abs(stvarno_sati - idealno)
            kazna += odstupanje * TEZINE["S3"]
    return kazna

def provjeri_s4(raspored):
    kazna = 0
    raspored_master_studenti = {}
    GRANICA_POPODNE = 7
    for d in raspored:
        slot = d["termin"][1]
        je_master = False
        for (smjer, godina) in d["grupe"]:
            if godina >= 4:
                je_master = True
                break
        if je_master and slot < GRANICA_POPODNE:
            kazna += TEZINE["S4"]
    return kazna
    
def termin_u_broj(termin):
    dan_index = DANI.index(termin[0])
    # imamo 12 slotova u jednom danu pa na ovaj nacin svaki termin u svakom danu dobije jedinstven broj
    return dan_index*12 + termin[1]
 
def provjeri_s5(raspored):
    kazna = 0
    termini_po_predmetu = {}
    for d in raspored:
        pid = d["predmet_id"]
        for grupa in d["grupe"]:
            kljuc = (grupa, pid)
            if pid not in termini_po_predmetu:
                termini_po_predmetu[kljuc] = {"P": [], "AV": [], "LV": []}
            termini_po_predmetu[kljuc][d["tip"]].append(d["termin"])
    for kljuc, tipovi in termini_po_predmetu.items():
        for p_termin in tipovi["P"]:
            for v_termin in tipovi["AV"] + tipovi["LV"]:
                if termin_u_broj(p_termin) > termin_u_broj(v_termin):
                    kazna += TEZINE["S5"]
    return kazna

def provjeri_redovno_zaposlenje(nastavnik):
    return any(r.lower() in nastavnik.lower() for r in REDOVNO_ZAPOSLENI)

def provjeri_s6(raspored):
    kazna = 0
    raspored_nastavnici = {}
    for d in raspored:
        # ako je redovan nastavnik onda kaznjavamo
        # ako je naprimjer strucni saradnik, oni obicno rade negdje
        # pa mogu doci naprimjer od 8 do 10 nesto da odrze pa 16h do 18h naprimjer
        # jer njima to zbog posla vise odgovara, pa nema potrebe da tada kaznjavamo 
        if not provjeri_redovno_zaposlenje(d["nastavnik"]):
            continue
        dan = d["termin"][0]
        slot = d["termin"][1]
        kljuc = (d["nastavnik"], dan)
        if kljuc not in raspored_nastavnici:
            raspored_nastavnici[kljuc] = set()
        raspored_nastavnici[kljuc].add(slot)
    for kljuc, jedinstveni_slotovi in raspored_nastavnici.items():
        slotovi = sorted(list(jedinstveni_slotovi))
        for i in range(len(slotovi)-1):
            razlika = slotovi[i+1] - slotovi[i]
            if razlika > 1:
                broj_praznih_sati = razlika - 1
                kazna += broj_praznih_sati * TEZINE["S6"]
    return kazna

def provjeri_s7(raspored):
    kazna = 0
    RANIJI_SLOTOVI = [1, 2, 3, 4, 5, 6, 7, 8]
    raspored_saradnici = {}
    for d in raspored:
        slot = d["termin"][1]
        if provjeri_redovno_zaposlenje(d["nastavnik"]):
            continue
        if slot in RANIJI_SLOTOVI:
            kazna += TEZINE["S7"]
    return kazna

def provjeri_s8(raspored):
    kazna = 0
    for d in raspored:
        predmet = d["predmet"]
        if predmet == "Programiranje I" and d["tip"] == "LV":
            if d["ucionica"]["id"] != "A1":
                kazna += TEZINE["S8"]
    return kazna
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
    radni_dani = len([d for d, s in dani_profesora.items() if len(s) > 0])
    if radni_dani > max_dana:
        return (radni_dani - max_dana) 
    return 0

def procijeni_rad_u_bloku(dani_profesora):
    prekrsaji = 0
    for dan, jedinstveni_slotovi in dani_profesora.items():
        if not jedinstveni_slotovi:
            continue
        slotovi = sorted(list(jedinstveni_slotovi))
        for i in range(len(slotovi)-1):
            razlika = slotovi[i+1] -  slotovi[i]
            if razlika > 1:
                prekrsaji += (razlika - 1)
    return prekrsaji

def provjeri_s9(raspored):
    kazna = 0
    raspored_profesora = {}
    casovi_profesora = {}

    for d in raspored:
        prof = d["nastavnik"]
        dan = d["termin"][0]
        slot = d["termin"][1]

        if prof not in raspored_profesora:
            raspored_profesora[prof] = {dan: set() for dan in DANI}
            casovi_profesora[prof] = []
        if dan in DANI:
            raspored_profesora[prof][dan].add(slot)
            casovi_profesora[prof].append(d)
    for prof, dani in raspored_profesora.items():
        prekrsaji = 0

        if prof == "Senada Kalabusic":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Utorak", "Srijeda"], max_slot=4)
        elif prof == "Amela Muratovic-Ribic":
            prekrsaji += procijeni_dane_i_sate(dani, dozvoljeni_dani=["Ponedjeljak", "Utorak", "Srijeda"])
            








