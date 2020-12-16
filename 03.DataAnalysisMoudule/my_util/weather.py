from urllib.parse import urlparse
import requests
import pandas as pd
key_fd = open('openweatherapikey.txt', mode='r')
oweather_key = key_fd.read(100)
key_fd.close()
def get_weather():
    lat = 37.550966
    lng = 126.849532
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={oweather_key}&units=metric&lang=kr'
    results = requests.get(urlparse(url).geturl()).json()
    icon = results['weather'][0]['icon']
    desc = results['weather'][0]['description']
    temp = results['main']['temp']
    temp = round(float(temp)+0.01, 1)
    temp_min = results['main']['temp_min']
    temp_max = results['main']['temp_max']
    return f' <img src="http://openweathermap.org/img/wn/{icon}@2x.png?q=1" height="32"> <strong>{desc}</strong> 온도: <strong>{temp}</strong>, {temp_min}/{temp_max}&#8451'