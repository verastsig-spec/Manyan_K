#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Currency Converter — Конвертер валют с API и историей
Автор: [Ваше Имя Фамилия]
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# === Конфигурация ===
API_URL = "https://v6.exchangerate-api.com/v6/{}/latest/{}"
# 🔑 Замените на ваш API-ключ или используйте переменную окружения
API_KEY = os.getenv("EXCHANGE_API_KEY", "your_api_key_here")
HISTORY_FILE = "history.json"


class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("💱 Currency Converter")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        
        # Загрузка данных
        self.currencies = []
        self.history = self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        self.load_currencies()
        
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # === Заголовок ===
        title = tk.Label(
            self.root, 
            text="💱 Конвертер валют", 
            font=("Arial", 16, "bold"),
            pady=10
        )
        title.pack()
        
        # === Фрейм ввода ===
        input_frame = tk.LabelFrame(self.root, text="Параметры конвертации", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Сумма
        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", pady=5)
        self.amount_entry = tk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        self.amount_entry.insert(0, "1.0")
        
        # Выбор валют
        tk.Label(input_frame, text="Из:").grid(row=0, column=2, sticky="w", padx=10)
        self.from_currency = ttk.Combobox(input_frame, width=10, state="readonly")
        self.from_currency.grid(row=0, column=3, padx=5)
        
        tk.Label(input_frame, text="В:").grid(row=0, column=4, sticky="w", padx=10)
        self.to_currency = ttk.Combobox(input_frame, width=10, state="readonly")
        self.to_currency.grid(row=0, column=5, padx=5)
        
        # Кнопка конвертации
        convert_btn = tk.Button(
            input_frame, 
            text="🔄 Конвертировать", 
            command=self.convert_currency,
            bg="#4CAF50", 
            fg="white",
            font=("Arial", 9, "bold")
        )
        convert_btn.grid(row=1, column=0, columnspan=6, pady=10, sticky="ew")
        
        # === Результат ===
        result_frame = tk.LabelFrame(self.root, text="Результат", padx=10, pady=10)
        result_frame.pack(fill="x", padx=10, pady=5)
        
        self.result_label = tk.Label(
            result_frame, 
            text="Введите параметры и нажмите «Конвертировать»",
            font=("Arial", 11),
            fg="#333"
        )
        self.result_label.pack()
        
        # === История ===
        history_frame = tk.LabelFrame(self.root, text="📜 История конвертаций", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Таблица истории
        columns = ("date", "from", "to", "amount", "result", "rate")
        self.history_table = ttk.Treeview(
            history_frame, 
            columns=columns, 
            show="headings",
            height=6
        )
        
        # Настройка колонок
        self.history_table.heading("date", text="Дата")
        self.history_table.heading("from", text="Из")
        self.history_table.heading("to", text="В")
        self.history_table.heading("amount", text="Сумма")
        self.history_table.heading("result", text="Результат")
        self.history_table.heading("rate", text="Курс")
        
        self.history_table.column("date", width=100)
        self.history_table.column("from", width=60)
        self.history_table.column("to", width=60)
        self.history_table.column("amount", width=80)
        self.history_table.column("result", width=80)
        self.history_table.column("rate", width=70)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=scrollbar.set)
        
        self.history_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления историей
        btn_frame = tk.Frame(history_frame)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="🗑️ Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        tk.Button(btn_frame, text="💾 Экспорт JSON", command=self.export_history).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Импорт JSON", command=self.import_history).pack(side="left", padx=5)
        
        # Обновление таблицы
        self.refresh_history_table()
    
    def load_currencies(self):
        """Загрузка списка валют из API"""
        try:
            # Используем USD как базовую валюту для получения списка
            url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.currencies = sorted(list(data["conversion_rates"].keys()))
                
                # Заполнение комбобоксов
                self.from_currency["values"] = self.currencies
                self.to_currency["values"] = self.currencies
                
                # Значения по умолчанию
                self.from_currency.set("USD")
                self.to_currency.set("EUR")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить курсы валют")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка подключения", f"Проверьте интернет-соединение:\n{e}")
    
    def validate_input(self):
        """Проверка корректности ввода"""
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            return amount
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректная сумма:\n{e}")
            return None
    
    def get_exchange_rate(self, from_curr, to_curr):
        """Получение курса валют через API"""
        try:
            url = API_URL.format(API_KEY, from_curr)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                rates = response.json()["conversion_rates"]
                return rates.get(to_curr)
            else:
                messagebox.showerror("API Error", f"Код ответа: {response.status_code}")
                return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить курс:\n{e}")
            return None
    
    def convert_currency(self):
        """Основная логика конвертации"""
        # Валидация
        amount = self.validate_input()
        if amount is None:
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        if not from_curr or not to_curr:
            messagebox.showwarning("Внимание", "Выберите обе валюты")
            return
        
        # Получение курса
        rate = self.get_exchange_rate(from_curr, to_curr)
        if rate is None:
            return
        
        # Расчёт
        result = amount * rate
        
        # Отображение результата
        self.result_label.config(
            text=f"{amount:,.2f} {from_curr} = {result:,.2f} {to_curr}\n"
                 f"Курс: 1 {from_curr} = {rate:.6f} {to_curr}",
            fg="#2E7D32"
        )
        
        # Сохранение в историю
        self.add_to_history({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": round(result, 2),
            "rate": round(rate, 6)
        })
    
    def load_history(self):
        """Загрузка истории из файла"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def save_history(self):
        """Сохранение истории в файл"""
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_to_history(self, record):
        """Добавление записи в историю"""
        self.history.insert(0, record)  # Добавляем в начало
        if len(self.history) > 100:  # Ограничение истории
            self.history = self.history[:100]
        self.save_history()
        self.refresh_history_table()
    
    def refresh_history_table(self):
        """Обновление таблицы истории"""
        # Очистка
        for item in self.history_table.get_children():
            self.history_table.delete(item)
        
        # Заполнение
        for record in self.history:
            self.history_table.insert("", "end", values=(
                record["date"],
                record["from"],
                record["to"],
                f"{record['amount']:.2f}",
                f"{record['result']:.2f}",
                f"{record['rate']:.6f}"
            ))
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_table()
    
    def export_history(self):
        """Экспорт истории в отдельный файл"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "История экспортирована!")
    
    def import_history(self):
        """Импорт истории из файла"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    imported = json.load(f)
                self.history = imported + self.history  # Объединение
                self.save_history()
                self.refresh_history_table()
                messagebox.showinfo("Успех", f"Импортировано {len(imported)} записей")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать:\n{e}")


def main():
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
