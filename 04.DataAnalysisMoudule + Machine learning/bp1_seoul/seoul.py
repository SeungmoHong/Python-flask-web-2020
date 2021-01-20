from flask import Blueprint, render_template, request, session, g
from flask import current_app
from datetime import timedelta
import os, json,folium
import pandas as pd
from my_util.weather import get_weather


seoul_bp = Blueprint('seoul_bp', __name__)


def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        current_app.logger.info("get new weather info")
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=60)
    return weather


seoulPark = pd.read_csv('./static/data/서울시 공원.csv')
@seoul_bp.before_app_first_request
def before_app_first_request():
    map = folium.Map(location=[37.5502, 126.982], zoom_start=10.5)
    for i in seoulPark.index:
        folium.CircleMarker([seoulPark.lat[i], seoulPark.lng[i]], 
                            tooltip=seoulPark['공원명'][i], radius= seoulPark['면적'][i]*0.000004,color='#3186cc', fill_color='#3186cc').add_to(map)
    map.save('./static/img/map1.html')

menu = {'ho':0, 'da':1, 'ml':0, 'se':1, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 'rg':0, 'cl':0}

@seoul_bp.route('/park', methods=['GET', 'POST'])
def park():
    seoulPark = pd.read_csv('./static/data/서울시 공원.csv')
    if request.method == 'GET':
        return render_template('seoul/seoulPark.html', menu=menu, weather=get_weather(), seoulPark=seoulPark)
    else:
        seoul = request.form['seoul']
        if seoul == 'gu' :
            park_gu = pd.read_csv('./static/data/서울시 공원분석2.csv')
            park_gu.set_index('지역', inplace=True)
            df = park_gu[park_gu.index == request.form["gu"]].reset_index()
            park_result = {'gu':df['지역'][0], 
                            'area':int(df['공원면적'][0]), 'm_area':int(park_gu['공원면적'].mean()),
                            'count':df['공원수'][0], 'm_count':round(park_gu['공원수'].mean(),1),
                            'area_ratio':round(df['공원면적비율'][0],2), 'm_area_ratio':round(park_gu['공원면적비율'].mean(),2),
                            'per_person':round(df['인당공원면적'][0],2), 'm_per_person':round(park_gu['인당공원면적'].mean(),2)}
            
            map = folium.Map(location=[seoulPark[seoulPark['구별']== request.form["gu"]]['lat'].mean(),
            seoulPark[seoulPark['구별']==request.form["gu"]]['lng'].mean()], zoom_start=13)
            for i in seoulPark[seoulPark['구별']==request.form["gu"]].index:
                folium.Marker([seoulPark.lat[i], seoulPark.lng[i]], popup=seoulPark['공원명'][i], tooltip=seoulPark['addr'][i]).add_to(map)
            park_count = len(seoulPark[seoulPark['구별']==request.form["gu"]].index)
            title_html = f'''
                        <h3 align="center" style="font-size:20px"><b>{request.form["gu"]}의 공원</b></h3>
                        '''
            map.get_root().html.add_child(folium.Element(title_html))
            map.save('./static/img/map.html')
            img_file = os.path.join(current_app.root_path, './static/img/map.html')
            mtime = int(os.stat(img_file).st_mtime)
            return render_template('seoul/guPark.html', menu=menu, weather=get_weather(), mtime=mtime, seoulPark=seoulPark, park_result= park_result, park_count = park_count)
        else:
            seoulPark.set_index('공원명',inplace=True)
            park = seoulPark.loc[request.form["park"]]
            map = folium.Map(location=[park.lat, park.lng], zoom_start=13)
            folium.Marker([park.lat, park.lng] , popup = park.name,
                                        tooltip=park.addr).add_to(map)
            map.save('./static/img/park.html')
            img_file = os.path.join(current_app.root_path, './static/img/park.html')
            mtime = int(os.stat(img_file).st_mtime)
            return render_template('seoul/parkInfo.html', menu=menu, weather=get_weather(), mtime=mtime , park=park)
@seoul_bp.route('/park_gu/<option>')
def park_gu_option(option):
    seoulPark = pd.read_csv('./static/data/서울시 공원.csv')
    park_gu = pd.read_csv('./static/data/서울시 공원분석2.csv', index_col= 0)
    geo_str = json.load(open('./static/data/skorea_municipalities_geo_simple.json',
                         encoding='utf8'))
    option_dict = {'area':'공원면적', 'count':'공원수', 'area_ratio':'공원면적 비율', 'per_person':'인당 공원면적'}
    column_index =option_dict[option].replace(' ','')
    map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')
    map.choropleth(geo_data = geo_str,
                       data = park_gu[column_index],
                       columns = [park_gu.index, park_gu[column_index]],
                       fill_color = 'PuRd',
                       key_on = 'feature.id')        
    seoulPark.set_index('공원명',inplace=True)
    for i in seoulPark.index:
        folium.CircleMarker([seoulPark.lat[i], seoulPark.lng[i]], 
                            radius= seoulPark['면적'][i]* 0.000002,
                            tooltip = i,
                            color='green', fill_color='green').add_to(map)
    html_file = os.path.join(current_app.root_path, 'static/img/park_gu.html')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)
    return render_template('seoul/park_gu.html', menu=menu, weather=get_weather(),
                            option=option, option_dict=option_dict, mtime=mtime)
@seoul_bp.route('/crime/<option>')
def crime_option(option):
    geo_str = json.load(open('./static/data/skorea_municipalities_geo_simple.json',
                         encoding='utf8'))
    df = pd.read_csv('./static/data/서울시5대범죄.csv', index_col=0)   
    option_dict = {'crime': '범죄','rape':'강간', 'rob':'강도', 'murder':'살인', 'thief':'절도', 'gang':'폭력',
    'crime_arrest': '검거','rape_arrest':'강간검거율', 'rob_arrest':'강도검거율', 'murder_arrest':'살인검거율', 'thief_arrest':'절도검거율', 'gang_arrest':'폭력검거율'}
    column_index =option_dict[option]
    if option.find('_arrest') > 0:
        fill_color = 'GnBu'
    else:
        fill_color = 'PuRd'
    map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')

    tmp_criminal = df[column_index] / df['인구수'] * 1000000
    map.choropleth(geo_data = geo_str,
                    data= tmp_criminal,
                    columns= [df.index, tmp_criminal],
                    fill_color= fill_color,
                    key_on='feature.id')

    p_df = pd.read_csv('./static/data/서울시경찰서.csv')
    for i in p_df.index:
        folium.Marker([p_df.lat[i], p_df.lng[i]], radius=10,
                            tooltip=p_df.name[i],
                            color='#3186cc', fill_color='#3186cc').add_to(map)
    html_file = os.path.join(current_app.root_path, 'static/img/crime.html')
    map.save(html_file)
    mtime = int(os.stat(html_file).st_mtime)
    return render_template('seoul/crime.html', menu=menu, weather=get_weather(),
                            option_dict=option_dict,option=option,mtime=mtime)

@seoul_bp.route('/cctv')
def cctv():
    result = pd.read_csv('./static/data/cctv.csv',index_col=0)
    return render_template('seoul/cctv.html', menu=menu, weather=get_weather(),result = result)

@seoul_bp.route('/cctv_table')
def table():
    result = pd.read_csv('./static/data/cctv.csv',index_col=0)
    result = result.round(2)
    result.reset_index(inplace=True)
    res = result[['구별','소계','최근증가율','인구수','내국인','외국인','고령자']]
    cols = list(res.columns)
    val = res.values
    return render_template('seoul/cctv_table.html', menu=menu, weather=get_weather(), res = res,cols = cols, val=val)