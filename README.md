# swe-testing-assignment

Quick-calc is a simple calculator application with a Tkinter UI. It supports addition, subtraction, multiplication, and division, including handling of division by zero, and a clear action that resets the current input and result to zero. 
The repository demonstrates a layered testing approach.

## Setup Instructions

### Requirements
- Python 3.10+
- Git

### Research
For python the most used frameworks for automated testing are unittest and pytest. I've chosen pytest for two reasons. 1. I've already worked with it before, so in was easier for me to implement everything using this famework. 2. Overall, it allows writing tests in a shoeter and easier way, and for example combine all tests in a single file, which is very suitable for such small task.
Even though, unittest is included in python, it requires much more syntxsis kwowlwdge and more complex code


### Install dependencies, run, tests
```bash
python3 -m venv .venv
source .venv/bin/activate # macOS/Linux
# .venv\Scripts\activate # Windows

pip install -r requirements.txt
python -m quick_calc.app # Run
pytest # Tests




