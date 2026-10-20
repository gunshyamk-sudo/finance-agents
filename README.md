# Finance Agents - Starter Pack

Companion to the workbook "Finance_AI_Agents_30_Day_Plan.xlsx". Follow the Step-by-Step Guide tab; it tells you exactly when to open each file.

## Folders
- data/    synthetic (fake) finance data - safe to use with any AI tool
- code/    reference scripts, one per day (dayNN_...). Type them yourself first, then compare.
- outputs/ created automatically when you run scripts

## Setup (Day 1)
    python -m venv .venv
    .venv\Scripts\activate          (Windows)   |   source .venv/bin/activate   (Mac)
    pip install -r requirements.txt
    copy .env.example .env          (Windows)   |   cp .env.example .env        (Mac)
Then open .env and paste your API key.

## Run a script
    cd code
    python day04_trial_balance.py

All data is fictional and generated for learning.
