from data_explorer.db import query_mysql


def validate_course_code(args):
	"""Check if course code exists in LSR."""
	course_code = str(args.get('course_code', False)).upper()
	# Check if found in DB; automatically escaped in MySQL via %s
	query = """
		SELECT
			EXISTS (
				SELECT course_code
				FROM lsr_last_year
				WHERE course_code = %s
				LIMIT 1
			)
		OR
			EXISTS (
				SELECT course_code
				FROM lsr_this_year
				WHERE course_code = %s
				LIMIT 1
			);
	"""
	course_check = query_mysql(query, (course_code, course_code))
	course_check = as_string(course_check)
	return course_code if course_check else False


def as_string(my_val, error_msg=False):
	"""Helper function for returning a single value	from
	MySQL. Convert from [(my_val,)] to string.
	"""
	if not my_val or not my_val[0][0]:
		return error_msg
	else:
		return str(my_val[0][0])


def as_float(my_val):
	"""Helper function for returning a single value	from
	MySQL. Convert from [(my_val,)] to float.
	"""
	return float(as_string(my_val))


def as_int(my_val):
	"""Helper function for returning a single value	from
	MySQL. Convert from [(my_val,)] to int.
	"""
	return int(as_float(my_val))


def as_percent(my_val):
	"""Helper function for returning a single value	from
	MySQL. Convert from [(my_val,)] to percentage.
	"""
	return round(as_float(my_val), 2) * 100
