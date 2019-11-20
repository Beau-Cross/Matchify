from flask import Flask, redirect, g, render_template, request, session, jsonify, json
from spotify_requests import spotify
from os.path import abspath
import ConfigParser
import pyrebase



app = Flask(__name__,static_url_path='/static')
app.secret_key = 'key key its a key of keys'

cfg = ConfigParser.ConfigParser()
cfg.read("/Users/teaganshepherd/Documents/Matchify/config.ini")

config = {
	"apiKey": cfg.get('info','FIREBASE_API_KEY'),
	"authDomain": "matchify-7b750.firebaseapp.com",
  	"databaseURL": "https://matchify-7b750.firebaseio.com",
  	"projectId": "matchify-7b750",
  	"storageBucket": "matchify-7b750.appspot.com",
  	"serviceAccount": "/Users/teaganshepherd/Documents/Matchify/firebase-private-key.json",
  	"messagingSenderId": "367663586987"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#Authorization API Calls
@app.route("/auth")
def auth():
	return redirect(spotify.AUTH_URL)

@app.route("/callback")
def callback():
	auth_token = request.args['code']
	auth_header = spotify.authorize(auth_token)
	session['auth_header'] = auth_header

	return profile()

def valid_toek(resp):
	return resp is not None and not 'error' in resp
#----------------END Authorizaton


#Home Page Calls
@app.route("/")
def home():
	return render_template("home.html")

@app.route("/home")
def template():
	return render_template("home.html")
#----------------END Home Calls


#HeadCall
#-----------------
@app.route("/header")
def nav():
	return render_template("header.html")
#-----------------

#Account Info Call
#-----------------
@app.route("/accountInfo")
def accountInfo():
	return render_template("accountInfo.html")
#-----------------

#Matches
#-----------------
@app.route("/matches")
def matches():
	return render_template("matches.html")
#-----------------

@app.route("/firebaseTest")
def fbTest():
	new_event = {"Test": "Value"}
	jsonData = json.dumps(new_event)
	db.child("events").push(jsonData)
	return str(new_event)

#This page is how to pass key/value pairs to the server side
@app.route("/validate")
def validate():
	username = request.args.get("username")
	password = request.args.get("password")
	return str("username: "+username+" password: "+password)

#This page shows how to export json files
@app.route("/jsontest")
def makejson():
	d = {'car': {'color': 'red', 'make': 'Nissan', 'model': 'Altima'}}
	return jsonify(d)

if __name__ == "__main__":
	app.run(debug=True, port=spotify.PORT)
