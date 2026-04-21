# UFC Predictions

A terminal-based UFC fight prediction tool. Enter two fighters and get a predicted winner based on their historical stats.

## Setup

Install dependencies:

```
pip install pandas scikit-learn joblib
```

## Running

```
python app.py
```

Fighter data is sourced from the UFC Stats website. Fighter names must match the site exactly (first and last name, capitalized).

## Requirements

- Python 3.10+
- anaconda or pip

## Features

- Match up any two fighters in the dataset
- Supports multiple models and datasets
- Confidence score for each prediction
- Past predictions log with delete support