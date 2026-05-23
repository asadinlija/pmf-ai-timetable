import random
import math
import copy
from config import TERMINI
from generator import generisi_raspored
from evaluator import evaluiraj_raspored

def daj_susjedni_raspored(trenutni_raspored, ucionice):
    # Koristimo listu sa kopiranim rječnicima na ulazu da budemo 100% sigurni
    novi_raspored = [cas.copy() for cas in trenutni_raspored]
    
    indeks_prvog = random.randint(0, len(novi_raspored) - 1)
    cas1 = novi_raspored[indeks_prvog]
    
    cas1["termin"] = random.choice(TERMINI)
    
    # ... onaj tvoj standardni kod za filtriranje učionica ...
    if cas1["tip"] == "LV":
        dostupne = [u for u in ucionice.values() 
                if u["tip_ucionice"] == "racunarski_kabinet" 
                and u["kapacitet_lv_vjezbi"] >= cas1["broj_studenata"]]
        if not dostupne:
            dostupne = [u for u in ucionice.values() 
                    if u["tip_ucionice"] == "racunarski_kabinet"]
    else:
        dostupne = [u for u in ucionice.values() 
                if u["kapacitet_nastave"] >= cas1["broj_studenata"]]
        if not dostupne:
            dostupne = list(ucionice.values())
    cas1["ucionica"] = random.choice(dostupne)
        
    return novi_raspored


def pokreni_simulated_annealing(zaduzenja, ucionice, pocetna_temp=150.0, stop_temp=1.0, alfa=0.98, max_iter=300):
    trenutno_stanje = generisi_raspored(zaduzenja, ucionice)
    trenutna_kazna = evaluiraj_raspored(trenutno_stanje, zaduzenja, ucionice)
    
    najbolje_stanje = copy.deepcopy(trenutno_stanje)
    najbolja_kazna = trenutna_kazna
    
    T = pocetna_temp
    print(f"SA pokrenut. Početna kazna: {trenutna_kazna}")
    
    while T > stop_temp:
        for _ in range(max_iter):
            susjed = daj_susjedni_raspored(trenutno_stanje, ucionice)
            kazna_susjeda = evaluiraj_raspored(susjed, zaduzenja, ucionice)
            
            delta_e = kazna_susjeda - trenutna_kazna
            
            if delta_e < 0:
                trenutno_stanje = [cas.copy() for cas in susjed]
                trenutna_kazna = kazna_susjeda
                
                if trenutna_kazna < najbolja_kazna:
                    najbolje_stanje = copy.deepcopy(susjed)
                    najbolja_kazna = trenutna_kazna
            else:
                vjerovatnoca = math.exp(-delta_e / T)
                if random.random() < vjerovatnoca:
                    trenutno_stanje = [cas.copy() for cas in susjed]
                    trenutna_kazna = kazna_susjeda
                    
        print(f"Temperatura: {T:.2f} | Trenutna kazna: {trenutna_kazna} | Najbolja kazna: {najbolja_kazna}")
        T = T * alfa
        
        if najbolja_kazna == 0:
            print("Pronađen savršen raspored bez ikakvih kazni!")
            break
            
    return najbolje_stanje, najbolja_kazna