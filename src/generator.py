import random as rand
import parser_podataka
from config import TERMINI
from math import ceil

def generisi_raspored(zaduzenja, ucionice):
    raspored = []
    grupirano = {}
    
    for z in zaduzenja:
        kljuc = (z["predmet_id"], z["tip_nastave"])
        if kljuc not in grupirano:
            grupirano[kljuc] = z 
            
    for kljuc, z in grupirano.items():
        if z["tip_nastave"] == "LV":
            dostupne = [u for u in ucionice.values() if u["tip_ucionice"] == "racunarski_kabinet"]
            if dostupne:
                max_kap_lv = max(u["kapacitet_lv_vjezbi"] for u in dostupne)
                broj_grupa = ceil(z["broj_studenata"] / max_kap_lv) if max_kap_lv > 0 else 1
                # koristimo ceil da osiguramo da kapacitet nigdje ne pukne
                studenti_po_grupi = ceil(z["broj_studenata"] / broj_grupa)
            else:
                broj_grupa = 1
                studenti_po_grupi = z["broj_studenata"]
                dostupne = list(ucionice.values())
        else:
            broj_grupa = 1
            studenti_po_grupi = z["broj_studenata"]
            dostupne = list(ucionice.values())

        # prvo vrtimo grupe
        for g in range(broj_grupa):
            # Svaka grupa dobija svoje slotove u zavisnosti od trajanja predmeta
            for _ in range(z["trajanje"]):
                termin = rand.choice(TERMINI)
                ucionica = rand.choice(dostupne)
                
                raspored.append({
                    # Dodajemo oznaku grupe u ID da evaluator broji fond za svaku grupu posebno
                    "predmet_id": f"{z['predmet_id']}_G{g+1}" if broj_grupa > 1 else z["predmet_id"],
                    "predmet_id_orig": z["predmet_id"],
                    "predmet": f"{z['predmet']} - G{g+1}" if broj_grupa > 1 else z["predmet"],
                    "tip": z["tip_nastave"],
                    "nastavnik": z["nastavnik"],
                    "zvanje_nastavnika": z["zvanje"],
                    "termin": termin,
                    "ucionica": ucionica,
                    "grupe": z["smjerovi"],
                    "broj_studenata": studenti_po_grupi,
                    "trajanje": z["trajanje"] 
                })
                
    return raspored