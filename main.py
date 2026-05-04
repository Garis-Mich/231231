import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import pandas as pd

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.data = []
        self.load_data()
        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Категория:").grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = tk.Entry(self.root)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка добавления расхода
        add_btn = tk.Button(self.root, text="Добавить расход", command=self.add_expense)
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица расходов
        self.tree = ttk.Treeview(self.root, columns=("amount", "category", "date"), show='headings')
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Фильтры
        tk.Label(self.root, text="Фильтр по категории:").grid(row=5, column=0, padx=5, pady=5)
        self.filter_category = tk.Entry(self.root)
        self.filter_category.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=6, column=0, padx=5, pady=5)
        self.filter_date = tk.Entry(self.root)
        self.filter_date.grid(row=6, column=1, padx=5, pady=5)

        filter_btn = tk.Button(self.root, text="Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=7, column=0, columnspan=2, pady=10)

        # Подсчёт суммы за период
        tk.Label(self.root, text="Период (ГГГГ-ММ-ДД):").grid(row=8, column=0, padx=5, pady=5)
        self.start_date_entry = tk.Entry(self.root)
        self.start_date_entry.grid(row=8, column=1, padx=5, pady=5)

        sum_btn = tk.Button(self.root, text="Сумма за период", command=self.calculate_sum)
        sum_btn.grid(row=9, column=0, columnspan=2, pady=10)

    def load_data(self):
        try:
            with open('expenses.json', 'r') as f:
                self.data = json.load(f)
                self.update_table()
        except FileNotFoundError:
            self.data = []

    def save_data(self):
        with open('expenses.json', 'w') as f:
            json.dump(self.data, f)

    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for item in self.data:
            self.tree.insert("", "end", values=(item["amount"], item["category"], item["date"]))

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()

        # Валидация ввода
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            datetime.strptime(date, "%Y-%m-%d")
            if not category:
                raise ValueError("Категория не может быть пустой")
            self.data.append({"amount": amount, "category": category, "date": date})
            self.save_data()
            self.update_table()
            self.amount_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            messagebox.showinfo("Успех", "Расход добавлен!")
            # Git: фиксируем изменения
            import os
            os.system('git add expenses.json')
            os.system('git commit -m "Добавлен новый расход"')
            os.system('git push')
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def apply_filter(self):
        category_filter = self.filter_category.get().lower()
        date_filter = self.filter_date.get()
        
        filtered_data = self.data.copy()
        
        if category_filter:
            filtered_data = [x for x in filtered_data if category_filter in x["category"].lower()]
        
        if date_filter:
            try:
                datetime.strptime(date_filter, "%Y-%m-%d")
                filtered_data = [x for x in filtered_data if x["date"] == date_filter]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты для фильтра")
        
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for item in filtered_data:
            self.tree.insert("", "end", values=(item["amount"], item["category"], item["date"]))

    def calculate_sum(self):
        start_date_str = self.start_date_entry.get()
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            
            df = pd.DataFrame(self.data)
            
            if not df.empty and "date" in df.columns and "amount" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                filtered_df = df[df["date"] >= start_date]
                total_sum = filtered_df["amount"].sum()
                messagebox.showinfo("Сумма", f"Сумма расходов с {start_date_str}: {total_sum:.2f} ₽")
            else:
                messagebox.showinfo("Сумма", "Нет данных для расчёта.")
                
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты периода")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
