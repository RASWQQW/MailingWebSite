from flask import Flask, render_template, request, redirect, url_for
from googlesearch import Search

app = Flask(__name__)

@app.route('/')
@app.route('/<lists>')
def home(lists: list=None):
    if request.method == 'GET':
        return render_template("index.html", searched="Write Text...")
    
    

@app.route("/search", methods=['GET', 'POST'])
def SearchIn():
    pass

@app.route('/searching', methods=['GET', 'POST'])
def searching():
    if request.method == 'POST':
        gettingTExt = request.form["text"]
        print("Text: ", gettingTExt)

        searching = Search(gettingTExt).results
        for el in searching:
            print(el.url)
            print(el.title)


        rtt = [{"Alma": "Alma", "Ata": "Kuku"}, {"Alma": "Alma", "Ata": "Kuku"}]
        return render_template("index.html", params=searching, searched=gettingTExt)


@app.route('/about')
def about():
    return 'About'