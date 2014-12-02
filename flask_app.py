from flask import Flask, render_template, request, redirect, url_for
import itertools
import ast
DIC_FILE = '/home/fabula/mysite/static/dic'
DATA_FILE = '/home/fabula/mysite/static/cur_data'
letters = list(map(chr, range(ord('a'), ord('z')+1))) + list(map(chr, range(ord('A'), ord('Z')+1))) + list(map(chr, range(ord('0'), ord('9')+1)))

def get_dict():
    with open(DIC_FILE, 'r') as dic_file:
        return ast.literal_eval(dic_file.read())

def set_dict(dic):
    with open(DIC_FILE, 'w') as dic_file:
        dic_file.write(dic.__repr__())

def set_current_data(l):
    with open(DATA_FILE, 'w') as data_file:
        for item in l:
            data_file.write(item.__repr__() + '#')

def get_current_data(types):
    with open(DATA_FILE, 'r') as data_file:
        l = data_file.read().split('#')
        ans = []
        for index, f in enumerate(types):
            ans.append(f(l[index]))
        return ans

app = Flask(__name__)

@app.route("/link/<url>/")
def home_with_url(url):
    return render_template('home.html', url='http://fabula.pythonanywhere.com/' + url)

@app.route("/")
def home():
    return render_template('home.html', url='')

@app.route("/<url>/")
def redirect_to_url(url):
    dic = get_dict()
    if (dic.get(url, 0)):
        return redirect(dic[url])
    else:
        return 'Page not found'

@app.route("/new_link/", methods=["POST"])
def new_link():
    cur_len, cur_index = get_current_data([int, int])
    cur_words = [''.join(i) for i in itertools.product(letters, repeat=cur_len)]
    long_url = request.form['long_url']
    short_url = cur_words[cur_index]
    if (cur_index + 1 == len(cur_words)):
        cur_index = 0
        cur_len += 1
    else:
        cur_index += 1
    set_current_data([cur_len, cur_index])
    dic= get_dict()
    dic[short_url] = long_url
    set_dict(dic)
    return redirect(url_for('home_with_url', url=short_url))

@app.route("/recent/")
def recent():
    dic = get_dict()
    return render_template('recent_url.html', dic=dic)

@app.route("/login/", methods=["POST"])
def login():
    login = request.form['login']
    password = request.form['pass']
    return login + password

if __name__ == "__main__":
    app.run(debug=True)