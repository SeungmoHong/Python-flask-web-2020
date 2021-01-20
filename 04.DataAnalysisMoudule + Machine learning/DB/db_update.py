import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd

key_fd = open('./과제data/gov_data_api_key.txt', mode='r')
govapi_key = key_fd.read(100)
key_fd.close()
end_date = datetime.today().strftime("%Y%m%d")

def daily_update(start_date):
    corona_url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    url = f'{corona_url}?ServiceKey={govapi_key}&pageNo=1&numOfRows=10&startCreateDt={start_date}&endCreateDt={end_date}'
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'xml')
    
    
    createDt_list,deathCnt_list,defCnt_list,gubun_list,incDec_list = [],[],[],[],[]
    isolClearCnt_list,isolIngCnt_list,localOccCnt_list,overFlowCnt_list = [],[],[],[]
    seq_list,qurRate_list,stdDay_list,updateDt_list = [],[],[],[]
    items = soup.find_all('item')
    for item in items:
        createDt_list.append(item.find('createDt').string if item.find('createDt') else '')
        deathCnt_list.append(item.find('deathCnt').string if item.find('deathCnt') else '')
        defCnt_list.append(item.find('defCnt').string if item.find('defCnt') else 0)
        gubun_list.append(item.find('gubun').string if item.find('gubun') else '')
        incDec_list.append(item.find('incDec').string if item.find('incDec') else '')
        isolClearCnt_list.append(item.find('isolClearCnt').string if item.find('isolClearCnt') else '')
        isolIngCnt_list.append(item.find('isolIngCnt').string if item.find('isolIngCnt') else '')
        localOccCnt_list.append(item.find('localOccCnt').string if item.find('localOccCnt') else '')
        overFlowCnt_list.append(item.find('overFlowCnt').string if item.find('overFlowCnt') else '')
        qurRate_list.append(item.find('qurRate').string if item.find('qurRate') else '')
        stdDay_list.append(item.find('stdDay').string if item.find('stdDay') else '')
        updateDt_list.append(item.find('updateDt').string if item.find('updateDt') else '')
        seq_list.append(item.find('seq').string)

    df = pd.DataFrame({
        '등록시간':createDt_list, '사망자':deathCnt_list, '확진자':defCnt_list,
        '광역시도':gubun_list, '전일대비':incDec_list, '격리해제':isolClearCnt_list, 
        '격리중':isolIngCnt_list, '지역발생':localOccCnt_list,'해외유입':overFlowCnt_list,
        '10만명당':qurRate_list, '기준시간':stdDay_list, '수정시간':updateDt_list, 'seq' : seq_list
    })
    df = df[['기준시간', '광역시도', '확진자', '사망자', '전일대비', '격리해제', '격리중', '지역발생', '해외유입', '10만명당','seq']]
    df['일자'] = df['기준시간'].apply(lambda r : r.split('일')[0].replace('년 ','-').replace('월 ','-'))
    df['일자'] = pd.to_datetime(df['일자']) 
    df['일자2'] = df['일자'].astype(str)

    for i in df['seq'].unique():
        if len(df[df['seq'] == i]) > 1 :
            x = df[df['seq'] == i][1:].index
            for k in x :
                df.drop(k, inplace=True)
    
    for i in df['일자2'].unique():
        if len(df[df['일자2'] == i]) > 20:
            x = df[df['일자2'] == i].tail(len(df[df['일자2'] == i]) - 19).index
            for k in x:
                df.drop(k, inplace=True)

    df.sort_index(ascending=False, inplace=True)
    df = df[['seq','일자2','광역시도','확진자','사망자','전일대비','격리해제','격리중','지역발생','해외유입','10만명당']]
    df.reset_index(drop=True, inplace=True)
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    sql_insert = 'insert into "시도발생_현황" values(?,?,?,?,?,?,?,?,?,?,?)'
    for i in df.index:
        params = list(df.loc[i])
        cur.execute(sql_insert, params)
        conn.commit()
    
    conn.close()