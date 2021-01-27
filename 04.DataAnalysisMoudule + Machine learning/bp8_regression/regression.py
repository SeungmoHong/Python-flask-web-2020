from flask import Blueprint, render_template, request , session
from flask import current_app
from fbprophet import Prophet
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import pandas_datareader as pdr
from sklearn.linear_model import LinearRegression
from my_util.weather import get_weather

rg_bp = Blueprint('rg_bp', __name__)

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
kospi_dict, kosdaq_dict = {}, {}
@rg_bp.before_app_first_request
def before_app_first_request():
    kospi = pd.read_csv('./static/data/KOSPI.csv', dtype={'종목코드': str})
    for i in kospi.index:
        kospi_dict[kospi['종목코드'][i]] = kospi['종목명'][i]
    kosdaq = pd.read_csv('./static/data/KOSDAQ.csv', dtype={'종목코드': str})
    for i in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['종목명'][i]
menu = {'ho':0, 'da':0, 'ml':1, 'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 'rg':1, 'cl':0}

@rg_bp.route('/stock', methods=['GET', 'POST'])
def stock():
    if request.method == 'GET':
        return render_template('regression/stock.html', menu=menu, weather=get_weather(),
                                kospi=kospi_dict, kosdaq=kosdaq_dict)
    else:
        market = request.form['market']
        if market == 'KS':
            code = request.form['kospi_code']
            company = kospi_dict[code]
            code += '.KS'
        else:
            code = request.form['kosdaq_code']
            company = kosdaq_dict[code]
            code += '.KQ'
        learn_period = int(request.form['learn'])
        pred_period = int(request.form['pred'])
        today = datetime.now()
        start_learn = today - timedelta(days=learn_period*365)
        end_learn = today - timedelta(days=1)
        current_app.logger.debug(f'{start_learn}, {end_learn}')

        stock_data = pdr.DataReader(code, data_source='yahoo', start=start_learn, end=end_learn)
        current_app.logger.info(f"get stock data: {code}")
        df = pd.DataFrame({'ds': stock_data.index, 'y': stock_data.Close})
        df.reset_index(inplace=True)
        del df['Date']

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=pred_period)
        forecast = model.predict(future)

        fig = model.plot(forecast);
        img_file = os.path.join(current_app.root_path, 'static/img/stock.png')
        fig.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('regression/stock_res.html', menu=menu, weather=get_weather(), 
                                mtime=mtime, company=company, code=code)

@rg_bp.route('/iris', methods=['GET', 'POST'])
def iris():
    if request.method == 'GET':
        return render_template('regression/iris.html', menu=menu, weather=get_weather())
    else:
        cols = {'sepal length (cm)': 0,'sepal width (cm)': 1,'petal length (cm)': 2,'petal width (cm)':3, 'class':4}
        columns = ['sepal length (cm)','sepal width (cm)','petal length (cm)','petal width (cm)', 'class']
        n_col = request.form['col']
        col = cols[n_col]
        del columns[col]
        index = int(request.form['index'])
        df = pd.read_csv('./static/data/iris_train.csv')
        t_df = pd.read_csv('./static/data/iris_test.csv')
        t_ori_val = t_df.iloc[index].values
        t_val = t_df.drop(request.form['col'], axis=1).iloc[index].values
        lr = LinearRegression()
        col_num = list(range(5))
        del col_num[col]
        lr.fit(df.iloc[:,col_num].values, df.iloc[:,col].values)
        class_names = {0:'setosa', 1:'versicolor',2:'virginica'}
        class_name = class_names[int(t_ori_val[4])]
        tmp = 0        
        for i in range(4):
            tmp += t_val[i]*lr.coef_[i]
        ans = tmp + lr.intercept_
        return render_template('regression/iris_res.html', menu=menu, weather=get_weather(), ans=ans,t_val=t_val,t_ori_val=t_ori_val,
        class_name=class_name,n_col=n_col,columns=columns,col=col, index=index)

        

@rg_bp.route('/boston', methods=['GET', 'POST'])
def boston():
    if request.method == 'GET':
        return render_template('regression/boston.html', menu=menu, weather=get_weather())
    else:
        cols = {'CRIM' : 0, 'ZN' : 1, 'INDUS' :2, 'CHAS': 3, 'NOX': 4, 'RM' : 5, 'AGE' :6, 'DIS' : 7,
        'RAD' : 8, 'TAX' :9,'PTRATIO' :10, 'B' : 11, 'LSTAT': 12, 'PRICE' :13}
        columns = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX','PTRATIO', 'B', 'LSTAT', 'PRICE']
        n_col = request.form['col']
        col = cols[n_col]
        del columns[col]
        index = int(request.form['index'])
        df = pd.read_csv('./static/data/boston_train.csv')
        t_df = pd.read_csv('./static/data/boston_test.csv')
        t_ori_val = t_df.iloc[index].values
        t_val = t_df.drop(request.form['col'], axis=1).iloc[index].values
        lr = LinearRegression()
        col_num = list(range(14))
        del col_num[col]
        lr.fit(df.iloc[:,col_num].values, df.iloc[:,col].values)
        
        tmp = 0
        for i in range(13):
            tmp += t_val[i]*lr.coef_[i]
        ans = tmp + lr.intercept_  #lr.predict(X_test)

        return render_template('regression/boston_res.html', menu=menu, weather=get_weather(), ans=ans,t_val=t_val,t_ori_val=t_ori_val,n_col=n_col,columns=columns,col=col, index=index)

@rg_bp.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    if request.method == 'GET':
        return render_template('regression/diabetes.html', menu=menu, weather=get_weather())
    else:
        col = request.form['col']
        index = int(request.form['index'])
        df = pd.read_csv('./static/data/l_diabetes_train.csv')
        df_test = pd.read_csv('./static/data/l_diabetes_test.csv')
        X = df[col].values.reshape(-1,1)
        y = df.target.values
        lr = LinearRegression()
        lr.fit(X, y)
        weight, bias = lr.coef_, lr.intercept_
        X_test = df_test[col][index]          
        y_test = df_test.target[index]
        pred = X_test * weight[0] + bias

        y_min = np.min(X) * weight[0] + bias
        y_max = np.max(X) * weight[0] + bias

        plt.figure()
        plt.scatter(X, y, label='train')
        plt.plot([np.min(X), np.max(X)], [y_min, y_max], 'r', lw=3)
        plt.scatter([X_test], [y_test], c='r', marker='*', s=100, label='test')
        plt.grid()
        plt.legend()
        plt.title(f'Diabetes target vs. {col}')
        plt.savefig('./static/img/diabetes.png')
        img_file = os.path.join(current_app.root_path, 'static/img/diabetes.png')
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('regression/diabetes_res.html', menu=menu, weather=get_weather(),index=index, y_test=y_test, pred=pred, mtime=mtime)