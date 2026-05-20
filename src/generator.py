import random as rand
import parser_podataka
from config import TERMINI

def generisi_raspored(zaduzenja, ucionice):
    raspored = []
    for z in zaduzenja:
        termin = rand.choice(TERMINI)
        if z["tip_nastave"] == "LV":
            dostupne = [u for u in list(ucionice.values()) if u["tip_ucionice"] == "racunarski_kabinet"]
        else:
            dostupne = list(ucionice.values())
        ucionica = rand.choice(dostupne)
        raspored.append({
            "predmet_id": z["predmet_id"],
            "predmet": z["predmet"],
            "tip": z["tip_nastave"],
            "nastavnik": z["nastavnik"],
            "zvanje_nastavnika": z["zvanje"],
            "termin": termin,
            "ucionica": ucionica,
            "grupe": z["smjerovi"],
            "broj_studenata": z["broj_studenata"],
            "trajanje": z["trajanje"]

        })
    return raspored

