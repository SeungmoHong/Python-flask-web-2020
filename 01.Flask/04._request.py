from flask import Flask, render_template, request
from flask import Response, make_response

app = Flask(__name__)

@app.route('/area')
def area():
    pi = request.args.get('pi', '3.14')  #디폴트 값 3.14로 지정
    radius = request.args['radius']
    s = float(pi) * float(radius)
    return f'pi={pi}, radius ={radius}, area={s}'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('03.login.html')
    else:
        uid = request.form['uid']    # form 의 name
        pwd = request.values['pwd']  # valuse로도 가능
        # pwd = request.form['pwd']
        return f'uid = {uid}, pwd = {pwd}'

@app.route('/response')
def response_fn():
    custom_res = Response('Custom Response', 200, {'test': 'ttt'})
    return make_response(custom_res)



if __name__ == '__main__':
    app.run(debug=True)