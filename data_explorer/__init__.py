from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from flask_babel import Babel
from data_explorer.config import Config

# Instantiate login
auth = HTTPBasicAuth()
users = {
	Config.BASIC_AUTH_USERNAME: Config.BASIC_AUTH_PASSWORD
}

# Instantiate Babel for bilingual text
babel = Babel()


# Create a function for handling 404: Page not found
def not_found(e):
	return render_template('not-found.html'), 404


# Application factory
def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
	
	
	# Register plugins
	@auth.get_password
	def get_pw(username):
		if username in users:
			return users.get(username)
		return None
	babel.init_app(app)
	
	# Register error handlers
	app.register_error_handler(404, not_found)
	
	
	# Set language
	@babel.localeselector
	def get_locale():
		# Only allow 'en' and 'fr' to be passed to app
		return 'fr' if request.cookies.get('lang', None) == 'fr' else 'en'
	
	# Register blueprints
	from data_explorer.main_routes.routes import main
	app.register_blueprint(main)
	return app
