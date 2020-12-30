from flask import Blueprint, render_template, request, session, g
from flask import current_app
from datetime import timedelta
import os, json,folium
import pandas as pd
from my_util.weather import get_weather
from my_util.crawl_a import *

crawling_bp = Blueprint('crawling_bp', __name__)


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

@crawling_bp.route('/bugs')
def bugs():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':1, 'st':0, 'wc':0}
    b_dict = bugs_crawl()
    return render_template('crawling/bugs.html', menu=menu, weather=get_weather(), b_dict=b_dict)

@crawling_bp.route('/mango' , methods=['GET', 'POST'])
def mango_plates():

    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':1, 'st':0, 'wc':0}
    if request.method == 'GET':
        mango = mango_crawl()
        search = '고기'
        count = len(mango['title'])
        
        return render_template('crawling/mango.html', menu=menu, weather=get_weather(), mango=mango,  count = count,search =search)
    else:
        search = request.form['search']
        mango = mango_search(search)
        count = len(mango['title'])
        
        return render_template('crawling/mango.html', menu=menu, weather=get_weather(), mango=mango, count = count,search =search)