#!/bin/python

'''
pip install geopy
pip install rich_pixels
pip install rich
pip install tabulate
'''

from geopy.geocoders import Nominatim
import json
import os
from PIL import Image
from rich.console import Console
from rich_pixels import Pixels
from rich_pixels._renderer import HalfcellRenderer
import requests
from tabulate import tabulate

print('''
__________             .___                    ___________                   
\______   \_____     __| _/____ _______        \__    ___/__________  _____  
 |       _/\__  \   / __ |\__  \\\_  __ \  ______ |    |_/ __ \_  __ \/     \ 
 |    |   \ / __ \_/ /_/ | / __ \|  | \/ /_____/ |    |\  ___/|  | \/  Y Y  \\
 |____|_  /(____  /\____ |(____  /__|            |____| \___  >__|  |__|_|  /
        \/      \/      \/     \/                           \/            \/ 
''')

os.system('')
gl = Nominatim(user_agent='radar-term')
console = Console()
files = []

# Prompt for zip code.
while True:
    zip = input('Enter your zip code (q to quit): ')

    #Validate input.
    if zip.lower() == 'q':
        break
    elif len(zip) > 5 or len(zip) < 5:
        print('Must be 5 digits. Try again.')
    elif zip.isdigit() is False:
        print('Must enter numbers only. Try again.')
    else:

        # Convert zip into lat, lon
        loc = gl.geocode(zip, country_codes='us')
        if loc == None:
            print('Invalid zip code. Try again.')
            continue
        lat = loc.latitude
        lon = loc.longitude

        # Get local radar station
        nws_url = 'https://api.weather.gov'

        response = requests.get(f'{nws_url}/points/{lat},{lon}').json()
        radar_stn = response['properties']['radarStation']
        wfo = response['properties']['gridId']
        forecast_url = response['properties']['forecast']

        # Get radar image
        radar_url = f'https://radar.weather.gov/ridge/standard/{radar_stn}_0.gif'
        response = requests.get(radar_url)

        with open('radar.gif', 'wb') as f:
            f.write(response.content)
                
        # Convert GIF to ANSI
        width, height = os.get_terminal_size()
        renderer = HalfcellRenderer()

        with Image.open('radar.gif', 'r') as image_png:
            x, y = image_png.size
            ratio = (x / y)
            height = int(ratio * width)
            image_ansi = Pixels.from_image(image_png, resize=(width, height), renderer=renderer)
            console.print(image_ansi)

        # Get forecast
        response = requests.get(forecast_url).json()

        # Parse forecast data
        names = []
        temps = []
        pops = []
        table1 = [[], [], []]
        table2 = [[], [], []]

        for period in response['properties']['periods']:
            if len(table1[0]) < 7:
                table1[0].append(period['name'])
                table1[1].append(period['temperature'])
                table1[2].append(period['probabilityOfPrecipitation']['value'])
            else:
                table2[0].append(period['name'])
                table2[1].append(period['temperature'])
                table2[2].append(period['probabilityOfPrecipitation']['value'])
        
        # Display forecast
        rowIDs = ['Temp', 'PoP']
        print(tabulate(table1, headers='firstrow', tablefmt='grid', showindex=rowIDs, 
                       stralign='center', numalign='center'))
        print(tabulate(table2, headers='firstrow', tablefmt='grid', showindex=rowIDs, 
                       stralign='center', numalign='center'))
        
        # Clean up
        os.remove('radar.gif')
