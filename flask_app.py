from flask import Flask, render_template, request, redirect
import itertools

app = Flask(__name__)
dic={}
letters = list(map(chr, range(ord('a'), ord('z')+1))) + list(map(chr, range(ord('A'), ord('Z')+1))) + list(map(chr, range(ord('0'), ord('9')+1)))
cur_len = 1
cur_index = 0
cur_words = [''.join(i) for i in itertools.product(letters, repeat=cur_len)]

@app.route("/new_link/<url>")
def home_with_url(url):
    return render_template('home.html', url='http://fabula.pythonanywhere.com/' + url)

@app.route("/")
def home():
    return render_template('home.html', url='')

@app.route("/<url>")
def redirect_to_url(url):
    return redirect(dic[url])

@app.route("/new_link/", methods=["POST"])
def new_link():
    global cur_len
    global cur_index
    global cur_words
    long_url = request.form['long_url']
    short_url = cur_words[cur_index]
    if (cur_index + 1 == len(cur_words)):
        cur_index = 0
        cur_len += 1
        cur_words = [''.join(i) for i in itertools.product(letters, repeat=cur_len)]
    else:
        cur_index += 1
    dic[short_url] = long_url
    return redirect('/new_link/' + short_url)

@app.route("/recent")
def recent():
    return render_template('recent_url.html', dic=dic)

if __name__ == "__main__":
    app.run(debug=True)