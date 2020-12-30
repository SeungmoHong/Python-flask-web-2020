import numpy as np
import pandas as pd

def fillter(all_shop):
    ci = ['수원','성남','안양','안산','고양','용인','청주','천안','전주','포항','창원']
    chang = ['마산합포구', '마산회원구']
    ad = []
    for shop in all_shop:
        df = pd.read_csv(shop, sep='|')
        df = df[df['상권업종중분류명'] == '패스트푸드']
        df = df[['상호명', '시도명' ,'시군구명', '도로명주소']]
        df['상호명'] = df['상호명'].str.lower()
        df.reset_index(inplace=True)
        if df['시도명'][0] in ['서울특별시', '광주광역시', '대구광역시', '대전광역시', '부산광역시', '울산광역시', '인천광역시']:
            df['ID'] = df.apply(lambda r: r['시도명'][:2] + ' ' + r['시군구명'] if len(r['시군구명']) == 2  else  r['시도명'][:2] + ' ' + r['시군구명'][:-1] , axis=1)
        elif df['시도명'][0] in '세종특별자치시':
                df['ID'] = '세종'
        else:
            df['ID'] = df.apply(lambda r:r['도로명주소'].split()[1][:2]+ ' '+ r['도로명주소'].split()[2][2:-1] if r['도로명주소'].split()[2] in chang else '고성(강원)' if (r['시군구명'][:-1] in '고성') and  (r['시도명'] in '강원도') else '고성(경남)' if (r['시군구명'][:-1] in '고성') and  (r['시도명'] in '경상남도')  else r['도로명주소'].split()[1][:2] + ' ' + r['도로명주소'].split()[2] if (r['도로명주소'].split()[1][:2] in ci) and len(r['도로명주소'].split()[2]) == 2 else r['도로명주소'].split()[1][:2] + ' ' + r['도로명주소'].split()[2][:-1] if r['도로명주소'].split()[1][:2] in ci else r['도로명주소'].split()[1][:-1] , axis=1)
        
        for city in df['ID'].unique():
            tmp = df[df['ID'] == city]
            bur = len(tmp[tmp['상호명'].str.find('버거킹')!= -1])
            mac = len(tmp[tmp['상호명'].str.find('롯데리아')!= -1]) 
            kfc = len(tmp[(tmp['상호명'].str.contains('케이에프시')) | (tmp['상호명'].str.contains('kfc')) | (tmp['상호명'].str.contains('케이에프씨'))])
            lot = len(tmp[tmp['상호명'].str.find('롯데리아')!= -1])
            mom = len(tmp[tmp['상호명'].str.find('맘스터치')!= -1])
            ad.append((city,bur,mac,kfc,lot,mom))
    return ad