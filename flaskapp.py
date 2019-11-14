from flask import Flask, redirect, g, render_template, request, session, jsonify, json
from spotify_requests import spotify
from os.path import abspath
import ConfigParser




app = Flask(__name__)
app.secret_key = 'key key its a key of keys'

cfg = ConfigParser.ConfigParser()
cfg.read("/home/vm_user/Desktop/Matchify/config.ini")

config = {
	#To do add config and change service account directory to yours
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

#This page will be a general controller to the mysql database
#In the future it will have the ability to authenticate accounts
@app.route("/db")
def dbController():
	#Create generalized function based on query arguments
	#Get all arguments
	qString = request.query_string[0:]
	delete = False
	qKeys = ""
	qKeysArr = []
	for char in qString:
		if (char == '='):
			delete = True
		if (char == '&'):
			delete = False
		if (delete == False):
			qKeys += char

	qKeysArr = qKeys.split("&")
	qDict = {}
	for key in qKeysArr:
		qDict[key] = request.args.get(key)

	returnJSON = False
	action = "null"
	if "action" in qDict:
		if (qDict["action"] == "select"):
			returnJSON = True
			action = "select"
		if (qDict["action"] == "proc"):
			returnJSON = True
			action = "proc"
	if ("table" in qDict and qDict["table"].isalpha()):
		table = qDict["table"]
	if ("proc" in qDict and qDict["proc"].isaplpha()):
		proc = qDict["proc"]

	#Export data
	if (returnJSON == True):
		return jsonify(json_data)
	else:
		return null

if __name__ == "__main__":
	app.run(debug=True, port=spotify.PORT)
