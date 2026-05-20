import itertools
DANI = ["Ponedjeljak", "Utorak", "Srijeda", "Četvrtak", "Petak"]
SLOTOVI = list(range(1, 13))  
TERMINI = list(itertools.product(DANI, SLOTOVI))
REDOVNO_ZAPOSLENI = ["Redovni profesor", "Vanredni profesor", "Asistent", "Viši asistent", "Docent"]

HARD_PENAL = 1000000
TEZINE = {
    "S1": 100,
    "S2": 90,
    "S3": 80,
    "S4": 70,
    "S5": 60,
    "S8": 50,
    "S7": 40,
    "S6": 20,
    "S9": 10
}