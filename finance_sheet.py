from finance_update import update_finance_sheet
from utils import run_categorizer
import sys


def main():
    if len(sys.argv) != 3:
        print("Useage: python3 main.py <csv_filname> <bank>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    bank = sys.argv[2]

    try:
        cleaned_csv = run_categorizer(csv_file_path, bank)
        update_finance_sheet(cleaned_csv, bank)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
