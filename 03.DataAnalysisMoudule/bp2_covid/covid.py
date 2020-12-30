from flask import Blueprint, render_template, request, session, g
from flask import current_app
from datetime import datetime, timedelta
from DB.db_module import *
import os, json,folium
import pandas as pd
import numpy as np
from my_util.weather import get_weather
import sqlite3

covid_bp = Blueprint('covid_bp', __name__)




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
@covid_bp.route('/bigcity', methods=['GET', 'POST'])
def bigcity():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    if request.method == 'GET': 
        rows = t_result()
        date = rows[0][1]
        return render_template('covid-19/bigcity.html', menu=menu, weather=get_weather(),rows= rows, date = date)
    else:
        date = request.form['date']
        rows = d_result(date)
        
        return render_template('covid-19/bigcity.html', menu=menu, weather=get_weather(),rows= rows, date = date)
        


@covid_bp.route('/daily' , methods=['GET', 'POST'])
def daily():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    if request.method == 'GET': 
        rows = day_result()
        return render_template('covid-19/day.html', menu=menu, weather=get_weather(),rows= rows)
    else :
        date = request.form['date']
        rows = d_day_result(date)
        return render_template('covid-19/day_res.html', menu=menu, weather=get_weather(),rows= rows)
@covid_bp.route('/age' , methods=['GET', 'POST'])
def age():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    if request.method == 'GET': 
        rows = age_result()
        return render_template('covid-19/age.html', menu=menu, weather=get_weather(),rows= rows)
    else :
        date = request.form['date']
        rows = d_age_result(date)
        
        return render_template('covid-19/age.html', menu=menu, weather=get_weather(),rows= rows)

@covid_bp.route('/sex' , methods=['GET', 'POST'])
def sex():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    if request.method == 'GET': 
        rows = sex_result()[9:]
        return render_template('covid-19/sex.html', menu=menu, weather=get_weather(),rows= rows)
    else :
        date = request.form['date']
        rows = d_sex_result(date)[9:]
        
        return render_template('covid-19/sex.html', menu=menu, weather=get_weather(),rows= rows, date= date)

@covid_bp.route('/seoul')
def seoul():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    rows = seoul_data()
    df = pd.DataFrame(rows, columns=['연번','확진일','지역','접촉력'])
    date = df['확진일'][df.index[-1]]
    df['지역'][df['지역'] == ''] = np.nan
    df['확진월'] = df['확진일'].apply(lambda r: r.split('-')[1] + '월' )
    df['확진자'] = 1
    pdf1 = pd.pivot_table(df,               
                    index = '지역',    
                    columns = '확진월',  
                    values = '확진자',   
                    aggfunc = 'sum')
    pdf1.fillna(0,inplace=True)
    pdf1.loc['기타'] = pdf1.loc['기타'] + pdf1.loc['타시도']
    pdf1.drop('타시도', inplace=True)
    pdf1.loc['합계'] = pdf1.sum(axis=0)
    pdf1 = pdf1.astype(int)
    c_d = df.pivot_table('연번', '지역', aggfunc='count')
    c_d.rename({'연번':'확진자수'},axis=1, inplace=True)
    geo_path = './static/data/skorea_municipalities_geo_simple.json'
    geo_data = json.load(open(geo_path, encoding='utf-8'))
    gu_df = pd.read_csv('./static/data/서울구청리스트.csv',index_col=0)
    gu_df.set_index('지역',inplace=True)
    gu_df.index =  gu_df.index.str.replace('청','')
    map = folium.Map(location=[37.5502, 126.982], zoom_start=10, tiles= 'Stamen Toner')
    map.choropleth(geo_data = geo_data,
    data= c_d['확진자수'],
    columns= [c_d.index, c_d['확진자수']],
    fill_color= 'PuRd',
    key_on='feature.id')
    map.save('static/img/seoul.html')
    img_file = os.path.join(current_app.root_path, './static/img/seoul.html')
    mtime = int(os.stat(img_file).st_mtime)
    c_d.loc['기타'] = c_d.loc['기타'] + c_d.loc['타시도']
    c_d.drop('타시도',inplace=True)
    c_d.reset_index(inplace=True)
    month = list(pdf1.columns)
    total = list(pdf1.loc['합계'])
   
    return render_template('covid-19/seoul.html', menu=menu, weather=get_weather(),mtime = mtime, c_d = c_d, date = date, month=month, total=total)

@covid_bp.route('/seoul/<gu>')
def seoul_gu(gu):
    gu = gu
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'st':0, 'wc':0}
    rows = seoul_data()
    df = pd.DataFrame(rows, columns=['연번','확진일','지역','접촉력'])
    df['확진월'] = df['확진일'].apply(lambda r: r.split('-')[1] + '월' )
    df['확진자'] = 1
    pdf1 = pd.pivot_table(df,               
                    index = '지역',    
                    columns = '확진월',  
                    values = '확진자',   
                    aggfunc = 'sum')
    pdf1.fillna(0,inplace=True)
    pdf1.loc['기타'] = pdf1.loc['기타'] + pdf1.loc['타시도']
    pdf1.drop('타시도', inplace=True)
    pdf1.loc['합계'] = pdf1.sum(axis=0)
    pdf1 = pdf1.astype(int)
    month = list(pdf1.columns)
    count = list(pdf1.loc[gu])
    history = df[df['지역'] == gu].pivot_table('연번','접촉력',aggfunc="count")
    his_name = list(history.sort_values(by='연번', ascending=False).head(10).index)
    his_count = list(history.sort_values(by='연번', ascending=False).head(10)['연번'])
    d_day = df[df['지역'] == '강서구'].pivot_table('연번','확진일',aggfunc="count")
    ten_day = d_day.sort_values(by='확진일', ascending=False).head(10)
    ten_day = d_day.sort_values(by='확진일', ascending=False).head(10)
    ten_date = list(ten_day.index)[::-1]
    ten_val = list(ten_day['연번'].values)
    
    return render_template('covid-19/seoul_gu.html', menu=menu, weather=get_weather(),
     month=month, count=count, gu =gu, his_name = his_name, his_count = his_count, ten_date=ten_date, ten_val=ten_val)
