from flask import Flask, render_template, session, request
from bp5_stock.stock import stock_bp
from bp1_seoul.seoul import seoul_bp
import os, json, logging
from logging.config import dictConfig
import pandas as pd
import pandas_datareader as pdr
import matplotlib as mpl 
import matplotlib.pyplot as plt
import folium
# 한글폰트 사용
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)



from my_util.weather import get_weather
app = Flask(__name__)
app.secret_key = 'qwert12345'
kospi_dict, kosdaq_dict = {}, {}

with open('./logging.json', 'r') as file:
    config = json.load(file)
dictConfig(config)
app.logger

app.register_blueprint(stock_bp, url_prefix='/stock')
app.register_blueprint(seoul_bp, url_prefix='/seoul')

def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        app.logger.debug("get new weather info")
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)
    return weather

@app.before_first_request
def before_first_request():
    seoulPark = pd.read_csv('./static/data/서울시 공원.csv')
    map = folium.Map(location=[37.5502, 126.982], zoom_start=10.5)
    for i in seoulPark.index:
        folium.CircleMarker([seoulPark.lat[i], seoulPark.lng[i]], 
                            tooltip=seoulPark['공원명'][i], radius= seoulPark['면적'][i]*0.000004,color='#3186cc', fill_color='#3186cc').add_to(map)
    map.save('./static/img/map1.html')


    title_html = '<h3 align="center" style="font-size:20px"><b>자치구별 공원수</b></h3>'   
    map.get_root().html.add_child(folium.Element(title_html))
    map.save('./static/img/park_gu1.html')

@app.before_request
def before_request():
    pass    # 모든 Get 요청을 처리하는 놈에 앞서서 공통적으로 뭔 일을 처리함

@app.route('/', methods=['GET', 'POST'])
def index():
    menu = {'ho':1, 'da':0, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    return render_template('main.html', menu=menu, weather=get_weather_main())



if __name__ == '__main__':
    app.run(debug=True)