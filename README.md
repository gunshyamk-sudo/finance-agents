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


## My finance agent ideas

| # | Task I did manually | Hours / month | Data used | Risk if AI gets it wrong |
|---|---------------------|---------------|-----------|--------------------------|
| 1 | Coding supplier invoices to GL accounts | 20 | Invoices (PDF), chart of accounts | Wrong P&L classification |
| 2 | Bank reconciliation | 12 | Bank statement, GL cash | Missed errors or fraud |
| 3 | Monthly variance commentary | 8 | Budget vs actual | Misleading management report |
| 4 | Chasing overdue customer invoices | 10 | AR ageing, emails | Upsetting good customers |
| 5 | Checking expense claims against policy | 15 | Expense claims, policy | Policy breaches missed |
| 6 | VAT return preparation checks | 6 | Sales/purchase ledgers | Penalties from FTA |
| 7 | Intercompany matching | 8 | Entity ledgers | Consolidation errors |
| 8 | Month-end accrual listing | 5 | AP ledger, POs | Misstated expenses |
| 9 | Duplicate payment checks | 4 | AP payment runs | Cash loss |
| 10 | Answering policy questions from staff | 6 | Finance policy manual | Wrong guidance given |