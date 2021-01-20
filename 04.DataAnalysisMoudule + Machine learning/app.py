from flask import Flask, render_template, session, request
from bp1_seoul.seoul import seoul_bp
from bp2_covid.covid import covid_bp
from bp3_catogram.carto import carto_bp
from bp4_crawling.crawling import crawling_bp
from bp5_wordcloud.wc import wc_bp
from bp6_classification.classification import cf_bp
import os, json, logging ,sqlite3
from logging.config import dictConfig
from datetime import timedelta
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import pandas_datareader as pdr
import matplotlib as mpl 
import matplotlib.pyplot as plt
import folium
# 한글폰트 사용
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)
from my_util.weather import get_weather
from DB.db_update import daily_update

app = Flask(__name__)
app.secret_key = 'qwert12345'
app.config['SESSION_COOKIE_PATH'] = '/'

app.register_blueprint(seoul_bp, url_prefix='/seoul')
app.register_blueprint(covid_bp, url_prefix='/covid-19')
app.register_blueprint(carto_bp, url_prefix='/cartogram')
app.register_blueprint(crawling_bp, url_prefix='/crawling')
app.register_blueprint(wc_bp, url_prefix='/wordcloud')
app.register_blueprint(cf_bp, url_prefix='/classification')

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

@app.before_first_request
def before_first_request():
    today = datetime.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute('select * from "시도발생_현황"')
    rows = cur.fetchall()
    conn.close()
    data_time = rows[-1][1]
    if data_time != today:
        key_fd = open('./과제data/gov_data_api_key.txt', mode='r')
        govapi_key = key_fd.read(100)
        key_fd.close()
        start_date = str(int(data_time.replace('-','')) +1)
        end_date = datetime.today().strftime("%Y%m%d")
        corona_url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
        url = f'{corona_url}?ServiceKey={govapi_key}&pageNo=1&numOfRows=10&startCreateDt={start_date}&endCreateDt={end_date}'
        result = requests.get(url)
        soup = BeautifulSoup(result.text, 'xml')
        if int(soup.find('totalCount').string) != 0:
            daily_update(start_date)


        


@app.before_request
def before_request():
    pass    # 모든 Get 요청을 처리하는 놈에 앞서서 공통적으로 뭔 일을 처리함

@app.route('/')
def index():
    menu = {'ho':1, 'da':0, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 'rg':0, 'cl':0}
    return render_template('main.html', menu=menu, weather=get_weather())



if __name__ == '__main__':
    app.run(debug=True)