import itertools
DANI = ["Ponedjeljak", "Utorak", "Srijeda", "Četvrtak", "Petak"]
SLOTOVI = list(range(1, 13))  
TERMINI = list(itertools.product(DANI, SLOTOVI))
REDOVNO_ZAPOSLENI = ["Redovni profesor", "Redovna profesorica", "Vanredni profesor", "Vanredna profesorica", "Asistent",
                      "Viši asistent", "Viša asistentica", "Asistentica", "Docent", "Docentica"]

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