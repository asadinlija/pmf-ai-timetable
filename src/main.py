from parser_podataka import ucitaj_zaduzenja, ucitaj_ucionice, ucitaj_ogranicenja
from generator import generisi_raspored
from evaluator import evaluiraj_raspored
from algorithms.sa_algorithm import pokreni_simulated_annealing
from algorithms.abc_algorithm import pokreni_abc
from config import HARD_PENAL
from pdf_generator import generisi_sve_rasporede

zaduzenja = ucitaj_zaduzenja("data/zaduzenja.xlsx", "data/predmeti.csv")

zimski = ["I", "III", "V"]
ljetni = ["II", "IV", "VI"]

zaduzenja_zimski = [z for z in zaduzenja if str(z["semestar"]).strip() in zimski]
zaduzenja_ljetni = [z for z in zaduzenja if str(z["semestar"]).strip() in ljetni]

ucionice = ucitaj_ucionice("data/ucionice.csv")
zelje = ucitaj_ogranicenja("data/ogranicenja.csv")


najbolji_raspored_zimski_sa, finalna_kazna_zimski_sa, _ = pokreni_simulated_annealing(
    zaduzenja_zimski, 
    ucionice,
    pocetna_temp=100000,
    stop_temp= 1000,
    alfa=0.95,
    max_iter = 150
)

najbolji_raspored_ljetni_sa, finalna_kazna_ljetni_sa, _ = pokreni_simulated_annealing(
    zaduzenja_ljetni, 
    ucionice,
    pocetna_temp=100000,
    stop_temp= 1000,
    alfa=0.95,
    max_iter = 150
)
najbolji_raspored_zimski_abc, finalna_kazna_zimski_abc, _ = pokreni_abc(
    zaduzenja_zimski, 
    ucionice,
    broj_kolonije=20,
    limit = 50,
    max_iteracija=700
)

najbolji_raspored_ljetni_abc, finalna_kazna_ljetni_abc, _ = pokreni_abc(
    zaduzenja_ljetni, 
    ucionice,
    broj_kolonije=20,
    limit = 50,
    max_iteracija=700
)
generisi_sve_rasporede(najbolji_raspored_zimski_sa, "zimski", "output/zimski_sa")
generisi_sve_rasporede(najbolji_raspored_ljetni_sa,"ljetni","output/ljetni_sa")

generisi_sve_rasporede(najbolji_raspored_zimski_abc, "zimski", "output/zimski_abc")
generisi_sve_rasporede(najbolji_raspored_ljetni_abc, "ljetni", "output/ljetni_abc")

