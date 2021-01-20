from flask import Blueprint, render_template, request, session, g
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import os, folium, json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from my_util.weather import get_weather
from my_util.pca_visualization import visual


cl_bp = Blueprint('cl_bp', __name__)

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
            'cf':0, 'ac':0, 'rg':0, 'cl':1}
@cl_bp.route('/', methods=['GET', 'POST'])
def pca():
    if request.method == 'GET':
        return render_template('cluster/cluster.html', menu=menu, weather=get_weather())
    else:
        count = int(request.form['count'])
        f = request.files['csv']
        filename = os.path.join(current_app.root_path, 'static/upload/') + f.filename
        f.save(filename)
        f_n = filename.split('/')[-1]
        current_app.logger.info(f'{filename} is saved.')
        df = pd.read_csv(filename)
        scaler = StandardScaler()
        data_std = scaler.fit_transform(df.iloc[:, :-1]) # 정규화
        data_df = pd.DataFrame(data_std)
        kmeans = KMeans(n_clusters=count, init='k-means++', max_iter=300, random_state=2021)
        kmeans.fit(data_df)
        data_df['target'] = df['target']
        data_df['cluster'] = kmeans.labels_
        pca = PCA(n_components=2)
        data_pca = pca.fit_transform(data_std)
        data_df['pca_x'] = data_pca[:,0]
        data_df['pca_y'] = data_pca[:,1]
        visual(count, data_df, 'static/img/pca.png')
        img_file = os.path.join(current_app.root_path, 'static/img/pca.png')
        mtime = int(os.stat(img_file).st_mtime)
        
        return render_template('cluster/cluster_res.html', menu=menu, weather=get_weather(), mtime=mtime, f_n=f_n,count=count)