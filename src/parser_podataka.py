import pandas as pd
import re


def ocisti_naziv_predmeta(naziv):
    naziv = str(naziv).strip()
    
    naziv = re.sub(r'\s*\([^)]+\)\s*$', '', naziv)
    
    return naziv.strip().lower()


def parsiraj_fond(fond):
    if pd.isna(fond):
        return 0, 0,0
    
    if isinstance(fond, (int, float)):
        return int(fond), 0, 0

    fond = str(fond).strip().lower()

    if fond in ["nan", "", "fond časova", "fond"]:
        return 0, 0,0

    if "+" in fond:
        try:
            dijelovi = [int(float(x.strip())) for x in fond.split("+") if x.strip()]
            p  = dijelovi[0] if len(dijelovi) > 0 else 0
            av = dijelovi[1] if len(dijelovi) > 1 else 0
            lv = dijelovi[2] if len(dijelovi) > 2 else 0
            return p, av, lv
        except (ValueError, TypeError):
            return 0, 0, 0

    try:
        # Prvo u float pa u int, za slucaj da je string "3.0"
        return int(float(fond)), 0, 0
    except (ValueError, TypeError):
        return 0, 0, 0


def odredi_tipove_nastave(zvanje, fond_p, fond_av, fond_lv):
    zvanje = str(zvanje).lower()

    asistenti = ["asistent", "viši asistent", "v.asist", "asist", "stručni saradnik", "saradnik", "viši stručni saradnik"]
    je_asistent = any(a in zvanje for a in asistenti)

    aktivnosti = []

    if fond_p > 0:
        tip = "AV" if je_asistent else "P"
        aktivnosti.append({"tip": tip, "trajanje": fond_p})
    if fond_av > 0:
        aktivnosti.append({"tip": "AV", "trajanje": fond_av})
    if fond_lv > 0:
        aktivnosti.append({"tip": "LV", "trajanje": fond_lv})

    return aktivnosti


def ucitaj_aktivne_predmete(putanja_csv):
    
    df = pd.read_csv(putanja_csv)

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["broj_studenata"] = pd.to_numeric(df["broj_studenata"], errors="coerce").fillna(0)
    
    # Izbacujemo redove gdje nemamo validan ID predmeta
    df = df.dropna(subset=["id"])

    df["predmet"] = df["predmet"].astype(str).str.strip()
    df["smjer"] = df["smjer"].astype(str).str.strip()

    agregirano = {}

    for _, r in df.iterrows():
        pid = int(r["id"])
        naziv = r["predmet"]
        smjer = r["smjer"]
        broj = int(r["broj_studenata"])
        godina = int(r["godina"])
        if pid not in agregirano:
            agregirano[pid] = {
                "id": pid,
                "glavni_naziv": naziv,
                "smjerovi": {(smjer, godina)},
                "ukupno": broj,
                "nazivi": {naziv.lower()}
            }
        else:
            agregirano[pid]["ukupno"] += broj
            agregirano[pid]["smjerovi"].add((smjer, godina))
            agregirano[pid]["nazivi"].add(naziv.lower())

    lookup = {}
    for pid, p in agregirano.items():
        for n in p["nazivi"]:
            lookup[n] = {
                "id": pid,
                "naziv": p["glavni_naziv"],
                "smjerovi": list(p["smjerovi"]),
                "ukupno_studenata": p["ukupno"]
            }

    return lookup

def ucitaj_zaduzenja(putanja_excel, putanja_csv):
    predmeti = ucitaj_aktivne_predmete(putanja_csv)

    df = pd.read_excel(putanja_excel, header=None)

    df[1] = df[1].ffill()
    df[3] = df[3].ffill()
    df[4] = df[4].ffill()

    zaduzenja = []
    seen = set()

    for _, r in df.iterrows():
        if pd.isna(r[5]):
            continue

        predmet = str(r[5]).strip()
        if "ZADUŽENJA" in predmet or predmet == "Predmet":
            continue

        predmet_lower = ocisti_naziv_predmeta(predmet)

        if predmet_lower not in predmeti:
            print(f"Preskočen predmet iz Excela (nema ga u CSV): {predmet}")
            continue

        info = predmeti[predmet_lower]

        profesor_raw = str(r[1]).strip()
        zvanje = str(r[3]).strip()
        ciklus = str(r[4]).strip()

        linije = [x.strip() for x in profesor_raw.split("\n") if x.strip()]
        if len(linije) > 0:
            profesor = linije[0]
            if len(linije) > 1:
                oblast = linije[-1]
                profesor = f"{profesor} ({oblast})"
        else:
            continue

        fond_p, fond_av, fond_lv = parsiraj_fond(r[7])


        if fond_p == 0 and fond_av == 0 and fond_lv == 0:
            print(f"Preskočeno zbog fonda 0: {predmet} (Vrijednost u Excelu: {r[7]})")
            continue

    
        tipovi = odredi_tipove_nastave(zvanje, fond_p, fond_av, fond_lv)

        for t in tipovi:
            key = (profesor, info["id"], t["tip"])
            if key in seen:
                continue
            seen.add(key)

            zaduzenja.append({
                "nastavnik": profesor,
                "zvanje": zvanje,
                "ciklus": ciklus,
                "predmet_id": info["id"],
                "predmet": info["naziv"],
                "smjerovi": info["smjerovi"],
                "broj_studenata": info["ukupno_studenata"],
                "semestar": r[6],
                "tip_nastave": t["tip"],
                "trajanje": t["trajanje"]
            })

    return zaduzenja

if __name__ == "__main__":
    zaduzenja = ucitaj_zaduzenja("data/zaduzenja.xlsx", "data/predmeti.csv")
    print(f"Ukupno učitano zaduženja: {len(zaduzenja)}")
    for x in zaduzenja:
        print(x)

def ucitaj_ucionice(putanja_csv):
    df = pd.read_csv(putanja_csv)

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    ucionice = {}
    for _, r in df.iterrows():
        uid = int(r["id"])
        naziv = r["naziv"]
        nkapacitet = r["kapacitet_nastava"]
        lvkapacitet = r["kapacitet_lv"]
        tip = r["tip"]
        ucionice[uid] = {
            "id": uid,
            "naziv": naziv,
            "kapacitet_nastave": nkapacitet,
            "kapacitet_lv_vjezbi" : lvkapacitet,
            "tip_ucionice": tip 
        }
    return ucionice

def ucitaj_ogranicenja(putanja_csv):
    df = pd.read_csv(putanja_csv)
    
    zelje = []
    for _, r in df.iterrows():
        tip = r["Tip"]
        if tip == "Zelja":
            opis = r["Opis"]
            zelje.append(opis)
    return zelje


