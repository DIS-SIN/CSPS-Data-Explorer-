import datetime
from data_explorer.db import query_mysql

# If offering has more than n confirmed registrations, it will remain
# on the books and not be cancelled
# Current rule-of-thumb is 10; decided by Programs team at Asticou
CONFIRMED_COUNT_THRESHOLD = 10
COLOR_DICT = {
	'GREEN': '#d4edda',
	'GREY': '#ddd',
	'ORANGE': '#fff3cd',
	'RED': '#f8d7da'
}


def offerings_scheduled(lang, fiscal_year, course_code):
	"""Data for the Schedule tab, purpose of which is to allow users to 
	browse see offerings this fiscal year.
	"""
	field_name_1 = 'offering_city_{0}'.format(lang)
	field_name_2 = 'offering_province_{0}'.format(lang)
	query = """
		SELECT offering_id, start_date, end_date, {0} as offering_city, {1} as offering_province,
			offering_language, instructor_names, confirmed_count, cancelled_count, waitlisted_count,
			no_show_count, client, offering_status
		FROM offerings
		WHERE course_code = %s AND fiscal_year >= %s
		ORDER BY 2 DESC;
	""".format(field_name_1, field_name_2)
	results = query_mysql(query, (course_code, fiscal_year), dict_=True)
	# Assign background colours
	results_processed = []
	for dict_ in results:
		temp_dict = dict_
		start_date = temp_dict['start_date']
		end_date = temp_dict['end_date']
		confirmed_count = temp_dict['confirmed_count']
		offering_status = temp_dict['offering_status']
		temp_dict['color'] = _assign_background_color(start_date, end_date, confirmed_count, offering_status)
		results_processed.append(temp_dict)
	return results_processed


def _assign_background_color(start_date, end_date, confirmed_count, offering_status):
	"""Assign offerings a background colour given their start date, number of
	confirmed registrations, and status.
	"""
	# MySQL returns values from date columns as Python datetime objects, which makes
	# for easy comparison
	current_date = datetime.date.today()
	thirty_days_from_now = current_date + datetime.timedelta(days=30)
	# If offering has been cancelled, red
	# Place this before date check to properly display past offerings that were cancelled
	if offering_status == 'Cancelled - Normal':
		return COLOR_DICT['RED']
	# If offering has already taken place, grey
	if end_date < current_date:
		return COLOR_DICT['GREY']
	# If offering more than a month away or has more than 10 confirmed registrations, green
	if (start_date >= thirty_days_from_now) or (confirmed_count >= CONFIRMED_COUNT_THRESHOLD):
		return COLOR_DICT['GREEN']
	# Else, orange
	return COLOR_DICT['ORANGE']
