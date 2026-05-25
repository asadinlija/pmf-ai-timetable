import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from config import DANI, SLOT_VREMENA

def generisi_pdf_raspored(raspored, smjer, godina, semestar, putanja_pdf):
    # 1. Inicijalizacija prazne tabele sa naslovima
    tabela = [["SATNICA"] + DANI]
    for slot in range(1, 13):
        red = [SLOT_VREMENA[slot]] + [""] * 5
        tabela.append(red)

    # 2. Popunjavanje sirovih podataka iz rasporeda
    for d in raspored:
        if (smjer, godina) not in d["grupe"]:
            continue
        dan_idx = DANI.index(d["termin"][0]) + 1
        slot_idx = d["termin"][1]
        naziv_ucionice = d["ucionica"]["naziv"] if isinstance(d["ucionica"], dict) else d["ucionica"]
        
        # Koristimo HTML tag <br/> za prelom unutar Paragraph-a
        sadrzaj = f"<b>{d['predmet']}</b><br/>({d['tip']})<br/><i>{naziv_ucionice}</i>"
        
        if tabela[slot_idx][dan_idx]:
            tabela[slot_idx][dan_idx] += f"<br/><font color='gray'>-----------------------</font><br/>{sadrzaj}"
        else:
            tabela[slot_idx][dan_idx] = sadrzaj

    # 3. Postavka stilova za tekst unutar ćelija
    styles = getSampleStyleSheet()
    
    # Stil za obične ćelije (centrirano, malo manji font da sve stane)
    stil_celije = ParagraphStyle(
        'StilCelije',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        alignment=1  # 1 označava CENTER
    )
    
    # Stil za zaglavlja (satnica i dani)
    stil_zaglavlja = ParagraphStyle(
        'StilZaglavlja',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    
    # Stil za kolonu sa satnicama
    stil_satnice = ParagraphStyle(
        'StilSatnice',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#333333'),
        alignment=1
    )

    # 4. Pretvaranje svih stringova u Paragraph objekte (KLJUČNI KORAK ZA REPORTLAB)
    procesirana_tabela = []
    for i, red in enumerate(tabela):
        novi_red = []
        for j, celija in enumerate(red):
            if i == 0:  # Prvi red (Dani)
                novi_red.append(Paragraph(celija, stil_zaglavlja))
            elif j == 0:  # Prva kolona (Satnica)
                novi_red.append(Paragraph(celija, stil_satnice))
            else:  # Predmeti unutar rasporeda
                if celija == "":
                    novi_red.append("")
                else:
                    novi_red.append(Paragraph(celija, stil_celije))
        procesirana_tabela.append(novi_red)

    # 5. Kreiranje dokumenta u landscape formatu
    os.makedirs(os.path.dirname(putanja_pdf), exist_ok=True)
    doc = SimpleDocTemplate(
        putanja_pdf,
        pagesize=landscape(A4),
        rightMargin=1*cm, leftMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm
    )

    # Naslov dokumenta
    stil_naslova = ParagraphStyle(
        'NaslovRasporeda',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        alignment=1,
        spaceAfter=10
    )
    naslov = Paragraph(
        f"RASPORED ČASOVA - {smjer.upper()} - {godina}. GODINA - {semestar.upper()} SEMESTAR",
        stil_naslova
    )

    # 6. Definisanje profesionalnog dizajna tabele
    stil_tabele = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')), # Tanja, siva mreža umjesto debele crne
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')), # Tamno plava boja za dane (izgleda akademski)
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f7fafc')), # Blaga siva pozadina za satnicu
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#fcfcfc')]), # Naizmjenični redovi
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])

    # Širine kolona (ukupno 27.5cm, idealno za A4 landscape sa marginama od 1cm)
    col_widths = [2.5*cm] + [5*cm] * 5
    
    # Ostavljamo rowHeights=None da se visina reda automatski prilagodi količini teksta
    t = Table(procesirana_tabela, colWidths=col_widths, rowHeights=None)
    t.setStyle(stil_tabele)

    # Izgradnja dokumenta
    doc.build([naslov, Spacer(1, 0.2*cm), t])
    print(f"PDF uspjesno generisan na lokaciji: {putanja_pdf}")

def generisi_sve_rasporede(raspored, putanja_folder="output/rasporedi"):    

    # sve jedinstvene kombinacije smjer+godina
    kombinacije = set()

    for d in raspored:
        for (smjer, godina) in d["grupe"]:
            kombinacije.add((smjer, godina))

    for (smjer, godina) in sorted(kombinacije):
        putanja = f"{putanja_folder}/{smjer}_godina{godina}.pdf"
        try:
            generisi_pdf_raspored(raspored, smjer, godina, "zimski", putanja)
        except Exception as e:

            print(f"Greska za {smjer} godina {godina}: {e}")