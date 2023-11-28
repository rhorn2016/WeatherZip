'''
WeatherZip: 
    Your Local Forecast at a Glance
    Description: WeatherZip is a user-friendly application that provides 
    current weather updates and a 3-day forecast based on the user's zip 
    code input, complete with temperature, conditions, and weather icons

Date: 11/18/2023
Author: Robert Horn
'''

# Import required libraries and modules
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
import io
import urllib
from datetime import datetime

# Define the API key as a global constant
API_KEY = '2cdd9eebe6f14125bae205702233110'

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

# Set up the style for the UI elements
style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook.Tab', background=ORANGE, padding=[10, 2])
style.configure('TFrame', background=DARK_BLUE)
style.configure('TLabel', background=DARK_BLUE, foreground=WHITE)
style.configure('TButton', background=LIGHT_BLUE, foreground=WHITE)
style.configure('Exit.TButton', font=('Helvetica', 14))
style.configure('TNotebook.Tab', padding=[10, 2])

# Configure tab styles for active and inactive states
style.map('TNotebook.Tab',
          background=[('selected', ORANGE), ('!selected', LIGHT_BLUE)],
          foreground=[('selected', WHITE), ('!selected', DARK_BLUE)])

# Create and configure the tab control with three tabs
tab_control = ttk.Notebook(app)
current_tab = ttk.Frame(tab_control)
forecast_tab = ttk.Frame(tab_control)
widget_tab = ttk.Frame(tab_control)
tab_control.add(current_tab, text='Current Weather')
tab_control.add(forecast_tab, text='3 Day Forecast')
tab_control.add(widget_tab, text='Widget')
tab_control.pack(expand=1, fill="both")

# Add input and output elements to the current weather tab
tk.Label(current_tab, text="Enter Zip Code:", background=DARK_BLUE, foreground=WHITE).pack()
zip_code_entry = tk.Entry(current_tab, background=WHITE)
zip_code_entry.pack()
submit_button = tk.Button(current_tab, text="Get Weather", command=lambda: fetch_weather(zip_code_entry.get()), background=LIGHT_BLUE)
submit_button.pack()
weather_result_label = tk.Label(current_tab, text="", background=DARK_BLUE, foreground=WHITE)
weather_result_label.pack()
weather_icon_label = tk.Label(current_tab, background=DARK_BLUE)
weather_icon_label.pack()

# Configure the forecast tab layout
forecast_frame = tk.Frame(forecast_tab, background=DARK_BLUE)
forecast_frame.pack(side='top', fill='both', expand=True)

# Configure the exit button
exit_button = ttk.Button(app, text="Exit", command=app.destroy, style='Exit.TButton')
exit_button.pack(side='bottom', pady=10, padx=10, ipadx=20, ipady=10)

# Global variable for storing weather data
weather_data_global = {}


# Function to load and return the forecast icon
def load_forecast_icon(url, frame):
    # Code to fetch, convert, and display an image from a URL
    image_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    pil_image = Image.open(data_stream)
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label = tk.Label(frame, image=tk_image, bg=DARK_BLUE)
    image_label.image = tk_image 
    return image_label


# Function to fetch the current weather from an API
def fetch_weather(zip_code):
    # Code to make an API request and process the response
    global weather_data_global
    api_key = API_KEY
    base_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q="
    full_url = base_url + zip_code
    response = requests.get(full_url)

    if response.status_code == 200:
        weather_data = response.json()
        weather_data_global = weather_data
        update_weather_display(weather_data['current'])
        fetch_forecast(zip_code)  # This will call update_forecast_display
    else:
        messagebox.showerror("Error", "Failed to retrieve weather data")


# Function to update the weather display
def update_weather_display(current):
    # Code to update the UI with the current weather data
    location = weather_data_global['location']
    weather_result_label.config(text=f"Location: {location['name']}, {location['region']}, {location['country']}\n"
                                     f"Temperature: {current['temp_f']} °F\n"
                                     f"Feels Like: {current['feelslike_f']} °F\n"
                                     f"Condition: {current['condition']['text']}\n"
                                     f"Wind: {current['wind_mph']} mph\n"
                                     f"Humidity: {current['humidity']}%",
                                font=('Helvetica', 12, 'bold'))
    load_weather_icon("https:" + current['condition']['icon'])


# Function to load and return the weather icon
def load_weather_icon(url):
    # Similar code to load_forecast_icon, for loading the current weather icon
    image_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    pil_image = Image.open(data_stream)
    tk_image = ImageTk.PhotoImage(pil_image)
    weather_icon_label.config(image=tk_image)
    weather_icon_label.image = tk_image  # Keep a reference


