import os

class Config:
	DEBUG = False
	LAST_YEAR = '2018-19'
	THIS_YEAR = '2019-20'
	BABEL_DEFAULT_LOCALE = 'en'
	# Options for flask.jsonify
	JSON_AS_ASCII = False
	JSONIFY_PRETTYPRINT_REGULAR = True
	JSON_SORT_KEYS = False
	# Load strings from environ vars to avoid storing in plaintext
	BASIC_AUTH_USERNAME = os.environ.get('BASIC_AUTH_USERNAME')
	BASIC_AUTH_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD')
	SECRET_KEY = os.environ.get('SECRET_KEY')
	GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
	REGISTHOR_API_KEY = os.environ.get('REGISTHOR_API_KEY')
