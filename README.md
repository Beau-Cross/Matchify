# Matchify
To get running:

flaskapp.py---------

	Comment out 
		import ConfigParser
		cfg = ConfigParser.ConfigParser()
		cfg.read("/home/vm_user/Desktop/Matchify/config.ini")

		config = {
	To do add config and change service account directory to yours
			 }

		firebase = pyrebase.initialize_app(config)
		db = firebase.database()

conf.json----------

	Go to https://developer.spotify.com/dashboard/login

	Sign in using the info posted in the GroupMe

	The client id is visible and there will be a button to show 
	the secret

	id = "client id" 
	secret = "client secret"

	Also on the dashboard there is a "edit settings" button
	There is a redirect url section where if you aren't running
	on any of the addresses listed the redirect from spotify login 
	won't work. If you are running on a different ip or on localhost
	just add the redirect formated: "http://UR_IP/home
		This could be wrong ^

Things to note:

home.html-------
	
	In the style section I added the custom css code for the 
	jumbotrons so if you want to change anything about the top
	do it there

spotify_requests

	
	This is the flask spotify communication API 
		https://github.com/mari-linhares/spotify-flask
	
	Some more details on how it works are found in the 
	spotify_requests file under spotify.py




	
