from config import HARD_PENAL

def provjeri_konflikt(raspored, polje):
    kazna = 0
    for i in range(len(raspored)):
        for j in range(i+1, len(raspored)):
            a = raspored[i]
            b = raspored[j]
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

