from flask import Flask, render_template, session, request
from bp1_seoul.seoul import seoul_bp
from bp3_catogram.carto import carto_bp
from bp5_stock.stock import stock_bp
from bp6_wordcloud.wc import wc_bp
import os, json, logging
from logging.config import dictConfig
from datetime import timedelta
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
app.config['SESSION_COOKIE_PATH'] = '/'

app.register_blueprint(seoul_bp, url_prefix='/seoul')
app.register_blueprint(carto_bp, url_prefix='/cartogram')
app.register_blueprint(stock_bp, url_prefix='/stock')
app.register_blueprint(wc_bp, url_prefix='/wordcloud')

with open('./logging.json', 'r') as file:
    config = json.load(file)
dictConfig(config)
app.logger


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


@app.before_request
def before_request():
    pass    # 모든 Get 요청을 처리하는 놈에 앞서서 공통적으로 뭔 일을 처리함

@app.route('/')
def index():
    menu = {'ho':1, 'da':0, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    return render_template('main.html', menu=menu, weather=get_weather_main())



if __name__ == '__main__':
    app.run(debug=True)