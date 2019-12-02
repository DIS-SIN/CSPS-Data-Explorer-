from flask import Blueprint, jsonify, render_template, request
from data_explorer import auth
from data_explorer.course_routes.queries import comment_queries

# Instantiate blueprint
api = Blueprint('api', __name__)

# Mapping of API routes to names in DB
QUESTION_DICT = {
	'general': 'Comment - General',
	'improvement': 'Comment - Improvement',
	'technical': 'Comment - Technical'
}


@api.route('/api/v1/counts/<string:short_question>/<string:course_code>')
@auth.login_required
def counts(short_question, course_code):
	"""Return number of comments by star for a given course code, question,
	and fiscal year.
	"""
	course_code = course_code.upper()
	# Unpack arguments
	fiscal_year = request.args.get('fiscal_year', '')
	
	# Run query; return dict of 0s in case of invalid arguments
	try:
		counts = comment_queries.CommentCounts(course_code, QUESTION_DICT[short_question], fiscal_year).load()
	except Exception as e:
		return jsonify({1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
	return jsonify(counts.processed)


@api.route('/api/v1/comments/<string:short_question>/<string:course_code>')
@auth.login_required
def comments(short_question, course_code):
	"""Return all comments of a given type (e.g. general comments) for a
	given course code.
	"""
	course_code = course_code.upper()
	# Unpack arguments
	# Lang; only allow 'en' and 'fr' to be passed to app
	query_string_lang = request.args.get('lang', '')
	if query_string_lang == 'fr':
		lang = 'fr'
	else:
		lang = 'en'
	# Fiscal year
	fiscal_year = request.args.get('fiscal_year', '')
	# Stars
	stars = request.args.get('stars', '')
	# Limit
	limit = request.args.get('limit', 999_999)
	# Offset
	offset = request.args.get('offset', 0)
	
	# Run query; display error message in case of invalid arguments
	if short_question in ['instructor', 'instructeur']:
		if lang == 'fr':
			error_message = {'Erreur': 'Les commentaires concernant les instructeurs sont présentement désactivés à cause des restrictions de confidentialité.'}
		else:
			error_message = {'Error': 'Comments on instructor performance are currently disabled due to privacy restrictions.'}
		return jsonify(error_message), 410
	else:
		try:
			comments = comment_queries.Comments(lang, course_code, QUESTION_DICT[short_question], fiscal_year, stars, limit, offset).load()
		except Exception as e:
			if lang == 'fr':
				error_message = {'Erreur': 'Les commentaires de ce genre ne sont présentement pas recueillis dans nos sondages.'}
			else:
				error_message = {'Error': 'Comments of this type are not currently collected in our surveys.'}
			return jsonify(error_message), 404
	
	# Account for 0 results
	# If 0 results, comments.processed = False
	if not comments.processed:
		if lang == 'fr':
			error_message = {'Erreur': 'Aucun résultat'}
		else:
			error_message = {'Error': 'No Results'}
		return jsonify(error_message)
	
	results = [_make_dict(lang, tup) for tup in comments.processed]
	# Allow both JSON and a rendered template to be returned
	html = request.args.get('html', False)
	if html == 'true':
		return jsonify(data=render_template('/course-page/comments/comments-generator.html', ajax_comments=results))
	else:
		return jsonify(results)


def _make_dict(lang, my_tup):
	"""Make tuple in a dictionary so can be jsonified into
	an object.
	"""
	labels = ['comment_text', 'learner_classification', 'offering_city',
			  'offering_fiscal_year', 'offering_quarter', 'stars', 'nanos']
	results = {key: val for key, val in zip(labels, my_tup)}
	return results
