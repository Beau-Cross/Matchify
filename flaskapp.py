from flask import Flask, redirect, url_for, g, render_template, request, session, jsonify, json
from spotify_requests import spotify
from spotify_requests import spotify as sp
from os.path import abspath
import ConfigParser
import pyrebase
import os



app = Flask(__name__,static_url_path='/static')
app.secret_key = 'key key its a key of keys'

here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, 'config.ini')
privatekeyPath = os.path.join(here, 'firebase-private-key.json')
cfg = ConfigParser.ConfigParser()
cfg.read(filename)

config = {
	"apiKey": cfg.get('info','FIREBASE_API_KEY'),
	"authDomain": "matchify-7b750.firebaseapp.com",
	"databaseURL": "https://matchify-7b750.firebaseio.com",
	"projectId": "matchify-7b750",
	"storageBucket": "matchify-7b750.appspot.com",
	"serviceAccount": privatekeyPath,
	"messagingSenderId": "367663586987"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#Authorization API Calls
@app.route("/auth")
def auth():
	return redirect(spotify.AUTH_URL)

@app.route("/logout")
def logout():
	session.clear()
	return redirect("/home")

@app.route("/callback")
def callback():
	auth_token = request.args['code']
	auth_header = spotify.authorize(auth_token)
	session['auth_header'] = auth_header

	return redirect("/home")
	#return profile()

def valid_toek(resp):
	return resp is not None and not 'error' in resp

#----------------END Authorizaton


#Spotify Helper functions

def getUserId():
	profileJSON = spotify.get_users_profile(session['auth_header'])
	return profileJSON["id"]

#----------------END Helper

#Home Page Calls
@app.route("/")
def home(accountInfo=None, tracks=None, artists=None):
	if ('auth_header' in session):
		profileJSON = spotify.get_users_profile(session['auth_header'])
		if ("id" not in profileJSON):
			return render_template("homeAnon.html")
		else:
			profileID = profileJSON["id"]
			accountInfo = db.child("users").child(profileID).get().val()
			if (accountInfo is None or 'name' not in accountInfo):
				return redirect("/updateAccountData")
			tracks = db.child("matchData").child(profileID).child("tracks").get().val()
			artists = db.child("matchData").child(profileID).child("artists").get().val()
			if (tracks != None and 'items' in tracks):
				tracksI = tracks["items"]
			else:
				tracksI = {}
			if (artists != None and 'items' in artists):
				artistsI = artists["items"]
			else:
				artistsI = {}

			return render_template("home.html", accountInfo=accountInfo, tracks=tracksI, artists=artistsI)
	else:
		return render_template("homeAnon.html")

@app.route("/home")
def template():
	return redirect("/")

#Account Synchronization

@app.route("/topArtists")
def topArtists(artists=None,tracks=None, profile=None):
	if ('auth_header' not in session):
		return redirect("/home")
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
	if ('auth_header' not in session):
		return redirect("/")
	#Grab account info
	profileJSON = spotify.get_users_profile(session['auth_header'])
	#Grab account data
	tracks = spotify.get_users_top(session['auth_header'], 'tracks')
	return str(tracks)

'''
@app.route("/debug")
def debug():
	if ('auth_header' not in session):
		return redirect("/")
	profileJSON = spotify.get_users_profile(session['auth_header'])
	profileID = profileJSON["id"]
	matchedWith = db.child("matchedWith").get().val()
	matchedWith = db.child("matchedWith").get().val()
	if (matchedWith is None or profileID not in matchedWith):
		matchInfo = {}
		db.child("matchedWith").child(profileID).set(matchInfo)
	return str(matchedWith)
'''

@app.route("/updateAccountData")
def updateAccountData():
	if ('auth_header' not in session):
		return redirect("/")
	#Get data
	profileJSON = spotify.get_users_profile(session['auth_header'])
	tracks = spotify.get_users_top(session['auth_header'], 'tracks')
	artists = spotify.get_users_top(session['auth_header'], 'artists')

	profileID = profileJSON["id"]

	db.child("matchData").child(profileID).child("artists").set(artists)
	db.child("matchData").child(profileID).child("tracks").set(tracks)

	#db.child("matchedWith").child(profileID).update( { 'animallza': 1 } )

	accountInfo = db.child("users").child(profileID).get().val()
	if (accountInfo is None or 'name' not in accountInfo):
		return redirect("/updateAccountInfo")
	else:
		return redirect("/updateAccountInfo")


@app.route("/updateAccountInfo", methods=['POST', 'GET'])
def updateAccountInfo(accountUpdated=None, AccountInfo=None):
	if ('auth_header' not in session):
		return redirect("/")
	accountUpdated = False
	profileJSON = spotify.get_users_profile(session['auth_header'])
	if ('id' not in profileJSON):
		return redirect("/")
	profileID = profileJSON["id"]
	AccountInfo = {}
	#If the form submitted
	if (request.method == 'POST'):
		#Fill Account Info
		AccountInfo["name"] = request.form.get("name")
		AccountInfo["age"] = request.form.get("age")
		AccountInfo["email"] = request.form.get("email")
		AccountInfo["phone"] = request.form.get("number")
		AccountInfo["gender"] = request.form.get("gender")
		AccountInfo["preference"] = request.form.get("preference")
		AccountInfo["bio"] = request.form.get("bio")
		#Update Info in database
		db.child("users").child(profileID).set(AccountInfo)
		accountUpdated = True
	else:
		#Get Account Info
		QueryList = db.child("users").child(profileID).get()
		AccountInfo = QueryList.val()
		if (AccountInfo == None):
			AccountInfo = {}
	return render_template("accountInfo.html", accountUpdated=accountUpdated, AccountInfo=AccountInfo)
'''
@app.route("/getAccountData")
def getAccountData():
	if ('auth_header' not in session):
		return redirect("/")
'''
#----------------END Account Sync

#View Other Accounts

@app.route("/account")
def account(AccountInfo=None, Matched=None, AccountID=None):
	Match = 0
	if ('auth_header' not in session):
		return redirect("/")
	#Get query key value pair for userID
	profileID = request.args.get("id")
	if (profileID == None or profileID == ""):
		return redirect("/updateAccountInfo")
	#Get users personal account
	profileJSON = spotify.get_users_profile(session['auth_header'])
	if ('id' not in profileJSON):
		return redirect("/")
	#Is the account Matched
		#0 is not matched with them --> don't show contact info/show match option
		#1 is matched with them but they haven't matched you --> don't show contact info/don't show match option
		#2 is both people are matched --> show contact info/don't show match option
	#Grab match data
	#yourMatches = db.child("matchedWith").child(profileJSON["id"]).get().val()
	#theirMatches = db.child("matchedWith").child(profileID).get().val()

	#Grab account info
	QueryList = db.child("users").child(profileID).get()
	AccountInfo = QueryList.val()
	if (AccountInfo == None):
		return str("This account doesn't exist in our database")
	else:
		return render_template("account.html", AccountInfo=AccountInfo, Matched=Match, AccountID=profileID)

@app.route("/match")
def match():
	if ('auth_header' not in session):
		return redirect("/")
	#Get query key value pair for userID
	otherID = request.args.get("id")
	if (otherID == None or otherID == ""):
		return str("Match failed")

	#Make sure otherID is in database
	users = db.child("users").get().val()
	userExists = False
	for user in users:
		if (user == otherID):
			userExists = True
	if (not userExists):
		return str("User doesn't exist")

	#Get user_id
	profileJSON = spotify.get_users_profile(session['auth_header'])
	profileID = profileJSON["id"]
	#Update Match
	db.child("matchedWith").child(profileID).update({otherID: 1})
	return redirect(url_for(".account", id=otherID))

#----------------End View

#HeadCall
#-----------------
'''
@app.route("/header")
def nav():
	return render_template("header.html")
'''
#-----------------

#Account Info Call
#-----------------
@app.route("/accountInfo")
def accountInfo():
	if ('auth_header' not in session):
		return redirect("/")
	return render_template("accountInfo.html")

@app.route("/matches")
def matches():
	if ('auth_header' in session):
		profileJSON = spotify.get_users_profile(session['auth_header'])
		if ("id" not in profileJSON):
			return render_template("homeAnon.html")
		else:
			return render_template("matches.html")
	else:
		return render_template("homeAnon.html")

@app.route("/updateMatches")
def updateMatches():
		if ('auth_header' in session):
			profileJSON = spotify.get_users_profile(session['auth_header'])
			if ("id" not in profileJSON):
				return render_template("homeAnon.html")
			else:
				#update matches
				#run matching algorithm

				return redirect("/matches")
		else:
			return render_template("homeAnon.html")
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

#This page shows how to export json fileshome
@app.route("/jsontest")
def makejson():
	d = {'car': {'color': 'red', 'make': 'Nissan', 'model': 'Altima'}}
	return jsonify(d)

if __name__ == "__main__":
	app.run(debug=True, port=spotify.PORT)
