import sqlite3

def all_result():
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute('select * from "시도발생_현황" ')
    rows = cur.fetchall()
    conn.close()

    return rows



def d_result(date):
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute(f'select * from "시도발생_현황" where "일자" = "{date}" ')
    rows = cur.fetchall()
    conn.close()

    return rows

def t_result():
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute('select * from "시도발생_현황" order by "일자" desc limit 19')
    rows = cur.fetchall()
    conn.close()

    return rows


def d_age_result(date):
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute(f'select * from "연령별·성별감염_현황" where "등록일" = "{date}" limit 9')
    rows = cur.fetchall()
    conn.close()

    return rows

def age_result():
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute('select * from "연령별·성별감염_현황"  limit 9 ')
    rows = cur.fetchall()
    conn.close()

    return rows

def d_sex_result(date):
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute(f'select * from "연령별·성별감염_현황" where "등록일" = "{date}" limit 11')
    rows = cur.fetchall()
    conn.close()

    return rows

def sex_result():
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute('select * from "연령별·성별감염_현황"  limit 11 ')
    rows = cur.fetchall()
    conn.close()

    return rows

def seoul_data():
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute(f'select * from "서울시 확진자 현황"')
    rows = cur.fetchall()
    conn.close()
    
    return rows


def t_chart(data,s_date,e_date):
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute(f'''select * from "{data}" where( "일자" >= "{s_date}") and ("일자" <= "{e_date}")''')
    rows = cur.fetchall()
    conn.close()

    return rows

def s_chart(s_date,e_date):
    conn = sqlite3.connect('./DB/covid-19.db')
    cur = conn.cursor()
    cur.execute(f'''select * from "서울시 확진자 현황" where( "확진일" >= "{s_date}") and ("확진일" <= "{e_date}") ''')
    rows = cur.fetchall()
    conn.close()

    return rows


