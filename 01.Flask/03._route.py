from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return '1234Hello Flask!!'

@app.route('/user/<uid>')
def string_fn(uid):
    return uid

@app.route('/int/<int:number>')
def int_fn(number):
    return str(100*number)
@app.route('/float/<float:number>')
def float_fn(number):
    return str(number*10)

@app.route('/path/<path:path>')
def path_fn(path):
    return f'path {path}'


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('03.login.html')
    else:
        return render_template('02.welcome.html')


if __name__ == '__main__':
    app.run(debug=True)