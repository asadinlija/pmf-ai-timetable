import random
import copy
from generator import generisi_raspored
from evaluator import evaluiraj_raspored
from .sa_algorithm import daj_susjedni_raspored

def pokreni_abc(zaduzenja, ucionice, broj_kolonije=20, limit=50, max_iteracija=500):
    
    kolonija = []
    historija = []
    for _ in range(broj_kolonije):
        raspored = generisi_raspored(zaduzenja, ucionice)
        kazna = evaluiraj_raspored(raspored, zaduzenja, ucionice)
        kolonija.append({
            "raspored": raspored,
            "kazna": kazna,
            "brojac": 0
        })
    najbolje = min(kolonija, key=lambda x: x["kazna"])
    najbolji_raspored = copy.deepcopy(najbolje["raspored"])
    najbolja_kazna = najbolje["kazna"]
    
    brojac_stagnacije = 0
    prethodna_najbolja = najbolja_kazna
    for i in range(max_iteracija):
        
        # employed bees
        for pcela in kolonija:
            novi_raspored = daj_susjedni_raspored(pcela["raspored"], ucionice)
            nova_kazna = evaluiraj_raspored(novi_raspored, zaduzenja, ucionice)
            if nova_kazna < pcela["kazna"]:
                pcela["raspored"] = novi_raspored
                pcela["kazna"] = nova_kazna
                pcela["brojac"] = 0
            else:
                pcela["brojac"] += 1

        # onlooker bees faza  
        fitness_vrijednosti = [1.0 / (pcela["kazna"] + 1.0) for pcela in kolonija]
        ukupni_fitness = sum(fitness_vrijednosti)
        vjerovatnoce = [f / ukupni_fitness for f in fitness_vrijednosti]

        for _ in range(broj_kolonije):
            # element biramo proporcionalno tezinama
            # veca tezina, veca sansa da bude odabran
            odabrana = random.choices(kolonija, weights=vjerovatnoce, k=1)[0]
            raspored_susjeda_odabrane = daj_susjedni_raspored(odabrana["raspored"], ucionice)
            kazna_susjeda_odabrane = evaluiraj_raspored(raspored_susjeda_odabrane, zaduzenja, ucionice)

            if kazna_susjeda_odabrane < odabrana["kazna"]:
                odabrana["raspored"] = raspored_susjeda_odabrane
                odabrana["kazna"] = kazna_susjeda_odabrane
                odabrana["brojac"] = 0
            else:
                odabrana["brojac"] += 1
        # scout bees faza
        for pcela in kolonija:
            if pcela["brojac"] > limit:
                pcela["raspored"] = generisi_raspored(zaduzenja, ucionice)
                pcela["kazna"] = evaluiraj_raspored(pcela["raspored"], zaduzenja, ucionice)
                pcela["brojac"] = 0
        
        # azuriramo najbolje rjesenje
        trenutno_najbolje = min(kolonija, key=lambda x: x["kazna"])
        if trenutno_najbolje["kazna"] < najbolja_kazna:
            najbolja_kazna = trenutno_najbolje["kazna"]
            najbolji_raspored = copy.deepcopy(trenutno_najbolje["raspored"])
        historija.append(najbolja_kazna)
        if i % 50 == 0:
            print(f"Iteracija {i} | Najbolja kazna: {najbolja_kazna}")
        
    
    return najbolji_raspored, najbolja_kazna, historija