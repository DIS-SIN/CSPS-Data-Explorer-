from flask import Blueprint, make_response, render_template, redirect, request, url_for
from data_explorer import auth

main = Blueprint('main', __name__)


@main.route('/')
def splash():
	return render_template('splash.html')


@main.route('/about')
@main.route('/browse')
@main.route('/calendar')
@main.route('/course-result')
@main.route('/departments')
@main.route('/download-browse')
@main.route('/download-calendar')
@main.route('/download-comments')
@main.route('/download-dashboard')
@main.route('/download-general')
@main.route('/download-ratings')
@main.route('/download-schedule')
@main.route('/home')
@auth.login_required
def home():
	return render_template('layout.html')


@main.route('/setlang')
@auth.login_required
def setlang():
	"""Allow pages to set cookie 'lang' via query string."""
	# Redirect pages back to themselves except for splash
	if request.referrer.endswith('/'):
		resp = make_response(redirect(url_for('main.home')))
	else:
		resp = make_response(redirect(request.referrer))
	# Only allow 'en' and 'fr' to be passed to app
	if 'lang' in request.args:
		if request.args['lang'] == 'fr':
			resp.set_cookie('lang', 'fr')
		# If 'en' or junk is passed, default to 'en'
		else:
			resp.set_cookie('lang', 'en')
	return resp
