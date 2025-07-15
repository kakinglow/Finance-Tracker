#  Finance Sheet Automation

This project automates the process of parsing and categorizing CSV bank statements, uploading them into a structured Google Sheet, and maintaining a financial summary per month.

---

##  What This Program Does

1. **Parses CSV bank statements** for specified banks.
2. **Categorizes transactions** using a simple keyword-based mapping.
3. **Uploads the data** to a year-based worksheet in a Google Sheet.
4. **Summarizes monthly spending** by category in a "Master" tab (e.g., Food, Transport, Rent).
5. **Handles multiple banks** and separates Credit/Debit transactions visually.

---

## How to Run

```bash
python finance_sheet.py <bank_statement_location> <bank>
```
Example
```bash
python finance_sheet.py statements/hsbc/june_2025.csv hsbc
```

##  Requirements
✅ 1. Google Sheets Setup

    Create a Google Sheet and copy its Spreadsheet ID (found in the URL).

    Share the sheet with the email in your credentials.json service account.

✅ 2. credentials.json

    Create a Google Service Account in the Google Cloud Console.

    Enable the Google Sheets API.

    Download the credentials.json and place it in the root of the project.

## Dependencies
Install the required libraries using:
```bash
pip install -r requirements.txt
```

##  Folder Structure & Categorization/Input/Output

  You should place your original bank statement CSV in:

    statements/<bank>/

By default, the cleaned and categorized output will go to:

    statements/<bank>/cleaned/

You can modify this behavior by adjusting the run_categorizer function in categorizing_csv.py.

By default, two banks are configured:

    hsbc → interpreted as Debit

    amex → interpreted as Credit

To add more banks or change labels, update the BANK_TYPE dictionary in finance_update.py:

    BANK_TYPE = {
      "hsbc": "Debit",
      "amex": "Credit",
      "barclays": "Debit",  # Add more here
    }

Transaction categories are determined using simple keyword matching. These are defined in utils.py under CATEGORY_RULES:

    CATEGORY_RULES = {
      "Groceries": ["tesco", "waitrose"],
      "Transport": ["tfl", "uber"],
      "Salary": ["skyscanner"],
      ...
    }


You can freely adjust the categories or add new ones to match your spending habits.

##  Google Sheets Layout

    Each year has its own tab (e.g., 2025).

    Each month creates a new block of columns.

    A "Master" tab tracks totals by category for each month and bank.

    Summary includes Total with Salary and Total without Salary for clarity.

##  Optional: Monthly Reminder

You can set a Task Scheduler entry on Windows to run a reminder script on the 1st of every month to remind you to download your latest bank statements. You can use tkinter for a simple pop-up.

Example reminder script:

    # finance_reminder.py
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Reminder", "Download your bank CSV files for this month.")

Then schedule it in Task Scheduler using your full Python path and script location.

