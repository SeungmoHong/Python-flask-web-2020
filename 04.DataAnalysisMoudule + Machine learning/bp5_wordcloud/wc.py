from flask import Blueprint, render_template, request, session, g
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import os, folium, json
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import nltk
from konlpy.tag import Okt
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import matplotlib as mpl 
import matplotlib.pyplot as plt
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)
import numpy as np
import pandas as pd
from my_util.weather import get_weather


wc_bp = Blueprint('wc_bp', __name__)

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


menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':1,
            'cf':0, 'ac':0, 'rg':0, 'cl':0}
@wc_bp.route('/craw', methods=['GET', 'POST'])
def craw():
    if request.method == 'GET':
        return render_template('wordcloud/craw.html', menu=menu, weather=get_weather())
    else:
        driver = webdriver.Chrome('./chromedriver')
        driver.maximize_window()
        okt = Okt()
        text = []
        for i in range(1,10):
            driver.get('https://sports.news.naver.com/index.nhn')
            time.sleep(0.5)
            driver.find_elements_by_class_name('link_main_menu')[i].click()
            time.sleep(0.5)
            driver.find_element_by_link_text('최신뉴스').click()
            time.sleep(0.5)
            old_pg = driver.current_url
            driver.get(old_pg+'&page='+'500')
            time.sleep(0.5)
            page = driver.find_element_by_class_name('paginate').find_element_by_css_selector('strong').text
            driver.get(old_pg)
            time.sleep(0.5)
            for k in range(1, int(page)+1):
                driver.get(driver.current_url+'&page='+str(k))
                time.sleep(0.5)
                tmp = driver.find_element_by_class_name('news_list').find_elements_by_class_name('title')
                for line in tmp:
                    text.append(line.text)
                present_text = ''
            for each_line in text:
                present_text = present_text + each_line + '\n'
            file = open('static/data/wc.txt', 'w',encoding='utf-8')
            file.write(present_text) 
            file.close() 
        return render_template('wordcloud/craw_res.html', menu=menu, weather=get_weather(), text = present_text)


@wc_bp.route('/text', methods=['GET', 'POST'])
def text():
    if request.method == 'GET':
        return render_template('wordcloud/text.html', menu=menu, weather=get_weather())
    else:
        lan = request.form['lan']
        color = request.form['color']
        f = request.files['txt']
        filename = os.path.join(current_app.root_path, 'static/upload/') + f.filename
        f.save(filename)
        current_app.logger.info(f'{filename} is saved.')
        
        try:
            f = request.files['img']
            imgname = os.path.join(current_app.root_path, 'static/upload/') + f.filename
            f.save(imgname)
            current_app.logger.info(f'{imgname} is saved.')
            mask = np.array(Image.open(imgname))

        except:
            mask = None
        
        stop_words = request.form['stop_words']
        stop_words = stop_words.split(' ') if stop_words else []

        if lan == 'eng':
            text = open(filename, encoding='utf-8').read()
            stopwords = set(STOPWORDS)
            for sw in stop_words:
                stopwords.add(sw)
            wc = WordCloud(background_color='white', max_words=2000, mask=mask,
              colormap= color,stopwords = stopwords)
            wc = wc.generate(text)
        elif lan == 'han':
            okt = Okt()
            text = open(filename , encoding='utf-8').read()
            tokens_ko = okt.nouns(text)
            ko = nltk.Text(tokens_ko)
            tokens_ko = [each_word for each_word in tokens_ko if each_word not in stop_words]
            ko = nltk.Text(tokens_ko)
            data = ko.vocab().most_common(200)

            wc= WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                                relative_scaling = 0.2,
                                background_color='white',
                                colormap=color,  
                                mask=mask,
                                width=1000, height=600
                                ).generate_from_frequencies(dict(data))

        plt.figure(figsize=(12,12), dpi=100)
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.savefig('static/img/text.png')
        img_file = os.path.join(current_app.root_path, 'static/img/text.png')
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('wordcloud/text_res.html', menu=menu, weather=get_weather(), mtime = mtime)

@wc_bp.route('/sports_news', methods=['GET', 'POST'])
def sports_news():
    if request.method == 'GET':
        return render_template('wordcloud/sports_news.html', menu=menu, weather=get_weather())
    else:
        color = request.form['color']
        try:
            f = request.files['img']
            imgname = os.path.join(current_app.root_path, 'static/upload/') + f.filename
            f.save(imgname)
            current_app.logger.info(f'{imgname} is saved.')
            mask = np.array(Image.open(imgname))

        except:
            mask = np.array(Image.open('static/img/heart.jpg'))

        text = open('static/data/wc.txt', encoding='utf-8').read()
        okt = Okt()
        tokens_ko = okt.nouns(text)
        ko = nltk.Text(tokens_ko)
        data = ko.vocab().most_common(200)
        wc= WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                                    relative_scaling = 0.2,
                                    background_color='white',
                                    colormap=color,  
                                    mask=mask,
                                    width=1000, height=600
                                    ).generate_from_frequencies(dict(data))
        plt.figure(figsize=(12,12), dpi=100)
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.savefig('static/img/sprots.png')
        img_file = os.path.join(current_app.root_path, 'static/img/sprots.png')
        mtime = int(os.stat(img_file).st_mtime)
        
        return render_template('wordcloud/sports_news_res.html', menu=menu, weather=get_weather(), mtime = mtime)
    
        


        