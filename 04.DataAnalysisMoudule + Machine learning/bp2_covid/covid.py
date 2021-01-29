from flask import Blueprint, render_template, request, session, g, redirect, flash, url_for
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
menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':1, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 'rg':0, 'cl':0}
@covid_bp.route('/bigcity', methods=['GET', 'POST'])
def bigcity():
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
    if request.method == 'GET': 
        # rows = day_result()
        # return render_template('covid-19/day.html', menu=menu, weather=get_weather(),rows= rows)
        rows = all_result()
        df1 = pd.DataFrame(rows)
        pt = df1.pivot_table(index=1, columns=2, values=5)[-7:]
        pt = pt.astype(int)
        pt.sort_index(ascending=False,inplace=True)
        pt.reset_index(inplace=True)
        rows = pt.values
        return render_template('covid-19/day.html', menu=menu, weather=get_weather(),rows= rows)
    else :
        date = request.form['date']
        rows = d_result(date)
        df1 = pd.DataFrame(rows)
        pt = df1.pivot_table(index=1, columns=2, values=5)
        pt = pt.astype(int)
        pt.sort_index(ascending=False,inplace=True)
        pt.reset_index(inplace=True)
        rows = pt.values
        return render_template('covid-19/day_res.html', menu=menu, weather=get_weather(),rows= rows)
@covid_bp.route('/age' , methods=['GET', 'POST'])
def age():
    if request.method == 'GET': 
        rows = age_result()
        return render_template('covid-19/age.html', menu=menu, weather=get_weather(),rows= rows)
    else :
        date = request.form['date']
        rows = d_age_result(date)
        
        return render_template('covid-19/age.html', menu=menu, weather=get_weather(),rows= rows)

@covid_bp.route('/sex' , methods=['GET', 'POST'])
def sex():
    if request.method == 'GET': 
        rows = sex_result()[9:]
        return render_template('covid-19/sex.html', menu=menu, weather=get_weather(),rows= rows)
    else :
        date = request.form['date']
        rows = d_sex_result(date)[9:]
        
        return render_template('covid-19/sex.html', menu=menu, weather=get_weather(),rows= rows, date= date)

@covid_bp.route('/seoul')
def seoul():
    rows = seoul_data()
    df = pd.DataFrame(rows, columns=['연번','확진일','지역','접촉력'])
    date = df['확진일'][df.index[-1]]
    df['지역'][df['지역'] == ''] = np.nan
    df['확진월'] = df['확진일'].apply(lambda r:r.split('-')[0]+'-' + r.split('-')[1] )
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
    rows = seoul_data()
    df = pd.DataFrame(rows, columns=['연번','확진일','지역','접촉력'])
    df['확진월'] = df['확진일'].apply(lambda r: r.split('-')[0]+ '-' + r.split('-')[1]  )
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
    d_day = df[df['지역'] == gu].pivot_table('연번','확진일',aggfunc="count")
    ten_day = d_day.sort_values(by='확진일', ascending=False).head(10)
    ten_day = d_day.sort_values(by='확진일', ascending=False).head(10)
    ten_date = list(ten_day.index)[::-1]
    ten_val = list(ten_day['연번'].values)
    
    return render_template('covid-19/seoul_gu.html', menu=menu, weather=get_weather(),
     month=month, count=count, gu =gu, his_name = his_name, his_count = his_count, ten_date=ten_date, ten_val=ten_val)


