from flask import Blueprint, make_response, render_template, redirect, request, url_for
from data_explorer import auth
from data_explorer.config import Config
from data_explorer.course_routes.queries import browse_queries

main = Blueprint('main', __name__)


# Make Registhor API key available to all templates
GOOGLE_MAPS_API_KEY = Config.GOOGLE_MAPS_API_KEY
REGISTHOR_API_KEY = Config.REGISTHOR_API_KEY
@main.context_processor
def context_processor():
	return {
		'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY,
		'REGISTHOR_API_KEY': REGISTHOR_API_KEY
	}


@main.route('/')
def splash():
	return render_template('splash.html')


@main.route('/about')
@auth.login_required
def about():
	return render_template('about.html')


# Browse
@main.route('/browse')
@auth.login_required
def browse():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.cookies.get('lang', None) == 'fr' else 'en'
	course_list = browse_queries.CourseList(lang).load()
	pass_dict = course_list._get_nested_dicts()
	return render_template('browse/browse.html', pass_dict=pass_dict)


# Calendar
@main.route('/calendar')
@auth.login_required
def calendar():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.cookies.get('lang', None) == 'fr' else 'en'
	pass_dict = {}
	return render_template('calendar/calendar.html', pass_dict=pass_dict)


# Coming soon
@main.route('/departments')
@auth.login_required
def departments():
	return render_template('departments.html')


@main.route('/setlang')
@auth.login_required
def setlang():
	"""Allow pages to set cookie 'lang' via query string."""
	# Redirect pages back to themselves except for splash
	if request.referrer.endswith('/'):
		resp = make_response(redirect(url_for('course.home')))
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
