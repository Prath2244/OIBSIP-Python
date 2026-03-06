import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt

class BMISystem:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator Project")
        
        try:
            self.db = sqlite3.connect("data.db")
            self.db.execute("CREATE TABLE IF NOT EXISTS logs (name TEXT, bmi REAL)")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
            root.destroy()

        tk.Label(root, text="Name:").pack()
        self.e_name = tk.Entry(root); self.e_name.pack()
        
        tk.Label(root, text="Weight (kg):").pack()
        self.e_w = tk.Entry(root); self.e_w.pack()
        
        tk.Label(root, text="Height (m):").pack()
        self.e_h = tk.Entry(root); self.e_h.pack()

        tk.Button(root, text="Calculate & Save", command=self.run).pack(pady=10)
        tk.Button(root, text="Show Trend", command=self.plot).pack()
        
        self.res = tk.Label(root, text="", font=("Arial", 12, "bold"))
        self.res.pack(pady=10)

    def run(self):
        try:
            n = self.e_name.get().strip()
            w_str = self.e_w.get()
            h_str = self.e_h.get()

            if not n or not w_str or not h_str:
                messagebox.showwarning("Input Error", "All fields are required!")
                return

            w, h = float(w_str), float(h_str)

            if not (0.5 <= h <= 3.0):
                messagebox.showwarning("Range Error", "Height must be between 0.5m and 3.0m.")
                return
            if not (2.0 <= w <= 500.0):
                messagebox.showwarning("Range Error", "Weight must be between 2kg and 500kg.")
                return

            bmi = round(w / (h**2), 2)

            if bmi < 18.5: 
                cat = "Underweight"
            elif bmi < 25: 
                cat = "Normal"
            else: 
                cat = "Overweight/Obese"

            self.db.execute("INSERT INTO logs VALUES (?, ?)", (n, bmi))
            self.db.commit()
            
            self.res.config(text=f"{cat} (BMI: {bmi})", fg="green")

        except ValueError:
            messagebox.showerror("Data Error", "Please enter numeric values for weight and height.")
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")

    def plot(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Enter a name to see their trends.")
            return

        data = self.db.execute("SELECT bmi FROM logs WHERE name=?", (name,)).fetchall()
        
        if data:
            values = [d[0] for d in data]
            plt.figure("BMI Trend")
            plt.plot(values, marker='o', color='b')
            plt.title(f"Trends for {name}")
            plt.ylabel("BMI")
            plt.show()
        else:
            messagebox.showinfo("Empty", f"No data found for user: {name}")

if __name__ == "__main__":
    root = tk.Tk()
    BMISystem(root)
    root.mainloop()