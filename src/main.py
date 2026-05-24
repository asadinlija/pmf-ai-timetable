from parser_podataka import ucitaj_zaduzenja, ucitaj_ucionice, ucitaj_ogranicenja
from generator import generisi_raspored
from evaluator import evaluiraj_raspored, debug_hard
from algorithms.sa_algorithm import pokreni_simulated_annealing
from algorithms.abc_algorithm import pokreni_abc
from config import HARD_PENAL

zaduzenja = ucitaj_zaduzenja("data/zaduzenja.xlsx", "data/predmeti.csv")

zimski = ["I", "III", "V"]
ljetni = ["II", "IV", "VI"]

zaduzenja_zimski = [z for z in zaduzenja if str(z["semestar"]).strip() in zimski]
zaduzenja_ljetni = [z for z in zaduzenja if str(z["semestar"]).strip() in ljetni]

ucionice = ucitaj_ucionice("data/ucionice.csv")
zelje = ucitaj_ogranicenja("data/ogranicenja.csv")

raspored_zimski = generisi_raspored(zaduzenja_zimski, ucionice)
kazna_zimski = evaluiraj_raspored(raspored_zimski, zaduzenja_zimski, ucionice)
print(f"Pocetna kazna: {kazna_zimski}")


raspored_ljetni = generisi_raspored(zaduzenja_ljetni, ucionice)
kazna_ljetni = evaluiraj_raspored(raspored_ljetni, zaduzenja_ljetni, ucionice)
print(f"Pocetna kazna: {kazna_ljetni}")

najbolji_raspored, finalna_kazna_ljetni = pokreni_abc(
    zaduzenja_ljetni, 
    ucionice,
    broj_kolonije=20,
    limit = 50,
    max_iteracija=700
)

#print(raspored)
'''
najbolji_raspored_zimski, finalna_kazna_zimski = pokreni_simulated_annealing(
    zaduzenja_zimski, 
    ucionice,
    pocetna_temp=1000000,
    stop_temp= 100,
    alfa=0.98,
    max_iter = 300
)
najbolji_raspored_ljetni, finalna_kazna_ljetni = pokreni_simulated_annealing(
    zaduzenja_ljetni, 
    ucionice,
    pocetna_temp=1000000,
    stop_temp= 100,
    alfa=0.98,
    max_iter = 300
)

print(f"\nOptimizacija završena! Finalna kazna rasporeda je: {finalna_kazna_zimski}")
print(f"\nOptimizacija završena! Finalna kazna rasporeda je: {finalna_kazna_ljetni}")

hard_krsenja_zimski = int(finalna_kazna_zimski // HARD_PENAL)
soft_kazna_zimski = finalna_kazna_zimski % HARD_PENAL
print(f"Hard kršenja: {hard_krsenja_zimski}")
print(f"Soft kazna: {soft_kazna_zimski:.0f}")
debug_hard(najbolji_raspored_zimski, zaduzenja_zimski, ucionice)

hard_krsenja_ljetni = int(finalna_kazna_ljetni // HARD_PENAL)
soft_kazna_ljetni = finalna_kazna_ljetni % HARD_PENAL
print(f"Hard kršenja: {hard_krsenja_ljetni}")
print(f"Soft kazna: {soft_kazna_ljetni:.0f}")
debug_hard(najbolji_raspored_ljetni, zaduzenja_ljetni, ucionice)

'''