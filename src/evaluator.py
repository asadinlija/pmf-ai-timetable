from config import HARD_PENAL, REDOVNO_ZAPOSLENI, TEZINE

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
            # ili isti termin razlicite ucionice, uglavnom nastale su grupe
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





