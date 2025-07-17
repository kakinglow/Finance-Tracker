import csv
import os
import re
from google.oauth2.service_account import Credentials
import gspread

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CATEGORY_RULES = {
    "Groceries": ["tesco", "waitrose", "sainsburys", "zapp", "tian tian"],
    "Food & Dining": [
        "nandos",
        "just eat",
        "uber",
        "watchhouse",
        "food",
        "tea",
        "dumpling",
        "restaurant",
        "market hall",
    ],
    "Transport": ["tfl", "national rail", "uber travel"],
    "Bills & Subscriptions": [
        "ee",
        "housekeep",
        "communityfibre",
        "british gas",
        "telegram",
        "discord",
    ],
    "Rent & Housing": ["gateway", "council tax"],
    "Leisure": ["uniqlo", "dsm", "paypal", "threatre", "amazon"],
    "Salary": ["skyscanner"],
}


def clean_csv(input_file_name: str) -> list:
    clean_rows = []

    with open(input_file_name, newline="", encoding="utf-8") as file:
        bank_statement = csv.reader(file)
        for row in bank_statement:
            if len(row) != 3:
                continue
            date, description, amount = row

            clean_description = re.sub(r"\)+$", "", description)
            clean_description = re.sub(r"\s{2,}", " ", clean_description)
            clean_description = clean_description.rstrip()
            clean_amount = amount.replace(",", "").strip()
            clean_rows.append([date.strip(), clean_description, clean_amount])

    return clean_rows


def category_labelling(description: str) -> str:
    description = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in description for keyword in keywords):
            return category

    return "Other"


def save_to_csv(rows: list, file_path: str):
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Description", "Amount", "Category"])
        writer.writerows(rows)


def set_dynamic_month_column(
    sheet: gspread.Worksheet, month: str, col_block_width=10
) -> int:
    first_row = sheet.row_values(1)
    for block_start in range(0, len(first_row), col_block_width):
        middle_index = block_start + (col_block_width // 2)
        if (
            middle_index < len(first_row)
            and first_row[middle_index].strip().lower() == month.lower()
        ):
            return block_start + 1

    last_filled = max(
        [index for index, value in enumerate(first_row) if value.strip()], default=-1
    )
    next_block_start = ((last_filled // col_block_width) + 1) * col_block_width
    middle_index = next_block_start + (col_block_width // 2)

    sheet.update_cell(1, middle_index + 1, month)

    return next_block_start + 1


def authenticate_open_worksheet(
    SCOPES: list[str], SPREADSHEET_ID: str
) -> gspread.Spreadsheet:
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet


def month_year_extractor(csv_path: str) -> str:
    filename = os.path.basename(csv_path)
    month_str, year = filename.replace(".csv", "").split("_")
    month = month_str.capitalize()

    return month, year


def label_rows(cleaned_csv: str) -> list:
    return [
        [date, description, amount, category_labelling(description)]
        for date, description, amount in cleaned_csv
    ]


def run_categorizer(input_file_path: str, bank: str) -> str:
    cleaned_rows = clean_csv(input_file_path)

    labeled_rows = label_rows(cleaned_rows)

    output_dir = os.path.join("statements", bank, "cleaned")
    os.makedirs(output_dir, exist_ok=True)

    output_file_path = os.path.join(output_dir, os.path.basename(input_file_path))

    save_to_csv(labeled_rows, output_file_path)
    print(f"Categorized data saved to {output_file_path}")
    return output_file_path
