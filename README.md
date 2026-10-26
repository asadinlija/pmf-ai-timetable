# PMF AI Timetable

A Python project for generating and optimizing university timetables using AI techniques. It automates the assignment of classes, rooms, teachers, and time slots while respecting constraints such as availability, course conflicts, and resource limits.

Developed as part of the "Introduction to Artificial Intelligence" course at the Faculty of Science (PMF), University of Sarajevo.

## Features

- Load scheduling data from input files (courses, teachers, rooms, groups)
- Detect conflicts between lectures
- Generate feasible timetable assignments
- Optimize schedule quality with search and optimization heuristics
- Export results in a readable format
- Easy to extend with new constraints and evaluation rules

## Tech Stack

- Python 3.9+
- Standard library
- Optional: `pandas`, `numpy`, `networkx`, `matplotlib`, `scikit-learn`, `ortools` / `pulp`

## Project Structure

```text
pmf-ai-timetable/
├── data/               # Input datasets and sample files
├── src/
│   ├── __init__.py
│   ├── parser.py       # Data loading and parsing
│   ├── constraints.py  # Constraint definitions
│   ├── solver.py       # AI / optimization logic
│   ├── evaluator.py    # Schedule quality evaluation
│   └── utils.py        # Helper functions
├── tests/              # Unit tests
├── main.py             # Entry point
├── requirements.txt
├── LICENSE
└── README.md
```

## Getting Started

### Installation

```bash
git clone https://github.com/asadinlija/pmf-ai-timetable.git
cd pmf-ai-timetable

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### Usage

```bash
python main.py
```

## Input Data

Input is a JSON file describing courses, rooms, and time slots:

```json
{
  "courses": [
    {
      "code": "CS101",
      "name": "Introduction to Programming",
      "teacher": "T1",
      "group": "G1",
      "duration": 2
    }
  ],
  "rooms": ["R101", "R202"],
  "timeslots": ["Mon 09:00", "Mon 11:00", "Tue 09:00"]
}
```

## How It Works

1. Parse and validate the input data
2. Generate candidate assignments
3. Evaluate each candidate against hard and soft constraints
4. Select the best feasible schedule

Supported approaches: backtracking, hill climbing, simulated annealing, genetic algorithms, and optimization solvers.

## Constraints

**Hard constraints**
- A teacher cannot teach two classes at the same time
- A room cannot host two classes at once
- A group cannot attend two lectures simultaneously
- Some classes have fixed time slots

**Soft constraints**
- Priority for certain courses or instructors

## Example Output

```text
Mon 09:00   CS101    R101   T1   G1
Mon 11:00   MATH201  R202   T2   G2
Tue 09:00   PHYS101  R101   T3   G1
```

## Testing

```bash
pytest
```

## Contact

Questions or collaboration: open an issue or contact the repository owner.
