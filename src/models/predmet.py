class Predmet:
    def __init__(self, id, naziv, smjer, godina, broj_studenata):
        self.id = id
        self.naziv = naziv
        self.smjer = smjer
        self.godina = godina
        self.broj_studenata = broj_studenata

        self.profesor = None
        self.asistent = None

        self.predavanja = 0
        self.vjezbe = 0