# Function to fetch the 3-day forecast from an API
def fetch_forecast(zip_code):
    # Code to make an API request for the forecast and process the response
    global weather_data_global
    api_key = API_KEY
    forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={zip_code}&days=3"
    response = requests.get(forecast_url)

    if response.status_code == 200:
        forecast_data = response.json()
        weather_data_global['forecast'] = forecast_data['forecast']  # Update the forecast part of the global variable
        update_forecast_display(forecast_data['forecast'])
    else:
        messagebox.showerror("Error", "Failed to retrieve forecast data")


# Function to update the forecast display
def update_forecast_display(forecast):
    # Code to update the UI with the forecast data
    for widget in forecast_frame.winfo_children():
        widget.destroy()

    for index, day in enumerate(forecast['forecastday']):
        if index > 0:
            ttk.Separator(forecast_frame, orient='vertical').pack(side='left', fill='y', pady=20)

        day_frame = tk.Frame(forecast_frame, bg=DARK_BLUE)
        day_frame.pack(side='left', fill='both', expand=True, padx=10, pady=40)

        date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%m.%d.%Y')
        tk.Label(day_frame, text=date, bg=DARK_BLUE, fg=WHITE, font=('Helvetica', 10)).pack()

        max_temp = day['day']['maxtemp_f']
        min_temp = day['day']['mintemp_f']
        condition = day['day']['condition']['text']
        forecast_text = f"High: {max_temp}°F\nLow: {min_temp}°F\n{condition}"
        tk.Label(day_frame, text=forecast_text, bg=DARK_BLUE, fg=WHITE, font=('Helvetica', 10)).pack()

        icon_url = "https:" + day['day']['condition']['icon']
        image_label = load_forecast_icon(icon_url, day_frame)
        image_label.pack(side='top', pady=(5, 0))

    create_weather_widget(widget_tab)  # Update the widget tab with the new forecast data


# Function to create the weather widget
def create_weather_widget(parent):
    # Code to create and update the weather widget in the UI
    global weather_data_global
    for widget in parent.winfo_children():
        widget.destroy()

    if not weather_data_global:
        return  # If not, simply return without creating the widget

    current = weather_data_global['current']
    location = weather_data_global['location']
    forecast = weather_data_global['forecast']['forecastday']

    # Main widget frame
    widget_frame = tk.Frame(parent, bg='lightblue', relief='raised', bd=2)
    widget_frame.pack(expand=True, fill='both', padx=10, pady=10)

    # City label at the top
    city_label = tk.Label(widget_frame, text=location['name'], bg='lightblue', font=('Helvetica', 16, 'bold'))
    city_label.pack(side='top')

    # Current condition and temperature in the middle
    middle_frame = tk.Frame(widget_frame, bg='lightblue')
    middle_frame.pack(expand=True, fill='both')

    condition_label = tk.Label(middle_frame, text=current['condition']['text'], bg='lightblue', font=('Helvetica', 12))
    condition_label.pack(side='top')

    temperature_label = tk.Label(middle_frame, text=f"{current['temp_f']} °F", bg='lightblue', font=('Helvetica', 30, 'bold'))
    temperature_label.pack(side='top')

    # Icon on the left of the temperature
    icon_image = load_icon_image("https:" + current['condition']['icon'])
    icon_label = tk.Label(middle_frame, image=icon_image, bg='lightblue')
    icon_label.image = icon_image
    icon_label.pack(side='top')

    # Frame for the forecast at the bottom
    days_frame = tk.Frame(widget_frame, bg='lightblue')
    days_frame.pack(side='bottom')

    # Forecast for each day, arranged from left to right
    for day_data in forecast:
        date = datetime.strptime(day_data['date'], '%Y-%m-%d')
        day_of_week = date.strftime('%a')

        day_frame = tk.Frame(days_frame, bg='lightblue')
        day_frame.pack(side='left', padx=5)

        tk.Label(day_frame, text=day_of_week, bg='lightblue').pack()

        forecast_icon_image = load_icon_image("https:" + day_data['day']['condition']['icon'])
        forecast_icon_label = tk.Label(day_frame, image=forecast_icon_image, bg='lightblue')
        forecast_icon_label.image = forecast_icon_image
        forecast_icon_label.pack()

        tk.Label(day_frame, text=f"{day_data['day']['maxtemp_f']} °F", bg='lightblue').pack()
        

# Helper function to load an image from a URL
def load_icon_image(url):
    # Similar code to load_forecast_icon and load_weather_icon
    image_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    pil_image = Image.open(data_stream)
    tk_image = ImageTk.PhotoImage(pil_image)
    return tk_image


# Call to create the initial weather widget
create_weather_widget(widget_tab)

# Start the main application loop
app.mainloop()
