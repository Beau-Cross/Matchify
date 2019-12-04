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
def account(AccountInfo=None, Matched=None, AccountID=None,dataMatch=None):
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
	yourMatches = db.child("matchedWith").child(profileJSON["id"]).get().val()
	theirMatches = db.child("matchedWith").child(profileID).get().val()
	dataMatch = db.child("matchResults").child(profileJSON["id"]).get().val()

	if (yourMatches is None):
		yourMatches = {}
	if (theirMatches is None):
		theirMatches = {}

	for yourMatch in yourMatches:
		if (yourMatch == profileID):
			Match = 1

	if (Match == 1):
		for theirMatch in theirMatches:
			if (theirMatch == profileJSON["id"]):
				Match = 2

	#Grab account info
	QueryList = db.child("users").child(profileID).get()
	AccountInfo = QueryList.val()
	if (AccountInfo == None):
		return str("This account doesn't exist in our database")
	else:
		return render_template("account.html", AccountInfo=AccountInfo, Matched=Match, AccountID=profileID,dataMatch=dataMatch[profileID])

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
def matches(yourMatches=None):
	if ('auth_header' in session):
		profileJSON = spotify.get_users_profile(session['auth_header'])
		if ("id" not in profileJSON):
			return render_template("homeAnon.html")
		else:
			profileID = profileJSON["id"]
			yourMatches = db.child("matchResults").child(profileID).get().val()
			if (yourMatches is None):
				return redirect("/updateMatches")
			topMatches = []
			for key, value in yourMatches.iteritems():
				if (len(topMatches) == 0):
					topMatches.append(yourMatches[key])
				else:
					idx = 0
					while (idx < len(topMatches) and int(yourMatches[key]["score"]) < int(topMatches[idx]["score"])):
						idx += 1
					yourMatches[key]["id"] = key
					topMatches.insert(idx, yourMatches[key])
			return render_template("matches.html", yourMatches=topMatches)
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
				profileMatchData = {}
				usersData = db.child("matchData").get().val()
				usersPersonalData = db.child("users").get().val()
				personalData = usersData[profileJSON["id"]]
				yourSex = usersPersonalData[profileJSON["id"]]["gender"]
				yourPref = usersPersonalData[profileJSON["id"]]["preference"]
				possibleSex = []
				if (yourPref == "both"):
					possibleSex = ['male', 'female']
				else:
					possibleSex = [yourPref]
				amount = 0
				for key, userData in usersData.iteritems(): #For every user
					score = 0
					if (key in usersPersonalData):
						theirSex = usersPersonalData[key]["gender"]
						theirPref = usersPersonalData[key]["preference"]
						theirPoss = []
						if (theirPref == "both"):
							theirPoss = ['male', 'female']
						else:
							theirPoss = [theirPref]
						#If the account isn't your own
						if (key != profileJSON["id"] and yourSex in theirPoss and theirSex in possibleSex):
							#Compare all songs
							if 'tracks' in usersData[key] and 'tracks' in personalData and usersData[key]["tracks"] is not None and personalData["tracks"] is not None and 'items' in usersData[key]["tracks"] and 'items' in personalData["tracks"]:
								for trackO in usersData[key]["tracks"]["items"]:
									for trackM in personalData["tracks"]["items"]:
										amount += 1
										#return str(trackM["name"].decode('utf-8'))+str(trackO["name"].decode('utf-8'))
										if (type(trackM["name"]) == type(trackO["name"]) and trackM["name"] == trackO["name"]):
										#if (usersData[userData]["tracks"]["items"][trackO]["name"] == personalData["tracks"]["items"][trackM]["name"]):
											score += 1
							#Compare all artists
							if 'artists' in usersData[key] and 'artists' in personalData and usersData[key]["artists"] is not None and personalData["artists"] is not None and 'items' in usersData[key]["artists"] and 'items' in personalData["artists"]:
								for artistO in usersData[key]["artists"]["items"]:
									for artistM in personalData["artists"]["items"]:
										amount += 1
										#return str(str(artistM["name"])+" "+str(artistO["name"]))
										if (type(artistM["name"]) == type(artistO["name"]) and artistM["name"] == artistO["name"]):
										#if (usersData[userData]["artists"]["items"][artistO]["name"] == personalData["artists"]["items"][artistM]["name"]):
											score += 1
										if 'genre' in artistM and 'genre' in artistO:
											for genreM in artistM["genre"]:
												for genreO in artistO["genre"]:
											#for genreM in personalData["artists"]["items"][artistM]["genre"]:
												#for genreO in usersData[userData]["artists"]["items"][artistO]["genre"]:
													if (type(genreM) == type(genreO) and genreM == genreO):	
														score += 1
							#Give score to user
							#return "key = "+str(key)+" score = "+str(score)
							profileMatchData[key] = {'score':score, 'name':str(usersPersonalData[key]["name"])}
				#update the database
				db.child("matchResults").child(profileJSON["id"]).set(profileMatchData)
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
