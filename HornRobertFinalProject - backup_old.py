import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
import io
import urllib
from datetime import datetime

# Define the API key as a global constant
API_KEY = '2cdd9eebe6f14125bae205702233110'  # Replace with your actual API key

# Define colors for UI elements
DARK_BLUE = '#003366'
LIGHT_BLUE = '#add8e6'
WHITE = '#ffffff'
ORANGE = '#FFA500'

# Initialize the main application window
app = tk.Tk()
app.title("WeatherZip")
app.geometry("700x500")
app.configure(bg=DARK_BLUE)

# Set up the style for the notebook (tab control) and other elements
style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook.Tab', background=ORANGE, padding=[10, 2])
style.configure('TFrame', background=DARK_BLUE)
style.configure('TLabel', background=DARK_BLUE, foreground=WHITE)
style.configure('TButton', background=LIGHT_BLUE, foreground=WHITE)
style.configure('Exit.TButton', font=('Helvetica', 14))  # Style for a larger Exit button

# Configure tab styles for active and inactive states
style.configure('TNotebook.Tab', padding=[10, 2])
style.map('TNotebook.Tab',
          background=[('selected', ORANGE), ('!selected', LIGHT_BLUE)],  # Active tab orange, inactive tab light blue
          foreground=[('selected', WHITE), ('!selected', DARK_BLUE)])    # Text color white for active, dark blue for inactive

# Create the notebook (tab control) and add tabs
tab_control = ttk.Notebook(app)
current_tab = ttk.Frame(tab_control)
forecast_tab = ttk.Frame(tab_control)
tab_control.add(current_tab, text='Current Weather')
tab_control.add(forecast_tab, text='3 Day Forecast')
tab_control.pack(expand=1, fill="both")

# Add widgets to the current weather tab
tk.Label(current_tab, text="Enter Zip Code:", background=DARK_BLUE, foreground=WHITE).pack()
zip_code_entry = tk.Entry(current_tab, background=WHITE)
zip_code_entry.pack()
submit_button = tk.Button(current_tab, text="Get Weather", command=lambda: fetch_weather(zip_code_entry.get()), background=LIGHT_BLUE)
submit_button.pack()
weather_result_label = tk.Label(current_tab, text="", background=DARK_BLUE, foreground=WHITE)
weather_result_label.pack()
weather_icon_label = tk.Label(current_tab, background=DARK_BLUE)
weather_icon_label.pack()

# Set up the forecast tab layout
forecast_frame = tk.Frame(forecast_tab, background=DARK_BLUE)
forecast_frame.pack(side='top', fill='both', expand=True)

# Configure the exit button with the 'Exit.TButton' style from ttk, not tk
exit_button = ttk.Button(app, text="Exit", command=app.destroy, style='Exit.TButton')
exit_button.pack(side='bottom', pady=10, padx=10, ipadx=20, ipady=10)

# Function to fetch the current weather
def fetch_weather(zip_code):
    # API key and base URL for fetching weather data
    api_key = API_KEY # Call global API KEY
    base_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q="
    full_url = base_url + zip_code
    response = requests.get(full_url)

    # If response is successful, update the display with weather data
    if response.status_code == 200:
        weather_data = response.json()
        current = weather_data['current']
        location = weather_data['location']
        temp_f = current['temp_f']
        condition = current['condition']['text']
        feelslike_f = current['feelslike_f']
        name = location['name']
        region = location['region']
        country = location['country']
        icon_url = "https:" + current['condition']['icon']
        wind_mph = current['wind_mph']
        humidity = current['humidity']

        # Update the weather display
        update_weather_display(temp_f, condition, feelslike_f, name, region, country, icon_url, wind_mph, humidity)
        # Fetch the forecast as well
        fetch_forecast(zip_code)
    else:
        # Show error if weather data couldn't be retrieved
        messagebox.showerror("Error", "Failed to retrieve weather data")

# Function to update the weather display
def update_weather_display(temp, condition, feelslike, name, region, country, icon_url, wind, humidity):
    weather_result_label.config(text=f"Location: {name}, {region}, {country}\n"
                                     f"Temperature: {temp} °F\n"
                                     f"Feels Like: {feelslike} °F\n"
                                     f"Condition: {condition}\n"
                                     f"Wind: {wind} mph\n"
                                     f"Humidity: {humidity}%",
                                font=('Helvetica', 12, 'bold'))
    # Load and display the weather icon
    load_weather_icon(icon_url)

# Function to load and return the weather icon
def load_weather_icon(url):
    image_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    pil_image = Image.open(data_stream)
    tk_image = ImageTk.PhotoImage(pil_image)
    weather_icon_label.config(image=tk_image)
    weather_icon_label.image = tk_image

# Function to fetch the 3-day forecast
def fetch_forecast(zip_code):
    api_key = API_KEY # Call global API KEY
    forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={zip_code}&days=5"
    response = requests.get(forecast_url)

    # If response is successful, update the forecast display
    if response.status_code == 200:
        forecast_data = response.json()
        update_forecast_display(forecast_data)
    else:
        # Show error if forecast data couldn't be retrieved
        messagebox.showerror("Error", "Failed to retrieve forecast data")

# Function to update the forecast display
def update_forecast_display(weather_data):
    # Clear any existing widgets in the forecast frame
    for widget in forecast_frame.winfo_children():
        widget.destroy()

    forecast_data = weather_data['forecast']['forecastday']
    for index, day in enumerate(forecast_data):
        # Add separators between forecast entries
        if index > 0:
            ttk.Separator(forecast_frame, orient='vertical').pack(side='left', fill='y', pady=20)

        # Create a frame for each day's forecast
        day_frame = tk.Frame(forecast_frame, bg=DARK_BLUE)
        day_frame.pack(side='left', fill='both', expand=True, padx=10, pady=40)

        # Display the date, high and low temperatures, and condition
        date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%m.%d.%Y')
        tk.Label(day_frame, text=date, bg=DARK_BLUE, fg=WHITE, font=('Helvetica', 10)).pack()

        max_temp = day['day']['maxtemp_f']
        min_temp = day['day']['mintemp_f']
        condition = day['day']['condition']['text']
        forecast_text = f"High: {max_temp}°F\nLow: {min_temp}°F\n{condition}"
        tk.Label(day_frame, text=forecast_text, bg=DARK_BLUE, fg=WHITE, font=('Helvetica', 10)).pack()

        # Load and display the weather icon for the forecast
        icon_url = "https:" + day['day']['condition']['icon']
        image_label = load_forecast_icon(icon_url, day_frame)
        image_label.pack(side='top', pady=(5, 0))  # Position icon below the forecast text

# Function to load and return the forecast icon
def load_forecast_icon(url, frame):
    image_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    pil_image = Image.open(data_stream)
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label = tk.Label(frame, image=tk_image, bg=DARK_BLUE)
    image_label.image = tk_image
    return image_label

# Start the main application loop
app.mainloop()
