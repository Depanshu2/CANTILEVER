import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Management System")
        self.geometry("1200x700")

        # Initialize bank balance
        self.bank_balance = 1000000.00  # Setting initial bank balance to 10 lakh

        # Create SQLite database
        self.conn = sqlite3.connect('finance.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, amount REAL, date TEXT, description TEXT)''')
        self.conn.commit()

        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True)

        # Create notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Create transaction tab
        transaction_tab = tk.Frame(self.notebook)
        self.notebook.add(transaction_tab, text='Transactions')

        # Create transaction widgets
        tk.Label(transaction_tab, text='Type:').grid(row=0, column=0, padx=10, pady=10)
        self.type_var = tk.StringVar()
        self.type_dropdown = ttk.Combobox(transaction_tab, textvariable=self.type_var, values=['Income', 'Expense'])
        self.type_dropdown.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(transaction_tab, text='Amount:').grid(row=1, column=0, padx=10, pady=10)
        self.amount_entry = tk.Entry(transaction_tab)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(transaction_tab, text='Date (DD-MM-YYYY):').grid(row=2, column=0, padx=10, pady=10)
        self.date_entry = tk.Entry(transaction_tab)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(transaction_tab, text='Description:').grid(row=3, column=0, padx=10, pady=10)
        self.description_entry = tk.Entry(transaction_tab)
        self.description_entry.grid(row=3, column=1, padx=10, pady=10)

        # Create bank balance widgets
        tk.Label(transaction_tab, text='Bank Balance:').grid(row=4, column=0, padx=10, pady=10)
        self.bank_balance_entry = tk.Entry(transaction_tab)
        self.bank_balance_entry.grid(row=4, column=1, padx=10, pady=10)

        update_balance_button = tk.Button(transaction_tab, text='Set Balance', command=self.set_bank_balance)
        update_balance_button.grid(row=5, column=0, padx=10, pady=10)

        # Create transaction buttons
        add_button = tk.Button(transaction_tab, text='Add', command=self.add_transaction)
        add_button.grid(row=6, column=0, padx=10, pady=10)

        edit_button = tk.Button(transaction_tab, text='Edit', command=self.edit_transaction)
        edit_button.grid(row=6, column=1, padx=10, pady=10)

        delete_button = tk.Button(transaction_tab, text='Delete', command=self.delete_transaction)
        delete_button.grid(row=6, column=2, padx=10, pady=10)

        # Create Treeview to display transactions
        self.tree = ttk.Treeview(transaction_tab, columns=('ID', 'Type', 'Amount', 'Date', 'Description'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Description', text='Description')
        self.tree.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(transaction_tab, orient='vertical', command=self.tree.yview)
        scrollbar.grid(row=7, column=3, sticky='ns')
        self.tree.configure(yscroll=scrollbar.set)

        # Create dashboard tab
        dashboard_tab = tk.Frame(self.notebook)
        self.notebook.add(dashboard_tab, text='Dashboard')

        # Create dashboard widgets
        self.figure, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        self.canvas = FigureCanvasTkAgg(self.figure, master=dashboard_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        # Create label for total balance
        self.balance_label = tk.Label(dashboard_tab, text=f'Total Balance: ${self.bank_balance:.2f}', font=('Arial', 14))
        self.balance_label.pack(pady=10)

        self.update_dashboard()
        self.update_treeview()

    def set_bank_balance(self):
        bank_balance_str = self.bank_balance_entry.get()

        # Validate bank balance input
        try:
            self.bank_balance = float(bank_balance_str)
            self.balance_label.config(text=f'Total Balance: ${self.bank_balance:.2f}')
            messagebox.showinfo("Success", "Bank balance set successfully!")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid bank balance.")

    def add_transaction(self):
        transaction_type = self.type_var.get()
        amount_str = self.amount_entry.get()
        date = self.date_entry.get()
        description = self.description_entry.get()

        # Validate amount input
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid amount.")
            return

        # Validate date format
        try:
            datetime.strptime(date, '%d-%m-%Y')
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid date in DD-MM-YYYY format.")
            return

        # Update bank balance based on expense
        if transaction_type == 'Expense':
            self.bank_balance -= amount

        # Insert the transaction into the database
        self.cursor.execute("INSERT INTO transactions (type, amount, date, description) VALUES (?, ?, ?, ?)", 
                            (transaction_type, amount, date, description))
        self.conn.commit()

        messagebox.showinfo("Success", "Transaction added successfully!")
        self.clear_entries()
        self.update_dashboard()
        self.update_treeview()

    def edit_transaction(self):
        selected = self.tree.focus()
        if selected:
            transaction_id = self.tree.item(selected)['values'][0]
            transaction_type = self.type_var.get()
            amount_str = self.amount_entry.get()
            date = self.date_entry.get()
            description = self.description_entry.get()

            # Validate amount input
            try:
                amount = float(amount_str)
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid amount.")
                return

            # Validate date format
            try:
                datetime.strptime(date, '%d-%m-%Y')
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid date in DD-MM-YYYY format.")
                return

            # Update the transaction in the database
            self.cursor.execute("UPDATE transactions SET type = ?, amount = ?, date = ?, description = ? WHERE id = ?", 
                                (transaction_type, amount, date, description, transaction_id))
            self.conn.commit()

            messagebox.showinfo("Success", "Transaction updated successfully!")
            self.clear_entries()
            self.update_dashboard()
            self.update_treeview()
        else:
            messagebox.showerror("Error", "Please select a transaction to edit.")

    def delete_transaction(self):
        selected = self.tree.focus()
        if selected:
            transaction_id = self.tree.item(selected)['values'][0]

            # Get the amount of the transaction to adjust bank balance
            self.cursor.execute("SELECT amount, type FROM transactions WHERE id = ?", (transaction_id,))
            transaction = self.cursor.fetchone()
            if transaction:
                amount, transaction_type = transaction

                # Adjust bank balance if the transaction is an expense
                if transaction_type == 'Expense':
                    self.bank_balance += amount

            # Delete the transaction from the database
            self.cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            self.conn.commit()

            messagebox.showinfo("Success", "Transaction deleted successfully!")
            self.update_dashboard()
            self.update_treeview()
        else:
            messagebox.showerror("Error", "Please select a transaction to delete.")

    def clear_entries(self):
        self.type_dropdown.set('')
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

 
    def update_dashboard(self):
    # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        # Fetch transactions from the database
        self.cursor.execute("SELECT type, amount, date FROM transactions")
        transactions = self.cursor.fetchall()

        # Calculate total income and expense
        income = sum(amount for ttype, amount, date in transactions if ttype == 'Income')
        expense = sum(amount for ttype, amount, date in transactions if ttype == 'Expense')

        # Set a fallback for empty transactions to prevent NaN issues
        if income == 0 and expense == 0:
            amounts = [1]  # Default value to avoid division by zero
            labels = ["No data available"]
            colors = ['gray']
        else:
            amounts = [income, expense]
            labels = ['Income', 'Expense']
            colors = ['green', 'red']

        # Plot income vs expense pie chart
        self.ax1.pie(amounts, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        self.ax1.set_title('Income vs Expense')

        # Plot bank balance bar chart
        self.ax2.bar(['Bank Balance'], [self.bank_balance], color='blue')
        self.ax2.set_title('Bank Balance')
        self.ax2.set_ylim(0, max(self.bank_balance, sum(amounts)) + 10000)

        # Plot income and expense trend over time
        dates = [datetime.strptime(date, '%d-%m-%Y') for _, _, date in transactions]
        income_over_time = [amount if ttype == 'Income' else 0 for ttype, amount, _ in transactions]
        expense_over_time = [amount if ttype == 'Expense' else 0 for ttype, amount, _ in transactions]

        if dates:
            df = pd.DataFrame({'Date': dates, 'Income': income_over_time, 'Expense': expense_over_time})
            df = df.groupby('Date').sum().resample('M').sum()

            self.ax3.plot(df.index, df['Income'], label='Income', color='green')
            self.ax3.plot(df.index, df['Expense'], label='Expense', color='red')
            self.ax3.set_title('Income and Expense Over Time')
            self.ax3.legend()

        # Plot category-wise expense distribution (assuming categories are set in the description)
        categories = {}
        for ttype, amount, desc in transactions:
            if ttype == 'Expense':
                category = desc if desc else 'Uncategorized'
                categories[category] = categories.get(category, 0) + amount

        if categories:
            self.ax4.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
            self.ax4.set_title('Category-wise Expense Distribution')

        # Update the canvas
        self.canvas.draw()

        # Update the balance label
        self.balance_label.config(text=f'Total Balance: ${self.bank_balance:.2f}')

    def update_treeview(self):
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch transactions from the database
        self.cursor.execute("SELECT * FROM transactions")
        transactions = self.cursor.fetchall()

        # Insert transactions into the treeview
        for transaction in transactions:
            self.tree.insert('', 'end', values=transaction)

    def run(self):
        self.mainloop()

# Create and run the finance app
if __name__ == '__main__':
    app = FinanceApp()
    app.run()

