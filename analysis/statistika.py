import json
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

try:
    with open('data/rezultati.json', 'r') as f:
        podaci = json.load(f)
except FileNotFoundError:
    print("Greska: Fajl 'rezultati.json' nije pronadjen u ovom direktoriju!")
    exit()

def daj_statistiku(fitness_niz, vrijeme_niz, ime_algoritma):
    return {
        "Algoritam": ime_algoritma,
        "Min Kazna": np.min(fitness_niz),
        "Max Kazna": np.max(fitness_niz),
        "Mean Kazna": np.mean(fitness_niz),
        "Median Kazna": np.median(fitness_niz),
        "Std Kazna": np.std(fitness_niz),
        "Mean Vrijeme (s)": np.mean(vrijeme_niz),
        "Std Vrijeme (s)": np.std(vrijeme_niz)
    }

def cliffs_delta(x, y):
    lx, ly = len(x), len(y)
    count = 0
    for i in x:
        for j in y:
            if i > j: count += 1
            elif i < j: count -= 1
    return count / (lx * ly)

def analiziraj_semestar(ime_semestra, kljuc_sa, kljuc_abc):
    print(f"\n**********************************************")
    print(f"       ANALIZA ZA: {ime_semestra.upper()} SEMESTAR")
    print(f"************************************************")
    
    # Izvlacenje nizova iz JSON strukture
    sa_fitness = [run['kazna'] for run in podaci[kljuc_sa]]
    sa_vrijeme = [run['trajanje'] for run in podaci[kljuc_sa]]
    
    abc_fitness = [run['kazna'] for run in podaci[kljuc_abc]]
    abc_vrijeme = [run['trajanje'] for run in podaci[kljuc_abc]]
    
    # deskriptivna statistika
    df_stat = pd.DataFrame([
        daj_statistiku(sa_fitness, sa_vrijeme, "Simulirano Kaljenje (SA)"),
        daj_statistiku(abc_fitness, abc_vrijeme, "Artificial Bee Colony (ABC)")
    ])
    print("\nDeskriptivna statistika:")
    print(df_stat.to_string(index=False))
    
    # test normalnosti Shapiro-Wilk
    _, p_shapiro1 = stats.shapiro(sa_fitness)
    _, p_shapiro2 = stats.shapiro(abc_fitness)
    print(f"\nShapiro-Wilk test normalnosti (p-vrijednost):")
    print(f"    - SA  (Kazna): {p_shapiro1:.4f}")
    print(f"    - ABC (Kazna): {p_shapiro2:.4f}")
    
    normalni = p_shapiro1 > 0.05 and p_shapiro2 > 0.05
    
    # statisticki test znacajnosti
    if normalni:
        stat, p_test = stats.ttest_rel(sa_fitness, abc_fitness)
        test_ime = "Parni t-test (Parametarski)"
    else:
        stat, p_test = stats.wilcoxon(sa_fitness, abc_fitness)
        test_ime = "Wilcoxon signed-rank test (Neparametarski)"
        
    print(f"\n Izabrani test znacajnosti: {test_ime}")
    print(f"    - p-vrijednost testa: {p_test:.5e}")
    if p_test < 0.05:
        print("    - Zakljucak: Razlika JE statisticki znacajna (p < 0.05).")
    else:
        print("    - Zakljucak: Razlika NIJE statisticki znacajna (p >= 0.05).")
        
    cd = cliffs_delta(sa_fitness, abc_fitness)
    print(f"\n[4] Cliff's delta effect size: {cd:.4f}")
    
    # plotovanje box-plota
    plt.figure(figsize=(6, 5))
    sns.boxplot(data=[sa_fitness, abc_fitness], palette="Set2")
    plt.xticks([0, 1], ['Simulirano Kaljenje (SA)', 'Artificial Bee Colony (ABC)'])
    
    # logaritamska skala jer su vrijednosti SA i ABC u potpuno razlicitim redovima velicine
    plt.yscale('log') 
    
    plt.ylabel('Kazna / Penali (Logaritamska skala)')
    plt.title(f'Distribucija zavrsnih kazni - {ime_semestra} semestar')
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    # Automatsko spasavanje slike u fajl sa jasnim nazivom
    ime_slike = f'analysis/plots/box_plot_fitness_{ime_semestra.lower()}.png'
    plt.savefig(ime_slike, dpi=300)
    plt.close()
    print(f"\nGrafik uspjesno sacuvan kao: '{ime_slike}'\n")

# pokretanje analize za oba semestra
analiziraj_semestar("Zimski", "sa_zimski", "abc_zimski")
analiziraj_semestar("Ljetni", "sa_ljetni", "abc_ljetni")