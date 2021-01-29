from flask import Blueprint, render_template, request, session, g
from flask import current_app
from datetime import timedelta
import os, folium, json, joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from my_util.weather import get_weather


cf_bp = Blueprint('cf_bp', __name__)

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
            'cf':1, 'ac':0, 'rg':0, 'cl':0}
@cf_bp.route('/cancer', methods=['GET', 'POST'])
def cancer():
    if request.method == 'GET':
        return render_template('classification/cancer.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'] or '0')
        scaler = joblib.load('./static/model/cancer_scaler.pkl')
        df = pd.read_csv('./static/data/cancer_test.csv')
        scaled_test = scaler.fit_transform(df.iloc[:, :-1])
        test_data = scaled_test[index, :].reshape(1,-1)

        lr = joblib.load('./static/model/cancer_lr.pkl')
        rf = joblib.load('./static/model/cancer_rf.pkl')
        sv = joblib.load('./static/model/cancer_sv.pkl')
        label = df.iloc[index, -1]
        pred_lr = lr.predict(test_data)
        pred_rf = rf.predict(test_data)
        pred_sv = sv.predict(test_data)
        columns1 = dict(df.loc[index][:10])
        columns2 = dict(df.loc[index][10:20])
        columns3 = dict(df.loc[index][20:30])
        cfs = ['실제 값 :', 'Logistic Regression 예측 :', 'Random Forest 예측 :', 'SVC 예측 :']
        labels = [label, pred_lr[0], pred_rf[0], pred_sv[0]]
        labels = list(map(lambda x: '악성' if x == 0 else '양성', labels))
        return render_template('classification/cancer_res.html', menu=menu, weather=get_weather(), labels=labels,cfs=cfs, columns1=columns1,columns2=columns2,columns3=columns3,index=index)
@cf_bp.route('/titanic', methods=['GET', 'POST'])
def titanic():
    if request.method == 'GET':
        return render_template('classification/titanic.html', menu=menu, weather=get_weather())
    else :
        index = int(request.form['index'] or '0')
        scaler = joblib.load('./static/model/titanic_scaler.pkl')
        ori_df = pd.read_csv('./static/data/titanic_test.csv')
        ori_df.fillna('정보없음', inplace=True)
        df = pd.read_csv('./static/data/n_titanic_test.csv')
        df_test_label = pd.read_csv('./static/data/titanic_test_label.csv')
        scaled_test = scaler.transform(df)
        lr = joblib.load('./static/model/titanic_lr.pkl')
        rf = joblib.load('./static/model/titanic_rf.pkl')
        sv = joblib.load('./static/model/titanic_sv.pkl')
        label = df_test_label['Survived'][index]
        pred_lr = lr.predict(scaled_test)
        pred_rf = rf.predict(scaled_test)
        pred_sv = sv.predict(scaled_test)
        cfs = ['실제 값 :', 'Logistic Regression 예측 :', 'Random Forest 예측 :', 'SVC 예측 :']
        labels = [label, pred_lr[index], pred_rf[index], pred_sv[index]]
        labels = list(map(lambda x: '사망' if x == 0 else '생존', labels))
        ori_col = list(ori_df.columns)
        ori_data = list(ori_df.iloc[index].values)
        
        return render_template('classification/titanic_res.html', menu=menu, weather=get_weather(), labels=labels,cfs=cfs,index=index, ori_col=ori_col, ori_data=ori_data)
@cf_bp.route('/pima', methods=['GET', 'POST'])
def pima():
    if request.method == 'GET':
        return render_template('classification/pima.html', menu=menu, weather=get_weather())
    else :
        index = int(request.form['index'] or '0')
        scaler = joblib.load('./static/model/diabetes_scaler.pkl')
        df = pd.read_csv('./static/data/diabetes_test.csv')
        scaled_test = scaler.fit_transform(df.iloc[:, :-1])
        test_data = scaled_test[index, :].reshape(1,-1)
        lr = joblib.load('./static/model/diabetes_lr.pkl')
        rf = joblib.load('./static/model/diabetes_rf.pkl')
        sv = joblib.load('./static/model/diabetes_sv.pkl')
        label = df.iloc[index, -1]
        pred_lr = lr.predict(test_data)
        pred_rf = rf.predict(test_data)
        pred_sv = sv.predict(test_data)
        labels = [label, pred_lr[0], pred_rf[0], pred_sv[0]]
        cfs = ['실제 값 :', 'Logistic Regression 예측 :', 'Random Forest 예측 :', 'SVC 예측 :']
        columns = dict(df.loc[index][:-1])
        labels = list(map(lambda x: '정상' if x == 0 else '당뇨병', labels))
        return render_template('classification/pima_res.html', menu=menu, weather=get_weather(), labels=labels,cfs=cfs, columns=columns,index=index)
@cf_bp.route('/iris', methods=['GET', 'POST'])
def iris():
    if request.method == 'GET':
        return render_template('classification/iris.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'] or '0')
        scaler = joblib.load('./static/model/iris_scaler.pkl')
        df = pd.read_csv('./static/data/iris_test.csv')
        scaled_test = scaler.fit_transform(df.iloc[:, :-1])
        test_data = scaled_test[index, :].reshape(1,-1)
        lr = joblib.load('./static/model/iris_lr.pkl')
        rf = joblib.load('./static/model/iris_rf.pkl')
        sv = joblib.load('./static/model/iris_sv.pkl')
        label = df.iloc[index, -1]
        pred_lr = lr.predict(test_data)
        pred_rf = rf.predict(test_data)
        pred_sv = sv.predict(test_data)
        labels = [label, pred_lr[0], pred_rf[0], pred_sv[0]]
        cfs = ['실제 값 :', 'Logistic Regression 예측 :', 'Random Forest 예측 :', 'SVC 예측 :']
        columns = dict(df.loc[index][:-1])
        labels = list(map(lambda x: 'setosa' if x == 0 else 'versicolor' if x == 1 else 'virginica', labels))
        return render_template('classification/iris_res.html', menu=menu, weather=get_weather(), labels=labels,cfs=cfs, columns=columns,index=index)

@cf_bp.route('/wine', methods=['GET', 'POST'])
def wine():
    if request.method == 'GET':
        return render_template('classification/wine.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'] or '0')
        scaler = joblib.load('./static/model/wine_scaler.pkl')
        df = pd.read_csv('./static/data/wine_test.csv')
        scaled_test = scaler.fit_transform(df.iloc[:, :-1])
        test_data = scaled_test[index, :].reshape(1,-1)
        lr = joblib.load('./static/model/wine_lr.pkl')
        rf = joblib.load('./static/model/wine_rf.pkl')
        sv = joblib.load('./static/model/wine_sv.pkl')
        label = df.iloc[index, -1]
        pred_lr = lr.predict(test_data)
        pred_rf = rf.predict(test_data)
        pred_sv = sv.predict(test_data)
        labels = [label, pred_lr[0], pred_rf[0], pred_sv[0]]
        cfs = ['실제 값 :', 'Logistic Regression 예측 :', 'Random Forest 예측 :', 'SVC 예측 :']
        columns = dict(df.loc[index][:-1])
        
        return render_template('classification/wine_res.html', menu=menu, weather=get_weather(), labels=labels,cfs=cfs, columns=columns,index=index)


        