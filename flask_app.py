#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, make_response
import itertools
import hashlib
import ast
import os
SCRIPT_PATH =  os.path.dirname(os.path.realpath(__file__))
DIC_FILE = SCRIPT_PATH + '/static/dic'
DATA_FILE = SCRIPT_PATH + '/static/cur_data'
USERS_FILE = SCRIPT_PATH + '/static/users'
letters = list(map(chr, range(ord('a'), ord('z')+1))) + list(map(chr, range(ord('A'), ord('Z')+1))) + list(map(chr, range(ord('0'), ord('9')+1)))

def get_dict(FILE):
    with open(FILE, 'r') as dic_file:
        return ast.literal_eval(dic_file.read())

def set_dict(FILE, dic):
    with open(FILE, 'w') as dic_file:
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
    return render_template('home.html', url='http://fabula.pythonanywhere.com/' + url, login=request.cookies.get('login'))

@app.route("/")
def home():
    return render_template('home.html', url='', login=request.cookies.get('login'))

@app.route("/<url>/")
def redirect_to_url(url):
    DIC = GET_DICT(DIC_FILE)
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
    dic= get_dict(DIC_FILE)
    dic[short_url] = long_url
    set_dict(DIC_FILE, dic)
    return redirect(url_for('home_with_url', url=short_url))

@app.route("/recent/")
def recent():
    dic = get_dict(DIC_FILE)
    return render_template('recent_url.html', dic=dic, login=request.cookies.get('login'))

@app.route("/sign_in/", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        login = request.form['login']
        password = request.form['pass'].encode('utf-8')
        users = get_dict(USERS_FILE)
        hash = hashlib.sha224(password).hexdigest()
        if users.get(login, None) == hash:
            resp = make_response(render_template('sign_in.html', msg='correct', login=login))
            resp.set_cookie('login', login)
            return resp
        else:
            return render_template('sign_in.html', msg='incorrect')

    else:
        return render_template('sign_in.html', login=request.cookies.get('login'))

@app.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    users = get_dict(DIC_FILE)
    if request.method == "POST":
        login = request.form['login']
        password = request.form['pass'].encode('utf-8')
        conf_pass = request.form['conf_pass'].encode('utf-8')
        if password != conf_pass:
            return 'Passwords are different'
        if users.get(login, None) != None:
            return 'This login is occupied'
        users[login] = hashlib.sha224(password).hexdigest()
        set_dict(USERS_FILE, users)
        return redirect(url_for('sign_in'))
    else:
        return render_template('sign_up.html', login=request.cookies.get('login'))

@app.route('/sign_out/', methods=['GET', 'POST'])
def sign_out():
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('login', '')
    return resp
    

if __name__ == "__main__":
    app.run(debug=True)
