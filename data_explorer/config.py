import os

class Config:
	DEBUG = False
	BABEL_DEFAULT_LOCALE = 'en'
	# Load strings from environ vars to avoid storing in plaintext
	BASIC_AUTH_USERNAME = os.environ.get('BASIC_AUTH_USERNAME')
	BASIC_AUTH_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD')
	SECRET_KEY = os.environ.get('SECRET_KEY')
