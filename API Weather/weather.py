import tkinter as tk
from tkinter import messagebox
import requests
import geocoder

class WeatherAPI:
    def __init__(self, window):
        self.window = window
        self.window.title("Weather")
        self.window.geometry("380x600")
        self.window.configure(bg="#ffffff")
        
        self.unit = "celsius" 
        self.last_data = None
        self.last_name = ""
        self.placeholder = "Enter city..."

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        self.colors = {
            "bg": "#ffffff", "text": "#1a1a1a", "dim": "#71717a", "border": "#e4e4e7",
            "freezing": "#0ea5e9", "cold": "#3b82f6", "mild": "#10b981", "warm": "#f59e0b", "hot": "#ef4444"
        }

    def create_widgets(self):
        self.search_frame = tk.Frame(self.window, bg=self.colors["bg"], pady=30)
        self.search_frame.pack(fill="x", padx=40)

        self.city_entry = tk.Entry(
            self.search_frame, font=("Helvetica", 12), 
            bg=self.colors["bg"], fg=self.colors["dim"],
            borderwidth=0, highlightthickness=1, highlightbackground=self.colors["border"]
        )
        self.city_entry.pack(fill="x", ipady=8)
        
        self.city_entry.insert(0, self.placeholder)
        
        self.city_entry.bind("<FocusIn>", self.on_focus_in)
        self.city_entry.bind("<FocusOut>", self.on_focus_out)
        self.city_entry.bind('<Return>', lambda e: self.get_weather())

        self.main_area = tk.Frame(self.window, bg=self.colors["bg"])
        self.main_area.pack(expand=True, fill="both", padx=40)

        header = tk.Frame(self.main_area, bg=self.colors["bg"])
        header.pack(fill="x")
        self.city_label = tk.Label(header, text="WEATHER", font=("Helvetica", 10, "bold"), bg=self.colors["bg"], fg=self.colors["dim"])
        self.city_label.pack(side="left")

        self.unit_btn = tk.Button(header, text="°C / °F", font=("Helvetica", 8, "bold"), relief="flat", command=self.toggle_temp, cursor="hand2")
        self.unit_btn.pack(side="right")

        self.temp_label = tk.Label(self.main_area, text="--°", font=("Helvetica", 72, "bold"), bg=self.colors["bg"])
        self.temp_label.pack(anchor="w")

        self.status_label = tk.Label(self.main_area, text="READY", font=("Helvetica", 14, "bold"), bg=self.colors["bg"], fg=self.colors["dim"])
        self.status_label.pack(anchor="w")

        self.feel_label = tk.Label(self.main_area, text="Conditions: ---", font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["dim"])
        self.feel_label.pack(anchor="w", pady=(5, 20))

        self.rain_label = tk.Label(self.main_area, text="Precipitation: --", font=("Helvetica", 10), bg=self.colors["bg"])
        self.rain_label.pack(anchor="w")
        self.hum_label = tk.Label(self.main_area, text="Humidity: --", font=("Helvetica", 10), bg=self.colors["bg"])
        self.hum_label.pack(anchor="w")
        self.wind_label = tk.Label(self.main_area, text="Wind: --", font=("Helvetica", 10), bg=self.colors["bg"])
        self.wind_label.pack(anchor="w")

        tk.Button(self.window, text="Use Current Location", command=self.get_weather_gps, relief="flat", fg=self.colors["dim"], bg="#ffffff").pack(pady=40)

    def on_focus_in(self, event):
        if self.city_entry.get() == self.placeholder:
            self.city_entry.delete(0, tk.END)
            self.city_entry.config(fg=self.colors["text"]) 

    def on_focus_out(self, event):
        if not self.city_entry.get():
            self.city_entry.insert(0, self.placeholder)
            self.city_entry.config(fg=self.colors["dim"]) 
    def toggle_temp(self):
        self.unit = "fahrenheit" if self.unit == "celsius" else "celsius"
        if self.last_data:
            self.update_ui(self.last_data, self.last_name)

    def get_weather(self):
        city = self.city_entry.get()
        if city == self.placeholder or not city: return
        try:
            geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
            if 'results' in geo:
                res = geo['results'][0]
                self.fetch_data(res['latitude'], res['longitude'], res['name'])
        except: messagebox.showerror("Error", "City not found")

    def get_weather_gps(self):
        g = geocoder.ip('me')
        if g.latlng: self.fetch_data(g.latlng[0], g.latlng[1], "Current Location")

    def fetch_data(self, lat, lon, name):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
            self.last_data = requests.get(url).json()
            self.last_name = name
            self.update_ui(self.last_data, name)
        except: messagebox.showerror("Error", "Data error")

    def update_ui(self, data, name):
        curr = data['current']
        temp_c = curr['temperature_2m']
        
        display_temp = round((temp_c * 9/5) + 32) if self.unit == "fahrenheit" else round(temp_c)
        symbol = "°F" if self.unit == "fahrenheit" else "°C"

        if temp_c <= 5: 
            color, status = self.colors["freezing"], "FREEZING"
        elif 5 < temp_c <= 13: 
            color, status = self.colors["cold"], "COLD"
        elif 13 < temp_c < 24: 
            color, status = self.colors["mild"], "MILD"
        elif 24 <= temp_c < 32: 
            color, status = self.colors["warm"], "WARM"
        else: 
            color, status = self.colors["hot"], "HOT"

        self.city_label.config(text=name.upper())
        self.temp_label.config(text=f"{display_temp}{symbol}")
        self.status_label.config(text=status, fg=color)
        self.hum_label.config(text=f"Humidity: {curr['relative_humidity_2m']}%")
        self.wind_label.config(text=f"Wind: {curr['wind_speed_10m']} km/h")
        self.rain_label.config(text=f"Precipitation: {curr['precipitation']} mm")
        
        codes = {0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast", 45: "Foggy", 61: "Rain", 95: "Storm"}
        self.feel_label.config(text=f"Conditions: {codes.get(curr['weather_code'], 'Variable')}")

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = WeatherAPI(root)
    root.mainloop()