@covid_bp.route('/bigcity_chart' , methods=['GET', 'POST'])
def bigcity_chart():
    if request.method == 'GET': 
        area = ['합계', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원',
       '충북', '충남', '전북', '전남', '경북', '경남', '제주', '검역']
        month = ['2020년 03월','2020년 04월','2020년 05월','2020년 06월','2020년 07월','2020년 08월','2020년 09월','2020년 10월','2020년 11월','2020년 12월','2021년 01월']
        
        return render_template('covid-19/makechart.html', menu=menu, weather=get_weather(), area = area , month = month)
        
    else :
        color_list = ["red","violet","green","blue","orange","purple","hotpink","aqua","lime","navy","darkred","indigo","magenta","orangered","royalblue","yellow","brown","blue"]
        data = request.form['data']
        
        sido_data_dict = {'확진자' : 3,'사망자' : 4, '전일대비' : 5,'격리해제' : 6, '격리중' : 7, '지역발생' : 8, '해외유입' : 9, '10만명당 확진자' : 10}
        sido_data = sido_data_dict[request.form['sido_data']]
        area = request.form.getlist('area_data')
        count = len(area)
        if count == 0 :
            flash('지역을 체크하지 않았습니다.', 'danger')
            return redirect(url_for('covid_bp.bigcity_chart'))

        if request.form['date'] == 'day':
            s_date = request.form['s_date']
            e_date = request.form['e_date']
            if int(s_date.replace('-','')) > int(e_date.replace('-','')) :
                flash('날짜를 확인해 주세요.', 'danger')
                return redirect(url_for('covid_bp.bigcity_chart'))
            rows = t_chart(data,s_date,e_date)
            df1 = pd.DataFrame(rows)
            chart_df = df1.pivot_table(index=2, columns=1, values=sido_data, aggfunc='sum')
        else:
            s_date = request.form['s_mon']
            e_date = request.form['e_mon']
            if int(s_date.replace('년 ','').replace('월','')) > int(e_date.replace('년 ','').replace('월','')) :
                flash('날짜를 확인해 주세요.', 'danger')
                return redirect(url_for('covid_bp.bigcity_chart'))
            s_mon = request.form['s_mon'][:-1].replace('년 ','-') + '-01'
            e_mon = request.form['e_mon'][:-1].replace('년 ','-') + '-31'
            rows = t_chart(data,s_mon,e_mon)
            df1 = pd.DataFrame(rows)
            df1['확진월'] = df1[1].apply(lambda r: r.split('-')[0] + '년' + r.split('-')[1] + '월' )
            chart_df = df1.pivot_table(index=2, columns='확진월', values=sido_data, aggfunc='max')
        
        
        label = list(chart_df.columns)
        val = chart_df.loc[area].values.tolist()
        chart_list = [] 
        for i in range(count):
            cha = f''' "label" : "{area[i]}", "data" : {val[i]}, "fill":false,"borderColor":"{color_list[i]}","lineTension":0.1 '''
            cha = '{' + cha + '}'
            chart_list.append(cha)
        return render_template('covid-19/makechart_res.html', menu=menu, weather=get_weather(), label=label, val = val, area= area, count = count, chart_list=chart_list, sido_data=request.form['sido_data'], s_date=s_date, e_date=e_date)
        
        
@covid_bp.route('/seoul_chart' , methods=['GET', 'POST'])
def seoul_chart():
    if request.method == 'GET': 
        area = ['강서구', '마포구', '중랑구', '종로구', '성북구', '송파구', '서대문구', '성동구',
       '강남구', '서초구', '구로구', '강동구', '관악구', '은평구', '노원구', '동작구', '금천구',
       '양천구', '영등포구', '광진구', '동대문구', '도봉구', '용산구', '강북구', '중구', '기타']
        month = ['2020년 03월','2020년 04월','2020년 05월','2020년 06월','2020년 07월','2020년 08월','2020년 09월','2020년 10월','2020년 11월','2020년 12월','2021년 01월']
        return render_template('covid-19/makechart_seoul.html', menu=menu, weather=get_weather(), area = area, month = month)
    
    else:
        area = request.form.getlist('area_data')
        count = len(area)
        color_list = ["red","violet","green","blue","orange","purple","hotpink","aqua","lime","navy","darkred","indigo","magenta","orangered","royalblue","yellow","brown","blue","red","violet","green","blue","orange","purple","hotpink","aqua","lime","navy","darkred","indigo","magenta","orangered","royalblue","yellow","brown","blue"]
        if request.form['date'] == 'day':
            pick = '확진일'
            s_date = request.form['s_date']
            e_date = request.form['e_date']
            rows = s_chart(s_date,e_date)
            s_d,e_d = s_date,e_date
            
        else:
            pick = '확진월'
            s_date = request.form['s_mon'][:-1].replace('년 ','-') + '-01'
            e_date = request.form['e_mon'][:-1].replace('년 ','-') + '-31'
            s_d,e_d = request.form['s_mon'], request.form['e_mon']
            rows = s_chart(s_date,e_date)
        
        df = pd.DataFrame(rows, columns=['연번','확진일','지역','접촉력'])
        df['지역'][df['지역'] == '타시도'] = '기타'
        df['지역'][df['지역'] == ''] = np.nan
        df['확진월'] = df['확진일'].apply(lambda r: r.split('-')[0] + '년' + r.split('-')[1] + '월' )
        df['확진자'] = 1
        chart_df = pd.pivot_table(df,               
                index = '지역',    
                columns = pick,  
                values = '확진자',   
                aggfunc = 'sum')       
        chart_df.fillna(0,inplace=True)
        label = list(chart_df.columns)
        val = chart_df.loc[area].values.tolist()
        chart_list = [] 
        for i in range(count):
            cha = f''' "label" : "{area[i]}", "data" : {val[i]}, "fill":false,"borderColor":"{color_list[i]}","lineTension":0.1 '''
            cha = '{' + cha + '}'
            chart_list.append(cha)
        
        return render_template('covid-19/makechart_seoul_res.html', menu=menu, weather=get_weather(), label=label, val = val, area= area, chart_list=chart_list, s_d= s_d, e_d = e_d)