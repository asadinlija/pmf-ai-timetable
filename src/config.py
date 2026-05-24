import itertools
DANI = ["Ponedjeljak", "Utorak", "Srijeda", "Četvrtak", "Petak"]
SLOTOVI = list(range(1, 13))  
TERMINI = list(itertools.product(DANI, SLOTOVI))
REDOVNO_ZAPOSLENI = ["Redovni profesor", "Redovna profesorica", "Vanredni profesor", "Vanredna profesorica", "Asistent",
                      "Viši asistent", "Viša asistentica", "Asistentica", "Docent", "Docentica"]
# dodala za ispis pdf rasporeda
SLOT_VREMENA = {               
    1:  "08:00 - 09:00",
    2:  "09:00 - 10:00",
    3:  "10:00 - 11:00",
    4:  "11:00 - 12:00",
    5:  "12:00 - 13:00",
    6:  "13:00 - 14:00",
    7:  "14:00 - 15:00",
    8:  "15:00 - 16:00",
    9:  "16:00 - 17:00",
    10: "17:00 - 18:00",
    11: "18:00 - 19:00",
    12: "19:00 - 20:00",
}

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