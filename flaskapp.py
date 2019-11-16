import pyrebase
from flask import Flask, render_template, request, session, jsonify, json
from os.path import abspath
import ConfigParser

app = Flask(__name__)

cfg = ConfigParser.ConfigParser()
cfg.read('/home/beauho/Programming/flaskappConfig/config.ini')

config = {
  "apiKey": cfg.get('info','FIREBASE_API_KEY'),
  "authDomain": "matchify-7b750.firebaseapp.com",
  "databaseURL": "https://matchify-7b750.firebaseio.com",
  "projectId": "matchify-7b750",
  "storageBucket": "matchify-7b750.appspot.com",
  "serviceAccount": "/home/beauho/Programming/flaskapp/firebase-private-key.json",
  "messagingSenderId": "367663586987"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/home")
def template():
	return render_template("home.html")

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
	app.run(debug=True)
