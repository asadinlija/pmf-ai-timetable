# PMF AI Timetable

Automatic generation of weekly class timetables for the Faculty of Science (PMF), University of Sarajevo, using metaheuristic algorithms. The project compares two optimization approaches, **Simulated Annealing (SA)** and **Artificial Bee Colony (ABC)**, on real data about teachers, courses and classrooms.

Developed as part of the "Introduction to Artificial Intelligence" course.

## Features

- Loads teacher assignments (Excel), courses, classrooms and constraints (CSV)
- Plans the **winter** (semesters I, III, V) and **summer** (semesters II, IV, VI) semesters separately
- Schedules over 5 days × 12 hourly slots (08:00–20:00)
- Automatically splits students into groups for lab exercises based on computer lab capacity
- Evaluates timetables with a penalty function (hard and soft constraints)
- Exports timetables to PDF, per study program and year
- Statistical comparison of SA and ABC (30 independent runs, significance tests, plots)

## Project Structure

```text
pmf-ai-timetable/
├── data/
│   ├── zaduzenja.xlsx        # Teacher assignments per course
│   ├── predmeti.csv          # Courses, programs, years, student counts
│   ├── ucionice.csv          # Classrooms, capacities and types
│   ├── ogranicenja.csv       # Hard/soft constraints and teacher wishes
│   └── rezultati.json        # Results of 30 runs of each algorithm
├── src/
│   ├── main.py               # Entry point: generates timetables and PDFs
│   ├── config.py             # Days, time slots, penalty weights
│   ├── parser_podataka.py    # Input data loading and processing
│   ├── generator.py          # Initial (random) timetable generation
│   ├── evaluator.py          # Penalty function (constraints)
│   ├── pdf_generator.py      # PDF export (reportlab)
│   └── algorithms/
│       ├── sa_algorithm.py  # Simulated Annealing
│       └── abc_algorithm.py # Artificial Bee Colony
├── analysis/
│   ├── analiza.py            # Runs SA/ABC 30 times, writes rezultati.json
│   ├── statistika.py         # Statistics and plots from rezultati.json
│   └── plots/                # Box plots and convergence curve
├── output/                   # Generated PDF timetables
│   ├── zimski_sa/  zimski_abc/
│   └── ljetni_sa/  ljetni_abc/
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/asadinlija/pmf-ai-timetable.git
cd pmf-ai-timetable

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

Data loading and analysis also need other packages the code imports:

```bash
pip install pandas openpyxl numpy scipy matplotlib seaborn reportlab
```

## Usage

Run all commands from the **project root** (data paths are relative).

**Generate timetables and PDFs**

```bash
python src/main.py
```

Runs SA and ABC for both semesters and writes PDFs to `output/<semester>_<algorithm>/`, e.g. `output/zimski_sa/KN_godina1.pdf`. Programs: KN, IT, OP, NM, NMI, PM.

**Compare the algorithms (30 runs)**

```bash
python analysis/analiza.py       # slow; writes data/rezultati.json
python analysis/statistika.py    # statistics and plots in analysis/plots/
```

## Constraints

Full descriptions are in [data/ogranicenja.csv](data/ogranicenja.csv).

**Hard (H1–H9):** no overlaps for teachers, rooms, or students of the same program and year; shared courses of multiple programs are held together; room capacity must fit the student count; exact weekly hours (lectures, exercises, labs); lab exercises only in computer labs; full-time staff have no classes on Thursday 13:00–14:00 (Faculty Council meeting).

**Soft (S1–S9):** minimal gaps for students and teachers, at most 5 consecutive classes, even distribution across the week, master-level courses (year 4 and above) in the afternoon, lectures before exercises, non-permanent staff preferably from 16:00, Programming I labs in room A1 (ABG), individual teacher wishes (S9, see below).

Each hard-constraint violation adds a penalty of 1,000,000 (`HARD_PENAL`); soft constraints use the weights in [src/config.py](src/config.py). The algorithms **minimize the total penalty**, so a timetable with no hard violations has a penalty well below 1,000,000.

**Teacher wishes.** `data/ogranicenja.csv` lists wishes Z1–Z28 for documentation, but the wishes are implemented per teacher (by name) directly in the S9 block of [src/evaluator.py](src/evaluator.py), not read from the CSV. Teachers without a rule there have no wishes.

## Algorithms

Both algorithms start from random timetables and use the same neighborhood operator: a random class is picked and assigned a new time slot and a new classroom (a computer lab for lab exercises).

| Algorithm           | Parameters (as used in `main.py` and `analiza.py`)                                  |
| ------------------- | ----------------------------------------------------------------------------------- |
| Simulated Annealing | initial temperature 100,000, stop at 1,000, α = 0.95, 150 iterations per temperature |
| ABC                 | colony of 20 bees, limit 50, 700 iterations (employed, onlooker and scout phases)    |

## Analysis

`statistika.py` computes descriptive statistics of penalty and runtime for each semester, tests normality (Shapiro-Wilk), picks a paired t-test or Wilcoxon test, computes Cliff's delta, and plots a box plot and convergence curve (in `analysis/plots/`).

## Tech Stack

Python 3 (the project was run with 3.14), pandas, openpyxl, NumPy, SciPy, Matplotlib, Seaborn, ReportLab.
