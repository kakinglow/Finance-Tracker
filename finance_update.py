from utils import (
    set_dynamic_month_column,
    SCOPES,
    authenticate_open_worksheet,
    month_year_extractor,
)
import gspread
from gspread.utils import rowcol_to_a1
import pandas as pd
from gspread_formatting import format_cell_range, CellFormat, TextFormat, NumberFormat
from google_secrets import SPREADSHEET_ID


BANK_TYPE = {"hsbc": "Debit", "amex": "Credit"}

BANK_COLUMN_OFFSETS = {"Debit": 0, "Credit": 6}

CATEGORIES = [
    "Salary",
    "Investment",
    "Food & Dining",
    "Transport",
    "Groceries",
    "Bills & Subscriptions",
    "Rent & Housing",
    "Leisure",
    "Other",
]


def summarize_category_totals(df: pd.DataFrame, bank_type: str) -> list:
    filtered = df.copy()
    filtered = filtered[filtered["Category"].notnull()]
    summary = filtered.groupby("Category")["Amount"].sum().to_dict()
    return [round(summary.get(cat, 0.0), 2) for cat in CATEGORIES]


def update_master_summary_from_data(
    values: list, month: str, year: str, bank_type: str
) -> None:
    sheet = authenticate_open_worksheet(SCOPES, SPREADSHEET_ID)
    master = sheet.worksheet("Master")

    bold = CellFormat(textFormat=TextFormat(bold=True))
    money = CellFormat(numberFormat=NumberFormat(type="CURRENCY", pattern="£#,##0.00"))

    headers = master.row_values(2)
    expected_headers = ["Year", "Label"] + CATEGORIES + ["Total (No Salary)", "Total"]

    if headers[: len(expected_headers)] != expected_headers:
        master.update("A2", [expected_headers])
        master.update_acell("A1", "Finance Overview")
        format_cell_range(master, "A1", bold)
        format_cell_range(master, f"A2:{chr(65 + len(expected_headers) - 1)}2", bold)

    label = f"{month} - {bank_type}"
    total_without_salary = round(sum(values[1:]), 2)
    total_with_salary = round(sum(values), 2)
    new_row = [year, label] + values + [total_without_salary, total_with_salary]


    start_column = 3
    end_column = 2 + len(CATEGORIES) + 2
    start_cell = rowcol_to_a1(3, start_column)
    end_cell = rowcol_to_a1(3, end_column)
    master.insert_row(new_row, index=3)
    format_cell_range(master, f"{start_cell}:{end_cell}", money)

    master.set_basic_filter(f"A2:{chr(65 + len(expected_headers) - 1)}2")


    print(f"✅ Master sheet updated: {label} (row 3)")


def update_finance_sheet(csv_file: str, bank: str) -> None:
    sheet = authenticate_open_worksheet(SCOPES, SPREADSHEET_ID)

    month, year = month_year_extractor(csv_file)

    df = pd.read_csv(csv_file)
    df.columns = [column.strip() for column in df.columns]
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)

    try:
        worksheet = sheet.worksheet(year)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=year, rows="1000", cols="100")

    start_column = set_dynamic_month_column(worksheet, month)

    bank_type = BANK_TYPE.get(bank.lower(), "Other")
    offset = BANK_COLUMN_OFFSETS.get(bank_type, 0)

    worksheet.update_cell(2, start_column + offset, bank_type)

    data = df.values.tolist()

    start_row = 3
    start_col = start_column + offset

    num_rows = len(data)
    num_columns = len(data[0]) if data else 0

    end_row = start_row + num_rows - 1
    end_column = start_column + num_columns - 1

    cell_range = (
        f"{rowcol_to_a1(start_row, start_col)}:{rowcol_to_a1(end_row, end_column)}"
    )

    worksheet.update(range_name=cell_range, values=data)

    print(f"Successfully updated worksheet {year} with {month} / {bank_type} data")

    category_totals = summarize_category_totals(df, bank_type)
    update_master_summary_from_data(category_totals, month, year, bank_type)
