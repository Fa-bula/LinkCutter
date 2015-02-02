#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, make_response
import itertools
import hashlib
import ast
import os

SCRIPT_PATH =  os.path.dirname(os.path.realpath(__file__))
USER_LINKS = os.path.join(SCRIPT_PATH, 'static/user_links/')
DATA_FILE = os.path.join(SCRIPT_PATH, 'static/cur_data')
LOGINS_FILE = os.path.join(SCRIPT_PATH, 'static/logins')
RECENT_LINKS = os.path.join(SCRIPT_PATH, 'static/recent')

letters = list(map(chr, range(ord('a'), ord('z')+1))) + list(map(chr, range(ord('A'), ord('Z')+1))) + list(map(chr, range(ord('0'), ord('9')+1)))

def get_dict(FILE):
    if os.path.exists(FILE):
        with open(FILE, 'r') as dict_file:
            return ast.literal_eval(dict_file.read())
    else:
        with open(FILE, 'w') as dict_file:
            dict_file.write('{}')
            return {}

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

@app.route("/link/<login>/<url>/")
def home_with_url(login, url):
    return render_template('home.html', url='http://fabula.pythonanywhere.com/' + login + '/' + url, login=login)

@app.route("/")
def home():
    return render_template('home.html', url='', login=request.cookies.get('login'))

@app.route("/<login>/<url>/")
def redirect_to_url(login, url):
    users = get_dict(LOGINS_FILE)
    if users.get(login, None) == None and login != 'l':
        return "No such login"
    links = get_dict(os.path.join(USER_LINKS, login))
    if (links.get(url, False)):
        return redirect(links[url])
    else:
        return 'Page not found'

@app.route("/new_link/", methods=["POST"])
def new_link():
    long_url = request.form['long_url']
    login =  request.cookies.get('login')
    hash = request.cookies.get('hash')
    users = get_dict(LOGINS_FILE)
    if users.get(login, None) == hash and hash != None:
        short_url = request.form['short_url']
    else:
        login = 'l'
        cur_len, cur_index = get_current_data([int, int])
        cur_words = [''.join(i) for i in itertools.product(letters, repeat=cur_len)]
        short_url = cur_words[cur_index]
        if (cur_index + 1 == len(cur_words)):
            cur_index = 0
            cur_len += 1
        else:
            cur_index += 1
        set_current_data([cur_len, cur_index])
    
    links = get_dict(os.path.join(USER_LINKS, login))
    if links.get(short_url, None) != None:
        return "Address alreafy in use"
    links[short_url] = long_url
    set_dict(os.path.join(USER_LINKS, login), links)
    recent = get_dict(RECENT_LINKS)
    if len(recent) >= 10:
        recent.pop()
    new_recent = [login + '/' + short_url]
    new_recent.extend(recent)
    set_dict(RECENT_LINKS, new_recent)
    return redirect(url_for('home_with_url', url=short_url, login=login))


@app.route("/recent/")
def recent():
    recent_links = get_dict(RECENT_LINKS)
    return render_template('recent_url.html', l=recent_links, login=request.cookies.get('login'))

@app.route("/sign_in/", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        login = request.form['login']
        password = request.form['pass'].encode('utf-8')
        users = get_dict(LOGINS_FILE)
        hash = hashlib.sha224(password).hexdigest()
        if users.get(login, None) == hash:
            resp = make_response(render_template('sign_in.html', msg='correct', login=login))
            resp.set_cookie('login', login)
            resp.set_cookie('hash', hash)
            return resp
        else:
            return render_template('sign_in.html', msg='incorrect')

    else:
        return render_template('sign_in.html', login=request.cookies.get('login'))

@app.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    users = get_dict(LOGINS_FILE)
    if request.method == "POST":
        login = request.form['login']
        password = request.form['pass'].encode('utf-8')
        conf_pass = request.form['conf_pass'].encode('utf-8')
        if password != conf_pass:
            # TODO: делать это через jquery
            return 'Passwords are different'
        if users.get(login, None) != None or login == 'l':
            return 'This login is occupied'
        users[login] = hashlib.sha224(password).hexdigest()
        set_dict(LOGINS_FILE, users)
        return redirect(url_for('sign_in'))
    else:
        return render_template('sign_up.html', login=request.cookies.get('login'))

@app.route('/sign_out/', methods=['GET', 'POST'])
def sign_out():
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('login', '')
    resp.set_cookie('hash', '')
    return resp
    
@app.route('/my_links/')
def my_links():
    login = request.cookies.get('login')
    hash = request.cookies.get('hash')
    users = get_dict(LOGINS_FILE)
    if users.get(login, None) == hash and hash != None:
        links = get_dict(os.path.join(USER_LINKS, login))
        return render_template('recent_url.html', login=login, l=links)
    else:
        redirect(url_for('sign_in'))


if __name__ == "__main__":
    app.run(debug=True)
