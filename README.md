# Parkinson's Disease Detection System

A Python-based application that assesses Parkinson's disease risk through motor skill tests.

![image](https://github.com/user-attachments/assets/9d25569a-aca7-4e65-a125-e691a09e738f)

## Features

- **Three diagnostic tests**:
  - Follow Line Test (assesses hand steadiness)
  - Draw Square Test (evaluates fine motor control)
  - Click Targets Test (measures reaction time and accuracy)

- **Comprehensive analysis**:
  - Calculates deviation from ideal path
  - Measures movement smoothness
  - Evaluates reaction times and consistency

- **Personalized recommendations**:
  - Provides food suggestions based on risk level
  - Visualizes test results with clear graphics

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- numpy (`pip install numpy`)

## How to Run

```bash
python parkinsons_detection.py
```

## Usage

1. Complete all three tests:
   - Follow the line while holding mouse button
   - Trace the square outline
   - Click moving targets as quickly as possible

2. View your results and risk assessment

![image](https://github.com/user-attachments/assets/66265aaa-2b1c-40e0-ade4-7abe2d332b96)

## Technical Details

- Uses mouse movement analysis to assess motor skills
- Implements mathematical models to calculate:
  - Mean squared error from ideal path
  - Movement smoothness (jerk analysis)
  - Reaction time statistics

## Disclaimer

This application provides preliminary assessment only and is not a medical diagnosis tool. Always consult with healthcare professionals for proper medical evaluation.

---

## Screenshot Description

The screenshot shows the application interface with:
1. Left panel with test buttons and settings
2. Main canvas area displaying the Follow Line test in progress
3. Results panel at the bottom showing test instructions
4. Clean, modern UI with intuitive controls

## License

MIT License - Free for educational and research purposes
