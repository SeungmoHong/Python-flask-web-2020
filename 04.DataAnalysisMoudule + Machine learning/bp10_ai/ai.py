from flask import Blueprint, render_template, request, session, g
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import os, json, requests
from urllib.parse import quote
from my_util.weather import get_weather



ai_bp = Blueprint('ai_bp', __name__)

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
            'cf':0, 'ac':0, 'rg':0, 'cl':0 ,'ai':1}
def generate_url(text, src, dst):
    return f'https://dapi.kakao.com/v2/translation/translate?query={quote(text)}&src_lang={src}&target_lang={dst}'   


@ai_bp.route('/translation', methods=['GET', 'POST'])
def translation():
    if request.method == 'GET':
        return render_template('ai/translation.html', menu=menu, weather=get_weather())
    else:
        with open('keys/papago_key.json') as nkey:
            json_str = nkey.read(100)
        with open('keys/kakaoaikey.txt') as kfile:
            kai_key = kfile.read(100)
        json_obj = json.loads(json_str)
        client_id = list(json_obj.keys())[0]
        client_secret = json_obj[client_id]
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret
        }
        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
        text = request.form['test']
        lang = request.form['lang']
        k_lang = {'en' : '영어', 'zh-CN' : '중국어 간체', 'zh-TW' : '중국어 번체', 'es' : '스페인어',
                  'fr' : '프랑스어', 'vi' : '베트남어', 'th' : '태국어', 'id' : '인도네시아어', 'ja' : '일본어'}
        kakao_lang =''
        if lang == 'zh-CN':
            kakao_lang = 'cn'
        elif lang == 'ja':
            kakao_lang = 'jp'
        else :
            kakao_lang = lang
        val = {
        "source": 'ko',
        "target": lang,
        "text": text
        }
        response = requests.post(url,  data=val, headers=headers)
        result1 = json.loads(response.text)
        result2 = requests.get(generate_url(text, 'kr', kakao_lang),
            headers={"Authorization": "KakaoAK "+kai_key}).json()
        tmp_ans = result2['translated_text']
        kakao_ans = '\n'.join([tmp[0] for tmp in tmp_ans])
        ans = [k_lang[lang],result1['message']['result']['translatedText'], kakao_ans]
        
        return render_template('ai/translation_res.html', menu=menu, weather=get_weather(), text=text, ans=ans)
@ai_bp.route('/voice', methods=['GET', 'POST'])
def voice():
    if request.method == 'GET':
        return render_template('ai/voice.html', menu=menu, weather=get_weather())
    else :
        with open('keys/clova_key.json') as nkey:
            json_str = nkey.read(100)
        json_obj = json.loads(json_str)
        client_id = list(json_obj.keys())[0]
        client_secret = json_obj[client_id]
        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        speed = str((int(request.form['speed'])-50)/-10)
        pitch = str((int(request.form['pitch'])-50)/-10)
        emotion = request.form['emotion']
        text = request.form['test']
        speakers = {'여성1' : 'nara', '여성2' : 'mijin', '남성' : 'jinho'}
        speaker = speakers[request.form['speaker']]
        val = {
        "speaker": speaker,
        "speed": speed,
        "text": text,
        "emotion": emotion,
        "pitch" : pitch
        }
        response = requests.post(url, data=val, headers=headers)
        rescode = response.status_code
        if(rescode == 200):
            with open('static/voice/voice.mp3', 'wb') as f:
                f.write(response.content)
        mp3_file = os.path.join(current_app.root_path, 'static/voice/voice.mp3')
        mtime = int(os.stat(mp3_file).st_mtime)
        ans = [request.form['test'], request.form['speaker'], request.form['speed']+'%', request.form['pitch']+'%']
        return render_template('ai/voice_res.html', menu=menu, weather=get_weather(), mtime=mtime, ans=ans)

        