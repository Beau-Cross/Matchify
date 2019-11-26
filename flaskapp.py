from flask import Flask, redirect, url_for, g, render_template, request, session, jsonify, json
from spotify_requests import spotify
from spotify_requests import spotify as sp
from os.path import abspath
#import ConfigParser
#import pyrebase



app = Flask(__name__,static_url_path='/static')
app.secret_key = 'key key its a key of keys'

#cfg = ConfigParser.ConfigParser()
#cfg.read("/Users/teaganshepherd/Documents/Matchify/config.ini")

#config = {
#	"apiKey": cfg.get('info','FIREBASE_API_KEY'),
#	"authDomain": "matchify-7b750.firebaseapp.com",
 # 	"databaseURL": "https://matchify-7b750.firebaseio.com",
  #	"projectId": "matchify-7b750",
  #	"storageBucket": "matchify-7b750.appspot.com",
  #	"serviceAccount": "/Users/teaganshepherd/Documents/Matchify/firebase-private-key.json",
  #	"messagingSenderId": "367663586987"
#}

#firebase = pyrebase.initialize_app(config)
#db = firebase.database()

#Authorization API Calls
@app.route("/auth")
def auth():
	return redirect(spotify.AUTH_URL)

@app.route("/callback")
def callback():
	auth_token = request.args['code']
	auth_header = spotify.authorize(auth_token)
	session['auth_header'] = auth_header

	return redirect(url_for('home'))
	#return profile()

def valid_toek(resp):
	return resp is not None and not 'error' in resp

#@app.route("/logout")
#def logout():

#----------------END Authorizaton


#Spotify Helper functions

def getUserId():
	profileJSON = spotify.get_users_profile(session['auth_header'])
	return profileJSON["id"]

#----------------END Helper

#Home Page Calls
@app.route("/")
def home():
	return render_template("home.html")

@app.route("/home")
def template():
	return render_template("home.html")
#----------------END Home Calls

#Account Synchronization

@app.route("/topArtists")
def topArtists(artists=None,tracks=None, profile=None):
	if (session['auth_header'] == None):
		return redirect(url_for('auth'))
	#Grab account info
	profileJSON = spotify.get_users_profile(session['auth_header'])
	#Grab account data
	artists = spotify.get_users_top(session['auth_header'],'artists')

	if (artists is None):
		return str("Sorry, this account has no listening information and cannot be used. Listen to some music on Spotify before using.")

	if (profileJSON != None):
		return render_template('data.html', artists=artists["items"], profile=profileJSON)
	else:
		return redirect(url_for('home'))

@app.route("/topTracks")
def topTracks():
	if (session['auth_header'] == None):
		return redirect(url_for('auth'))
	#Grab account info
	profileJSON = spotify.get_users_profile(session['auth_header'])
	#Grab account data
	tracks = spotify.get_users_top(session['auth_header'], 'tracks')
	return str(tracks)

@app.route("/updateAccountData")
def updateAccountData():
	if (session['auth_header'] == None):
		return redirect(url_for('auth'))
	#Get data
	profileJSON = spotify.get_users_profile(session['auth_header'])
	tracks = spotify.get_users_top(session['auth_header'], 'tracks')
	artists = spotify.get_users_top(session['auth_header'], 'artists')

	profileID = profileJSON["id"]

	db.child("matchData").child(profileID).child("artists").set(artists)
	db.child("matchData").child(profileID).child("tracks").set(tracks)

	return str("For account: "+profileID+" tracks:"+str(tracks)+" artists:"+str(artists))


@app.route("/updateAccountInfo", methods=['POST', 'GET'])
def updateAccountInfo(accountUpdated=None, AccountInfo=None):
	if (session['auth_header'] == None):
		return redirect(url_for('auth'))
	accountUpdated = False
	profileJSON = spotify.get_users_profile(session['auth_header'])
	profileID = profileJSON["id"]
	AccountInfo = {}
	#If the form submitted
	if (request.method == 'POST'):
		#Fill Account Info
		AccountInfo["name"] = request.form.get("name")
		AccountInfo["email"] = request.form.get("email")
		AccountInfo["phone"] = request.form.get("number")
		AccountInfo["gender"] = request.form.get("gender")
		AccountInfo["preference"] = request.form.get("preference")
		#Update Info in database
		db.child("users").child(profileID).set(AccountInfo)
		accountUpdated = True
	else:
		#Get Account Info
		QueryList = db.child("users").child(profileID).get()
		AccountInfo = QueryList[0]
		if (AccountInfo == None):
			AccountInfo = {}
	return render_template("accountInfo.html", accountUpdated=accountUpdated, AccountInfo=AccountInfo)

@app.route("/updateAccountMatch")
def updateAccountMatch():
	if (session['auth_header'] == None):
		return redirect(url_for('auth'))

@app.route("/getAccountData")
def getAccountData():
	if (session['auth_header'] == None):
		return redirect(url_for('auth'))

#----------------END Account Sync

#View Other Accounts

@app.route("/account")
def account():
	#Get query key value pair for userID
	profileID = request.args.get("id")
	if (profileID == None):
		return str("Profile ID Required")
	#Grab account info
	QueryList = db.child("users").child(profileID).get()
	AccountInfo = QueryList.val()
	if (AccountInfo == None):
		return str("This account doesn't exist in our database")
	else:
		return str(AccountInfo)

#----------------End View

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

class Matched(object):
    name = ""
    bio = ""
    matchPercentage = 0.0

    # The class "constructor" - It's actually an initializer
    def __init__(self, name, bio, perc):
        self.name = name
        self.bio = bio
        self.matchPercentage = perc

myMatches = []
#-----------------

#Matches (need to pass in items = )

		#Which is an object that contains the matching info (Name,Bio,MatchPerc)
#-----------------
@app.route("/matches")
def matches():
	return render_template("matches.html")
#-----------------

@app.route("/firebaseTest")
def fbTest():
	new_event = {"Test": "Value"}
	db.child("events").child("0").set(new_event)
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
