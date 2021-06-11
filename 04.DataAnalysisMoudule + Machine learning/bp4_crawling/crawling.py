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
menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':1, 'wc':0,
            'cf':0, 'ac':0, 'rg':0, 'cl':0}
@crawling_bp.route('/bugs')
def bugs():
    b_dict = bugs_crawl()
    return render_template('crawling/bugs.html', menu=menu, weather=get_weather(), b_dict=b_dict)

@crawling_bp.route('/mango' , methods=['GET', 'POST'])
def mango_plates():
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

@crawling_bp.route('/tv/<option>')
def tv_option(option):
    soup = tv_crawl(option)
    family = soup.select_one('table.ranking_tb')
    fam = str(family).replace('class="ranking_tb"','table class="table table-bordered table-sm"').replace('<td>','<td><small>').replace('</td>','</td></small>')
    viewer = soup.select('table.ranking_tb')[1]
    view = str(viewer).replace('class="ranking_tb"','table class="table table-bordered table-sm"').replace('<td>','<td><small>').replace('</td>','</td></small>')
    title = soup.select_one('span.subbody_tit_kor').text
    
    return render_template('crawling/tv.html', menu=menu, weather=get_weather(), fam=fam, view=view , title = title)

@crawling_bp.route('/lolchess')
def lolchess():
    soup = lolchess_crawl()
    # contents = soup.select_one('.guide-meta__group.tier-S')
    contents = soup.select_one('.container-full')

    return render_template('crawling/lolchess.html', menu=menu, weather=get_weather(), contents=contents)


