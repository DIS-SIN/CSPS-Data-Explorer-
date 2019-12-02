from flask import Blueprint, render_template, request
from data_explorer import auth
from data_explorer.config import Config
from data_explorer.course_routes import utils
from data_explorer.course_routes.forms import course_form
from data_explorer.course_routes.queries import (
	comment_queries, dashboard_learner_queries, dashboard_offering_queries,
	general_queries, map_queries, rating_queries, schedule_queries
)

# Instantiate blueprint
course = Blueprint('course', __name__)


# Make certain config vars available to all templates
LAST_YEAR = Config.LAST_YEAR
THIS_YEAR = Config.THIS_YEAR
GOOGLE_MAPS_API_KEY = Config.GOOGLE_MAPS_API_KEY
@course.context_processor
def context_processor():
	return {
		'LAST_YEAR': LAST_YEAR,
		'THIS_YEAR': THIS_YEAR,
		'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY
	}


# Home page with search bar
@course.route('/home')
@auth.login_required
def home():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.cookies.get('lang', None) == 'fr' else 'en'
	form = course_form(lang)()
	return render_template('index.html', form=form)


# Data Explorer's entry for a given course: the meat & potatoes of the app
@course.route('/course-result')
@auth.login_required
def course_result():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.cookies.get('lang', None) == 'fr' else 'en'
	# Security check: if course_code doesn't exist, render not_found.html
	course_code = utils.validate_course_code(request.args)
	if not course_code:
		return render_template('not-found.html')
	
	# Instantiate classes
	course_info = general_queries.CourseInfo(lang, course_code).load()
	overall_offering_numbers_LY = dashboard_offering_queries.OverallOfferingNumbers(LAST_YEAR, course_code).load()
	overall_offering_numbers_TY = dashboard_offering_queries.OverallOfferingNumbers(THIS_YEAR, course_code).load()
	offering_locations = dashboard_offering_queries.OfferingLocations(lang, THIS_YEAR, course_code).load()
	overall_learner_numbers_LY = dashboard_learner_queries.OverallLearnerNumbers('last_year', course_code).load()
	overall_learner_numbers_TY = dashboard_learner_queries.OverallLearnerNumbers('this_year', course_code).load()
	learners_LY = dashboard_learner_queries.Learners(lang, 'last_year', course_code).load()
	learners_TY = dashboard_learner_queries.Learners(lang, 'this_year', course_code).load()
	map = map_queries.Map(lang, 'this_year', THIS_YEAR, course_code).load()
	categorical = comment_queries.Categorical(lang, course_code).load()
	overall_satisfaction_nanos_LY = rating_queries.OverallSatisfaction(course_code, LAST_YEAR, old_survey=False).load()
	overall_satisfaction_nanos_TY = rating_queries.OverallSatisfaction(course_code, THIS_YEAR, old_survey=False).load()
	overall_satisfaction_old_LY = rating_queries.OverallSatisfaction(course_code, LAST_YEAR, old_survey=True).load()
	overall_satisfaction_old_TY = rating_queries.OverallSatisfaction(course_code, THIS_YEAR, old_survey=True).load()
	ratings_LY = rating_queries.Ratings(course_code, LAST_YEAR).load()
	ratings_TY = rating_queries.Ratings(course_code, THIS_YEAR).load()
	
	pass_dict = {
		#Global
		'course_code': course_code,
		'course_title': learners_TY.course_title if learners_TY.course_title else learners_LY.course_title,
		'business_type': learners_TY.business_type if learners_TY.business_type else learners_LY.business_type,
		# General
		'course_info': course_info.course_info,
		# Dashboards - Offerings
		'overall_offering_numbers_LY': overall_offering_numbers_LY.counts,
		'overall_offering_numbers_TY': overall_offering_numbers_TY.counts,
		'region_drilldown': offering_locations.regions,
		'province_drilldown': offering_locations.provinces,
		'city_drilldown': offering_locations.cities,
		'offerings_per_region_and_quarter': dashboard_offering_queries.offerings_per_region_and_quarter(lang, THIS_YEAR, course_code),
		'offerings_per_lang_LY': dashboard_offering_queries.offerings_per_lang(LAST_YEAR, course_code),
		'offerings_per_lang_TY': dashboard_offering_queries.offerings_per_lang(THIS_YEAR, course_code),
		'offerings_cancelled_global_LY': dashboard_offering_queries.offerings_cancelled_global(LAST_YEAR),
		'offerings_cancelled_global_TY': dashboard_offering_queries.offerings_cancelled_global(THIS_YEAR),
		'offerings_cancelled_LY': dashboard_offering_queries.offerings_cancelled(LAST_YEAR, course_code),
		'offerings_cancelled_TY': dashboard_offering_queries.offerings_cancelled(THIS_YEAR, course_code),
		'avg_class_size_global_LY': dashboard_offering_queries.avg_class_size_global('last_year'),
		'avg_class_size_global_TY': dashboard_offering_queries.avg_class_size_global('this_year'),
		'avg_class_size_LY': dashboard_offering_queries.avg_class_size('last_year', course_code),
		'avg_class_size_TY': dashboard_offering_queries.avg_class_size('this_year', course_code),
		'avg_no_shows_global_LY': round(dashboard_offering_queries.avg_no_shows_global('last_year'), 1),
		'avg_no_shows_global_TY': round(dashboard_offering_queries.avg_no_shows_global('this_year'), 1),
		'avg_no_shows_LY': round(dashboard_offering_queries.avg_no_shows('last_year', course_code), 1),
		'avg_no_shows_TY': round(dashboard_offering_queries.avg_no_shows('this_year', course_code), 1),
		# Dashboards - Learners
		'overall_learner_numbers_LY': overall_learner_numbers_LY.counts,
		'overall_learner_numbers_TY': overall_learner_numbers_TY.counts,
		'regs_per_month_TY': learners_TY.regs_per_month,
		'regs_per_month_LY': learners_LY.regs_per_month,
		'no_shows_per_month_TY': learners_TY.no_shows_per_month,
		'no_shows_per_month_LY': learners_LY.no_shows_per_month,
		'top_5_depts_TY': learners_TY.top_depts,
		'top_5_classifs_TY': learners_TY.top_classifs,
		'top_5_depts_LY': learners_LY.top_depts,
		'top_5_classifs_LY': learners_LY.top_classifs,
		# Maps
		'offering_city_counts': map.offerings,
		'learner_city_counts': map.learners,
		# Comments - Categorical
		'expectations': categorical.expectations,
		'recommend': categorical.recommend,
		'gccampus': categorical.gccampus,
		'videos': categorical.videos,
		'blogs': categorical.blogs,
		'forums': categorical.forums,
		'job_aids': categorical.job_aids,
		# Comments - Overall Satisfaction
		'overall_satisfaction_nanos_LY': overall_satisfaction_nanos_LY.processed,
		'overall_satisfaction_nanos_TY': overall_satisfaction_nanos_TY.processed,
		'overall_satisfaction_old_LY': overall_satisfaction_old_LY.processed,
		'overall_satisfaction_old_TY': overall_satisfaction_old_TY.processed,
		# Comments - Ratings
		'ratings_LY': ratings_LY.processed,
		'ratings_TY': ratings_TY.processed,
		# Schedule
		'offerings_scheduled': schedule_queries.offerings_scheduled(lang, THIS_YEAR, course_code)
	}
	return render_template('/course-page/main.html', pass_dict=pass_dict)
