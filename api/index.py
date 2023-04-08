import asyncio
from typing import Union, Any

from flask import Flask, render_template, request, redirect, url_for, jsonify
from googlesearch import Search
from api.execs.requesting import RequestSender
from flask_login import LoginManager, current_user, login_user


app = Flask(__name__)
# loginmanager = LoginManager(app)


@app.route('/')
@app.route('/<lists>')
def home(lists: list = None):
    if request.method == 'GET':
        return render_template("index.html", query="Write Text...", city="Write City")

# it is main element of getting query results
@app.route('/searching', methods=['POST'])
@app.route("/search", methods=['POST'])
def searching():
    if request.method == 'POST':
        def GettingResultFrom2Gis(SessionJson: dict) -> Union[list, dict, Any]:
            if all([True if tag in SessionJson else False for tag in ["query", "city"]]):
                OtherArgs = SessionJson.copy(); [OtherArgs.__delitem__(item) for item in ["query", "city"]]
                return asyncio.run(RequestSender(
                    query=SessionJson['query'], city=SessionJson['city'], **OtherArgs).Sendrequest(all_val=True))

        if request.form:
            queryText = request.form["text"]
            cityText = request.form["city"]
            print("Text: ", queryText)
            FirmValues = GettingResultFrom2Gis({'query': queryText, 'city': cityText})[1]
            return render_template("index.html", params=FirmValues, query=queryText, city=cityText)

        if request.get_json() is not None:
            SessionJson: dict = request.get_json()
            return jsonify(GettingResultFrom2Gis(SessionJson)[1])

        return jsonify({"Request json tags": "invalid"}), 400



@app.route('/about')
def about():
    return 'About'

@app.route('/user')
def UserPage():
    # formis = RegisterForm()
    if current_user.is_authenticated():
        return "Authenticated User"
    return 'About'

@app.route('/register')
def Reqister():
    # formis = RegisterForm()
    return 'About'


@app.route('/login')
def Login():
    # formIs = LoginForm()
    return 'About'

if __name__ == "__main__":
    app.run(debug=True, port=2731)