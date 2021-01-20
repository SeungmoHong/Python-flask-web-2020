from flask import Blueprint, render_template, request, session, g
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import os, folium, json
import pandas as pd
from my_util.weather import get_weather
from cartogram.drawkorea import drawKorea as dk

carto_bp = Blueprint('carto_bp', __name__)

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
menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':1, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 'rg':0, 'cl':0}
@carto_bp.route('/coffee', methods=['GET', 'POST'])
def coffee():
    if request.method == 'GET':
        return render_template('cartogram/coffee.html', menu=menu, weather=get_weather())
    else:
        item = request.form['item']
        color = request.form['color']
        f = request.files['csv']
        #filename = os.path.join(current_app.root_path, 'static/upload/') + secure_filename(f.filename)
        filename = os.path.join(current_app.root_path, 'static/upload/') + f.filename
        f.save(filename)
        current_app.logger.info(f'{filename} is saved.')
        df = pd.read_csv(filename, index_col=0)
        dk(item , df, color,'static/img/coffee.png')
        img_file = os.path.join(current_app.root_path, 'static/img/coffee.png')
        mtime = int(os.stat(img_file).st_mtime)
        top_10 = df.sort_values(item ,ascending=False).head(10)['ID'].values.tolist()

        if item != '커피지수':
            item += '지수'

        return render_template('cartogram/coffee_res.html', menu=menu, weather=get_weather(), 
                                mtime=mtime, item= item, top_10 = top_10)

@carto_bp.route('/people', methods=['GET', 'POST'])
def people():
    if request.method == 'GET': 
        return render_template('cartogram/people.html', menu=menu, weather=get_weather())
    else:
        item = request.form['item']
        color = request.form['color']
        f = request.files['csv']
        #filename = os.path.join(current_app.root_path, 'static/upload/') + secure_filename(f.filename)
        filename = os.path.join(current_app.root_path, 'static/upload/') + f.filename
        f.save(filename)
        current_app.logger.info(f'{filename} is saved.')
        df = pd.read_csv(filename, index_col=0)
        dk(item , df, color,'static/img/people.png')
        img_file = os.path.join(current_app.root_path, 'static/img/people.png')
        mtime = int(os.stat(img_file).st_mtime)


        if item == '소멸위기지역':
            item = '소멸비율'
            top_10 = df.sort_values(item).head(10)['ID'].values.tolist()
        else:
            top_10 = df.sort_values(item ,ascending=False).head(10)['ID'].values.tolist()

        return render_template('cartogram/people_res.html', menu=menu, weather=get_weather(), 
                                mtime=mtime, item= item, top_10 = top_10)

@carto_bp.route('/burger', methods=['GET', 'POST'])
def burger():
    if request.method == 'GET': 
        return render_template('cartogram/burger.html', menu=menu, weather=get_weather())
    else:
        item = request.form['item']
        color = request.form['color']
        f = request.files['csv']
        #filename = os.path.join(current_app.root_path, 'static/upload/') + secure_filename(f.filename)
        filename = os.path.join(current_app.root_path, 'static/upload/') + f.filename
        f.save(filename)
        current_app.logger.info(f'{filename} is saved.')
        df = pd.read_csv(filename, index_col=0)
        dk(item , df, color,'static/img/burger.png')
        img_file = os.path.join(current_app.root_path, 'static/img/burger.png')
        mtime = int(os.stat(img_file).st_mtime)
        top_10 = df.sort_values(item ,ascending=False).head(10)['ID'].values.tolist()

        if item != '버거지수':
            item += '지수'

        return render_template('cartogram/burger_res.html', menu=menu, weather=get_weather(), 
                                mtime=mtime, item= item, top_10 = top_10)
