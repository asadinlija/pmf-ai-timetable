from parser_podataka import ucitaj_zaduzenja, ucitaj_ucionice, ucitaj_ogranicenja
from generator import generisi_raspored
from evaluator import evaluiraj_raspored

zaduzenja = ucitaj_zaduzenja("data/zaduzenja.xlsx", "data/predmeti.csv")
ucionice = ucitaj_ucionice("data/ucionice.csv")
zelje = ucitaj_ogranicenja("data/ogranicenja.csv")

raspored = generisi_raspored(zaduzenja, ucionice)
kazna = evaluiraj_raspored(raspored, zaduzenja, ucionice)
print(f"Pocetna kazna: {kazna}")
print(raspored)

