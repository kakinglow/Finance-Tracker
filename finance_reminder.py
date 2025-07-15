import tkinter as tk
from tkinter import messagebox

def show_reminder():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Finance Sheet Reminder",
        "Don't forget to download your bank statements (Credit/Debit) for the month that just ended!"
    )

if __name__ == "__main__":
    show_reminder()