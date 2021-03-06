from flask import Flask, render_template, session, request
from fbprophet import Prophet
from datetime import datetime, timedelta
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
    kospi = pd.read_csv('./static/data/KOSPI.csv', dtype={'종목코드': str})
    for i in kospi.index:
        kospi_dict[kospi['종목코드'][i]] = kospi['종목명'][i]
    kosdaq = pd.read_csv('./static/data/KOSDAQ.csv', dtype={'종목코드': str})
    for i in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['종목명'][i]
    seoulPark = pd.read_csv('./static/data/서울시 공원.csv')
    map = folium.Map(location=[37.5502, 126.982], zoom_start=10.5)
    for i in seoulPark.index:
        folium.CircleMarker([seoulPark.lat[i], seoulPark.lng[i]], 
                            tooltip=seoulPark['공원명'][i], radius= seoulPark['면적'][i]*0.000004,color='#3186cc', fill_color='#3186cc').add_to(map)
    map.save('./static/img/map1.html')



@app.before_request
def before_request():
    pass    # 모든 Get 요청을 처리하는 놈에 앞서서 공통적으로 뭔 일을 처리함

@app.route('/', methods=['GET', 'POST'])
def index():
    menu = {'ho':1, 'da':0, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    return render_template('main.html', menu=menu, weather=get_weather_main())

@app.route('/seoul/park', methods=['GET', 'POST'])
def park():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    seoulPark = pd.read_csv('./static/data/서울시 공원.csv')
    if request.method == 'GET':
        return render_template('seoulPark.html', menu=menu, weather=get_weather_main(), seoulPark=seoulPark)
    else:
        seoul = request.form['seoul']
        if seoul == 'gu' :
            map = folium.Map(location=[seoulPark[seoulPark['구별']== request.form["gu"]]['lat'].mean(),
            seoulPark[seoulPark['구별']==request.form["gu"]]['lng'].mean()], zoom_start=13)
            for i in seoulPark[seoulPark['구별']==request.form["gu"]].index:
                folium.Marker([seoulPark.lat[i], seoulPark.lng[i]], popup=seoulPark['공원명'][i], tooltip=seoulPark['addr'][i]).add_to(map)
                                    
            title_html = f'''
                        <h3 align="center" style="font-size:20px"><b>{request.form["gu"]}의 공원</b></h3>
                        '''
            map.get_root().html.add_child(folium.Element(title_html))
            map.save('./static/img/map.html')
            img_file = os.path.join(app.root_path, './static/img/map.html')
            mtime = int(os.stat(img_file).st_mtime)
            return render_template('guPark.html', menu=menu, weather=get_weather_main(), mtime=mtime, seoulPark=seoulPark)
        else:
            seoulPark.set_index('공원명',inplace=True)
            park = seoulPark.loc[request.form["park"]]
            map = folium.Map(location=[park.lat, park.lng], zoom_start=13)
            folium.Marker([park.lat, park.lng] , popup = park.name,
                                        tooltip=park.addr).add_to(map)
            map.save('./static/img/park.html')
            img_file = os.path.join(app.root_path, './static/img/park.html')
            mtime = int(os.stat(img_file).st_mtime)
            return render_template('parkInfo.html', menu=menu, weather=get_weather_main(), mtime=mtime , park=park)
@app.route('/seoul/park_gu/<option>')
def park_gu_option(option):
    menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    seoulPark = pd.read_csv('./static/data/서울시 공원.csv')
    park_gu = pd.read_csv('./static/data/서울시 공원분석.csv', index_col= 0)
    geo_str = json.load(open('./static/data/skorea_municipalities_geo_simple.json',
                         encoding='utf8'))
    map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')
    if option == 'area':
        map.choropleth(geo_data = geo_str,
                       data = park_gu['공원의면적'],
                       columns = [park_gu.index, park_gu['공원의면적']],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')
    elif option == 'count':
        map.choropleth(geo_data = geo_str,
                       data = park_gu['공원의수'],
                       columns = [park_gu.index, park_gu['공원의수']],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')
    elif option == 'area_ratio':
        map.choropleth(geo_data = geo_str,
                       data = (park_gu['공원의면적']/park_gu['공원의수']),
                       columns = [park_gu.index, (park_gu['공원의면적']/park_gu['공원의수'])],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')
    elif option == 'per_person':
        map.choropleth(geo_data = geo_str,
                       data = (park_gu['공원의면적']/ park_gu['인구수']),
                       columns = [park_gu.index, (park_gu['공원의면적']/ park_gu['인구수'])],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')             
    seoulPark.set_index('공원명',inplace=True)
    for i in seoulPark.index:
        folium.CircleMarker([seoulPark.lat[i], seoulPark.lng[i]], 
                            radius= seoulPark['면적'][i]*0.000002,
                            tooltip = i,
                            color='green', fill_color='green').add_to(map)
    html_file = os.path.join(app.root_path, 'static/img/park_gu.html')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)
    option_dict = {'area':'공원면적', 'count':'공원수', 'area_ratio':'공원면적 비율', 'per_person':'인당 공원면적'}
    return render_template('park_gu.html', menu=menu, weather=get_weather_main(),
                            option=option, option_dict=option_dict, mtime=mtime)
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':1, 'wc':0}
    if request.method == 'GET':
        return render_template('stock.html', menu=menu, weather=get_weather_main(),
                                kospi=kospi_dict, kosdaq=kosdaq_dict)
    else:
        market = request.form['market']
        if market == 'KS':
            code = request.form['kospi_code']
            company = kospi_dict[code]
            code += '.KS'
        else:
            code = request.form['kosdaq_code']
            company = kosdaq_dict[code]
            code += '.KQ'
        learn_period = int(request.form['learn'])
        pred_period = int(request.form['pred'])
        today = datetime.now()
        start_learn = today - timedelta(days=learn_period*365)
        end_learn = today - timedelta(days=1)

        stock_data = pdr.DataReader(code, data_source='yahoo', start=start_learn, end=end_learn)
        app.logger.debug(f"get stock data: {code}")
        df = pd.DataFrame({'ds': stock_data.index, 'y': stock_data.Close})
        df.reset_index(inplace=True)
        del df['Date']

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=pred_period)
        forecast = model.predict(future)

        fig = model.plot(forecast);
        img_file = os.path.join(app.root_path, 'static/img/stock.png')
        fig.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('stock_res.html', menu=menu, weather=get_weather_main(), 
                                mtime=mtime, company=company, code=code)

if __name__ == '__main__':
    app.run(debug=True)