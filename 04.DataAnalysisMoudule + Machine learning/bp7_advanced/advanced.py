from flask import Blueprint, render_template, request, session, g
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import os, folium, json, joblib
import numpy as np
import pandas as pd
import sklearn.datasets as sd
import matplotlib.pyplot as plt 
from sklearn.datasets import fetch_20newsgroups
from my_util.weather import get_weather
from konlpy.tag import Okt




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
        index = int(request.form['index'] or '0')
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
@ac_bp.route('/news', methods=['GET', 'POST'])
def news():
    test_news = fetch_20newsgroups(subset='test', random_state=156,
                                remove=('header', 'footer', 'quotes'))
    if request.method == 'GET':
        return render_template('advanced/news.html', menu=menu, weather=get_weather())
    else :
        index = int(request.form['index'] or '0')
        
        features = test_news.target_names
        test_df = pd.DataFrame(test_news.data)
        test_df['target'] = test_news.target
        X_test = test_df[test_df[0] != ''][0]
        y_test = test_df[test_df[0] != '']['target']
        X_test.reset_index(drop=True,inplace=True)
        y_test.reset_index(drop=True,inplace=True)
        tfidf_vect = joblib.load('./static/model/news_tfidf_vect.pkl')
        count_vect = joblib.load('./static/model/news_count_vect.pkl')
        X_test_tfidf = tfidf_vect.transform(X_test)
        X_test_count = count_vect.transform(X_test)
        tf_lr = joblib.load('./static/model/news_tf_lr.pkl')
        tf_sv = joblib.load('./static/model/news_tf_sv.pkl')
        co_lr = joblib.load('./static/model/news_co_lr.pkl')
        label = y_test.iloc[index]
        tr_lr_pred = tf_lr.predict(X_test_tfidf)[index]
        tr_sv_pred = tf_sv.predict(X_test_tfidf)[index]
        co_lr_pred = co_lr.predict(X_test_count)[index]
        news = X_test[index]
        ans = {'실제 분류' : features[label], 'TfidfVectorizer + LogisticRegression' : features[tr_lr_pred], 'TfidfVectorizer + SVC' : features[tr_sv_pred], 'CountVectorizer + LogisticRegression' : features[co_lr_pred]}           
        return render_template('advanced/news_res.html', menu=menu, weather=get_weather(), ans=ans, index=index, news=news)
@ac_bp.route('/imdb', methods=['GET', 'POST'])
def imdb():
    if request.method == 'GET':
        return render_template('advanced/IMDB.html', menu=menu, weather=get_weather())
    else :
        tf_lr = joblib.load('./static/model/tf_lr_imdb.pkl')
        co_lr = joblib.load('./static/model/co_lr_imdb.pkl')
        evaluation = ['부정', '긍정']
        if request.form['sel'] == 'test_data':
            index = int(request.form['index'] or '0')
            df_test = pd.read_csv('./static/data/imdb_test.csv')
            X_test = df_test.iloc[index].review
            y_test = df_test.iloc[index].sentiment
            tr_lr_pred = tf_lr.predict([X_test])
            co_lr_pred = co_lr.predict([X_test])
            ans = {'실제 값 :' : evaluation[y_test] ,
                   'TfidfVectorizer + LogisticRegression' : evaluation[tr_lr_pred[0]],
                   'CountVectorizer + LogisticRegression' : evaluation[co_lr_pred[0]]}
            item = [request.form['index'] + '번', X_test]
        else :
            X_test = request.form['test']
            tr_lr_pred = tf_lr.predict([X_test])
            co_lr_pred = co_lr.predict([X_test])
            ans = {'TfidfVectorizer + LogisticRegression' : evaluation[tr_lr_pred[0]],
                   'CountVectorizer + LogisticRegression' : evaluation[co_lr_pred[0]]}
            item = ['사용자 테스트' , X_test]
        return render_template('advanced/IMDB_res.html', menu=menu, weather=get_weather(), ans=ans, item=item)

@ac_bp.route('/nmsc', methods=['GET', 'POST'])
def nmsc():
    if request.method == 'GET':
        return render_template('advanced/nmsc.html', menu=menu, weather=get_weather())
    else :
        okt = Okt()
        stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다','을']
        evaluation = ['부정', '긍정']
        tf_lr = joblib.load('./static/model/tf_lr_nmsc.pkl')
        tf_nb = joblib.load('./static/model/tf_nb_nmsc.pkl')
        co_lr = joblib.load('./static/model/co_lr_nmsc.pkl')
        co_nb = joblib.load('./static/model/co_nb_nmsc.pkl')
        if request.form['sel'] == 'test_data':
            index = int(request.form['index'] or '0')
            df_test = pd.read_csv('./static/data/nmsc_test.tsv',sep ='\t')
            text = df_test.iloc[index].document
            morphs = okt.morphs(text, stem=True)
            X_test = ' '.join([word for word in morphs if not word in stopwords])
            y_test = df_test.iloc[index].label
            tf_lr_pred = tf_lr.predict([X_test])
            tf_nb_pred = tf_nb.predict([X_test])
            co_lr_pred = co_lr.predict([X_test])
            co_nb_pred = co_nb.predict([X_test])
            ans = {'실제 값 :' : evaluation[y_test] ,
                'TfidfVectorizer + LogisticRegression' : evaluation[tf_lr_pred[0]],
                'TfidfVectorizer + 나이브 베이즈' : evaluation[tf_nb_pred[0]],
                'CountVectorizer + LogisticRegression' : evaluation[co_lr_pred[0]],
                'CountVectorizer + 나이브 베이즈' : evaluation[co_nb_pred[0]]}
            item = [request.form['index'] + '번', text]

        else :
            text = request.form['test']
            morphs = okt.morphs(text, stem=True)
            X_test = ' '.join([word for word in morphs if not word in stopwords])
            tf_lr_pred = tf_lr.predict([X_test])
            tf_nb_pred = tf_nb.predict([X_test])
            co_lr_pred = co_lr.predict([X_test])
            co_nb_pred = co_nb.predict([X_test])
            ans = {'TfidfVectorizer + LogisticRegression' : evaluation[tf_lr_pred[0]],
                    'TfidfVectorizer + 나이브 베이즈' : evaluation[tf_nb_pred[0]],
                    'CountVectorizer + LogisticRegression' : evaluation[co_lr_pred[0]],
                    'CountVectorizer + 나이브 베이즈' : evaluation[co_nb_pred[0]]}
            item = ['사용자 테스트' , text]
        return render_template('advanced/nmsc_res.html', menu=menu, weather=get_weather(), ans=ans, item=item)
    
            

            
        

        