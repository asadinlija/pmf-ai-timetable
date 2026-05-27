import json
import time
import sys, os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

sys.path.append(os.path.join(ROOT_DIR, 'src'))

from src.parser_podataka import ucitaj_zaduzenja, ucitaj_ucionice
from src.algorithms.sa_algorithm import pokreni_simulated_annealing
from src.algorithms.abc_algorithm import pokreni_abc


zaduzenja = ucitaj_zaduzenja("data/zaduzenja.xlsx", "data/predmeti.csv")
ucionice = ucitaj_ucionice("data/ucionice.csv")

zimski = ["I", "III", "V"]
zaduzenja_zimski = [z for z in zaduzenja if str(z["semestar"]).strip() in zimski]

ljetni = ["II", "IV", "VI"]
zaduzenja_ljetni = [z for z in zaduzenja if str(z["semestar"]).strip() in ljetni]

rezultati_sa_zimski = []
rezultati_abc_zimski = []
rezultati_sa_ljetni = []
rezultati_abc_ljetni = []

sve_historije_sa_zimski = []
sve_historije_abc_zimski = []
sve_historije_sa_ljetni = []
sve_historije_abc_ljetni = []


for i in range(30):
    print(f"SA zimski pokretanje {i+1}/30")
    pocetak = time.time()
    _, kazna, historija_sa_zimski = pokreni_simulated_annealing(
        zaduzenja_zimski, ucionice,
        pocetna_temp=100_000,
        stop_temp=1000,
        alfa=0.95,
        max_iter=150
    )
    sve_historije_sa_zimski.append(historija_sa_zimski)
    trajanje = time.time() - pocetak
    rezultati_sa_zimski.append({"kazna": float(kazna), "trajanje": trajanje})
    print(f"  Kazna: {kazna:.0f}, Trajanje: {trajanje:.1f}s")

for i in range(30):
    print(f"ABC zimski pokretanje {i+1}/30")
    pocetak = time.time()
    _, kazna, historija_abc_zimski = pokreni_abc(
        zaduzenja_zimski, ucionice,
        broj_kolonije=20,
        limit=50,
        max_iteracija=500
    )
    sve_historije_abc_zimski.append(historija_abc_zimski)
    trajanje = time.time() - pocetak
    rezultati_abc_zimski.append({"kazna": float(kazna), "trajanje": trajanje})
    print(f"  Kazna: {kazna:.0f}, Trajanje: {trajanje:.1f}s")


for i in range(30):
    print(f"SA ljetni pokretanje {i+1}/30")
    pocetak = time.time()
    _, kazna, historija_sa_ljetni= pokreni_simulated_annealing(
        zaduzenja_ljetni, ucionice,
        pocetna_temp=100_000,
        stop_temp=1000,
        alfa=0.95,
        max_iter=150
    )
    sve_historije_sa_ljetni.append(historija_sa_ljetni)
    trajanje = time.time() - pocetak
    rezultati_sa_ljetni.append({"kazna": float(kazna), "trajanje": trajanje})
    print(f"  Kazna: {kazna:.0f}, Trajanje: {trajanje:.1f}s")  

for i in range(30):
    print(f"ABC ljetni pokretanje {i+1}/30")
    pocetak = time.time()
    _, kazna, historija_abc_ljetni = pokreni_abc(
        zaduzenja_ljetni, ucionice,
        broj_kolonije=20,
        limit=50,
        max_iteracija=500
    )
    sve_historije_abc_ljetni.append(historija_abc_ljetni)
    trajanje = time.time() - pocetak
    rezultati_abc_ljetni.append({"kazna": float(kazna), "trajanje": trajanje})
    print(f"  Kazna: {kazna:.0f}, Trajanje: {trajanje:.1f}s")

with open("data/rezultati.json", "w") as f:
    json.dump({
        "sa_zimski": rezultati_sa_zimski,
        "abc_zimski": rezultati_abc_zimski,
        "sa_ljetni": rezultati_sa_ljetni,
        "abc_ljetni": rezultati_abc_ljetni
    }, f, indent=2)

print(f"Gotovo! Rezultati snimljeni u data/rezultati.json")