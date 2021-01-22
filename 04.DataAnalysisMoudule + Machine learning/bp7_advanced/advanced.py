from flask import Blueprint, render_template, request, session, g
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import os, folium, json, joblib
import numpy as np
import pandas as pd
import sklearn.datasets as sd
import matplotlib.pyplot as plt 
from my_util.weather import get_weather


ac_bp = Blueprint('ac_bp', __name__)

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


menu = {'ho':0, 'da':0, 'ml':1, 'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':1, 'rg':0, 'cl':0}
@ac_bp.route('/digits', methods=['GET', 'POST'])
def digits():
    if request.method == 'GET':
        return render_template('advanced/digits.html', menu=menu, weather=get_weather())
    else :
        index = int(request.form['index'])
        digits = sd.load_digits()
        df_test = pd.read_csv('./static/data/digits_test.csv')
        test_index = df_test['index'][index] # 실제 인덱스
        test_label = df_test['target'][index] # 실제 값
        scaler = joblib.load('./static/model/digits_scaler.pkl')
        scaled_test = scaler.fit_transform(df_test.drop(columns=['index','target'], axis=1))
        test_data = scaled_test[index].reshape(1,-1)

        lr = joblib.load('./static/model/digits_lr.pkl')
        rf = joblib.load('./static/model/digits_rf.pkl')
        sv = joblib.load('./static/model/digits_sv.pkl')
        pred_lr = lr.predict(test_data)
        pred_rf = rf.predict(test_data)
        pred_sv = sv.predict(test_data)
        acs = ['실제 값 :', 'Logistic Regression 예측 :', 'Random Forest 예측 :', 'SVC 예측 :']
        labels = [test_label, pred_lr[0], pred_rf[0], pred_sv[0]]
        

        plt.figure(figsize=(2,2))
        plt.xticks([]); plt.yticks([])
        plt.imshow(digits.images[test_index], cmap=plt.cm.binary, interpolation='nearest')
        plt.savefig('./static/img/digits.png')
        img_file = os.path.join(current_app.root_path, './static/img/digits.png')
        mtime = int(os.stat(img_file).st_mtime)
       
        return render_template('advanced/digits_res.html', menu=menu, weather=get_weather(), acs=acs, labels=labels, mtime=mtime, index=index)
