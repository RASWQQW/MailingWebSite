from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Some Greetings far from Sholda'

@app.route('/about')
def about():
    return 'About'