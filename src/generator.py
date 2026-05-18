import random as rand
import parser_podataka
from config import TERMINI

def generisi_raspored(zaduzenja, ucionice):
    raspored = []
    for z in zaduzenja:
        termin = rand.choice(TERMINI)
        ucionica = rand.choice(ucionice)
        # nastavit ce se ...
    return raspored

