from bs4 import BeautifulSoup
import urllib.parse
import requests
import pandas as pd


def bugs_crawl():
    url = 'https://music.bugs.co.kr/chart'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    html = requests.get(url, headers = headers).text
    soup = BeautifulSoup(html, 'html.parser')
    img_list,rank_list, title_list, singer_list, album_list =[],[],[],[],[]
    for i in range(100):
        img = soup.find('tbody').find_all('tr')[i].find('a')
        rank = soup.find('tbody').find_all('tr')[i].find('strong').text
        title = soup.find('tbody').find_all('tr')[i].select_one('p.title')
        singer = soup.find('tbody').find_all('tr')[i].select_one('p.artist')
        album = soup.find('tbody').find_all('tr')[i].select_one('a.album')
        img_list.append(img)
        rank_list.append(rank)
        title_list.append(title)
        singer_list.append(singer)
        album_list.append(album)
    
    
    bugs_dict = dict({
        'img' : img_list,
        'rank' : rank_list,
        'title' : title_list,
        'singer' : singer_list,
        'album' : album_list
    })

    return bugs_dict


def mango_crawl():
    url = 'https://www.mangoplate.com/search/%EA%B3%A0%EA%B8%B0'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    html = requests.get(url, headers = headers).text
    soup = BeautifulSoup(html, 'html.parser')
    
    img_list, title_list, point_list, info_list, addr_list, link_list =[],[],[],[],[],[]
    for i in range(10):
        title = soup.select('li.list-restaurant')[i].find('h2').get_text().strip('\n').split('\n')[0]
        img = soup.select('li.list-restaurant')[i].find('img').attrs['data-original'].replace('359:240','120:80')
        point = soup.select('li.list-restaurant')[i].find('strong').text
        info = soup.select('li.list-restaurant')[i].find('p').text
        addr = soup.select('li.list-restaurant')[i].find('img').attrs['alt'].split(' - ')[1]
        link = soup.select('li.list-restaurant')[i].find('a').attrs['href']
        title_list.append(title)
        img_list.append(img)
        point_list.append(point)
        info_list.append(info)
        addr_list.append(addr)
        link_list.append('https://www.mangoplate.com/' + link)
        title = soup.select('li.list-restaurant')[i].find_all('h2')[1].get_text().strip('\n').split('\n')[0]
        img = soup.select('li.list-restaurant')[i].find_all('img')[1].attrs['data-original'].replace('359:240','120:80')
        point = soup.select('li.list-restaurant')[i].find_all('strong')[1].text
        info = soup.select('li.list-restaurant')[i].find_all('p')[2].text
        addr = soup.select('li.list-restaurant')[i].find_all('img')[1].attrs['alt'].split(' - ')[1]
        link = soup.select('li.list-restaurant')[i].find_all('a')[3].attrs['href']
        title_list.append(title)
        img_list.append(img)
        point_list.append(point)
        info_list.append(info)
        addr_list.append(addr)
        link_list.append('https://www.mangoplate.com/' + link)
    
        mango_dict = dict({
            'title' : title_list,
            'img' : img_list,
            'point' : point_list,
            'info' : info_list,
            'addr' : addr_list,
            'link' : link_list
        })

    return mango_dict

def mango_search(search):
    key =  urllib.parse.quote(search)
    url = f'https://www.mangoplate.com/search/{key}'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    html = requests.get(url, headers = headers).text
    soup = BeautifulSoup(html, 'html.parser')
    
    img_list, title_list, point_list, info_list, addr_list, link_list =[],[],[],[],[],[]
    for i in range(10):
        try:
            title = soup.select('li.list-restaurant')[i].find('h2').get_text().strip('\n').split('\n')[0]
            img = soup.select('li.list-restaurant')[i].find('img').attrs['data-original'].replace('359:240','120:80')
            point = soup.select('li.list-restaurant')[i].find('strong').text
            info = soup.select('li.list-restaurant')[i].find('p').text
            addr = soup.select('li.list-restaurant')[i].find('img').attrs['alt'].split(' - ')[1]
            link = soup.select('li.list-restaurant')[i].find('a').attrs['href']
            title_list.append(title)
            img_list.append(img)
            point_list.append(point)
            info_list.append(info)
            addr_list.append(addr)
            link_list.append('https://www.mangoplate.com/' + link)
            title = soup.select('li.list-restaurant')[i].find_all('h2')[1].get_text().strip('\n').split('\n')[0]
            img = soup.select('li.list-restaurant')[i].find_all('img')[1].attrs['data-original'].replace('359:240','120:80')
            point = soup.select('li.list-restaurant')[i].find_all('strong')[1].text
            info = soup.select('li.list-restaurant')[i].find_all('p')[2].text
            addr = soup.select('li.list-restaurant')[i].find_all('img')[1].attrs['alt'].split(' - ')[1]
            link = soup.select('li.list-restaurant')[i].find_all('a')[3].attrs['href']
            title_list.append(title)
            img_list.append(img)
            point_list.append(point)
            info_list.append(info)
            addr_list.append(addr)
            link_list.append('https://www.mangoplate.com/' + link)
        except:
            pass
    
        mango_dict = dict({
            'title' : title_list,
            'img' : img_list,
            'point' : point_list,
            'info' : info_list,
            'addr' : addr_list,
            'link' : link_list
        })

    return mango_dict
