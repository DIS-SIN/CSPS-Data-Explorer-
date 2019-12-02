import datetime
from io import BytesIO
import pandas as pd
from flask_babel import gettext
from data_explorer.db import query_mysql


def browse_tab(tab_name):
	"""Query contents of the 'product_info' table."""
	query = """
		SELECT course_code, course_description_en, course_description_fr,
			business_type_en, business_type_fr, provider_en, provider_fr,
			displayed_on_gccampus_en, displayed_on_gccampus_fr, duration,
			main_topic_en, main_topic_fr, business_line_en, business_line_fr,
			required_training_en, required_training_fr, communities_en, communities_fr,
			point_of_contact, director, program_manager, project_lead
		FROM product_info
		ORDER BY 1 ASC;
	"""
	# Run query
	results = query_mysql(query, dict_=True)
	results_processed = _dicts_to_lists(results)
	# Create file
	file = _create_file(results_processed, tab_name)
	return file


def calendar_tab(tab_name):
	"""Query contents of the 'offerings' table."""
	query = """
		SELECT offering_id, course_title_en, course_title_fr, course_code, instructor_names,
			confirmed_count, cancelled_count, waitlisted_count, no_show_count, business_type,
			event_description, fiscal_year, quarter, start_date, end_date, client, offering_status,
			offering_language, offering_region_en, offering_region_fr, offering_province_en,
			offering_province_fr, offering_city_en, offering_city_fr, offering_lat, offering_lng
		FROM offerings
		ORDER BY 12 ASC, 14 ASC, 4 ASC;
	"""
	# Run query
	results = query_mysql(query, dict_=True)
	results_processed = _dicts_to_lists(results)
	# Create file
	file = _create_file(results_processed, tab_name)
	return file


def general_tab(course_code):
	"""Query raw data used for the General tab."""
	query = """
		SELECT course_code, course_description_en, course_description_fr,
			business_type_en, business_type_fr, provider_en, provider_fr,
			displayed_on_gccampus_en, displayed_on_gccampus_fr, duration,
			main_topic_en, main_topic_fr, business_line_en, business_line_fr,
			required_training_en, required_training_fr, communities_en, communities_fr,
			point_of_contact, director, program_manager, project_lead
		FROM product_info
		WHERE course_code = %s;
	"""
	# Run query
	results = query_mysql(query, (course_code,), dict_=True)
	results_processed = _dicts_to_lists(results)
	# Create file
	file = _create_file(results_processed, course_code)
	return file


def comments_tab(course_code):
	"""Query raw data used for the Comments tab."""
	query = """
		SELECT course_code, survey_id, fiscal_year, quarter, offering_city_en,
			offering_city_fr, original_question, short_question, text_answer,
			overall_satisfaction, stars, magnitude
		FROM comments
		WHERE course_code = %s;
	"""
	# Run query
	results = query_mysql(query, (course_code,), dict_=True)
	results_processed = _dicts_to_lists(results)
	# Create file
	file = _create_file(results_processed, course_code)
	return file


def schedule_tab(course_code):
	"""Query raw data used for the Schedule tab."""
	query = """
		SELECT course_code, offering_id, instructor_names, confirmed_count,
			cancelled_count, waitlisted_count, no_show_count, business_type,
			start_date, end_date, client, offering_status, offering_language,
			offering_region_en, offering_region_fr, offering_province_en,
			offering_province_fr, offering_city_en, offering_city_fr,
			offering_lat, offering_lng
		FROM offerings
		WHERE course_code = %s;
	"""
	# Run query
	results = query_mysql(query, (course_code,), dict_=True)
	results_processed = _dicts_to_lists(results)
	# Create file
	file = _create_file(results_processed, course_code)
	return file


def ratings_tab(course_code):
	"""Query raw data used for the Comments->Ratings tab."""
	query = """
		SELECT course_code, survey_id, fiscal_year, month_en, month_fr,
			original_question, numerical_answer, text_answer_en,
			text_answer_fr
		FROM ratings
		WHERE course_code = %s;
	"""
	# Run query
	results = query_mysql(query, (course_code,), dict_=True)
	results_processed = _dicts_to_lists(results)
	# Create file
	file = _create_file(results_processed, course_code)
	return file


def _dicts_to_lists(my_list):
	"""Convert list of dictionaries to list of lists, with first
	nested list containing column names.
	"""
	try:
		column_names = list(my_list[0].keys())
	# Account for tabs without data e.g. no learners have filled out a survey
	except IndexError:
		return [[gettext('Apologies, this tab contains no data.')]]
	results_processed = []
	results_processed.append(column_names)
	for dict_ in my_list:
		# Passing each key to dict is slow as requires each key
		# to be hashed. However, this method is safer than using
		# dict.values as lists produced guaranteed to follow correct
		# order. Note dicts in Python >= 3.6 preserve order.
		new_list = [dict_[column] for column in column_names]
		results_processed.append(new_list)
	return results_processed


def _create_file(my_data, sheet_name):
	"""Create .xlsx file in memory."""
	df = pd.DataFrame(my_data[1:], columns=my_data[0], index=None)
	file = BytesIO()
	with pd.ExcelWriter(file, date_format='YYYY-MM-DD', mode='w', engine='xlsxwriter') as writer:
		df.to_excel(writer, sheet_name=sheet_name, na_rep='', index=False)
	return file.getvalue()
