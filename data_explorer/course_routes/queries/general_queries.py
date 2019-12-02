from data_explorer.db import query_mysql


class CourseInfo:
	"""Data for the General tab."""
	def __init__(self, lang, course_code):
		self.lang = lang
		self.course_code = course_code
		self.course_info = None
	
	
	def load(self):
		"""Query course's info from table 'product_info' and format for
		display in General tab.
		"""
		# Explicitely list field names to avoid anti-pattern 'SELECT *' + to
		# future proof if columns change order
		if self.lang == 'fr':
			fields = """
				course_description_fr, business_type_fr, provider_fr,
				displayed_on_gccampus_fr, duration, main_topic_fr, business_line_fr,
				required_training_fr, communities_fr, point_of_contact, director,
				program_manager, project_lead
			"""
		else:
			fields = """
				course_description_en, business_type_en, provider_en,
				displayed_on_gccampus_en, duration, main_topic_en, business_line_en,
				required_training_en, communities_en, point_of_contact, director,
				program_manager, project_lead
			"""
		query = "SELECT {0} FROM product_info WHERE course_code = %s LIMIT 1;".format(fields)
		results = query_mysql(query, (self.course_code,), dict_=True)
		# Account for new courses that have registrations but have yet to be catalogued
		# Return empty dict as templates use method dict.pop to handle missing vals
		if not results:
			self.course_info = {}
			return self
		# Format keys for displaying on page
		results_processed = {self._clean_key(key): val for (key, val) in results[0].items()}
		self.course_info = results_processed
		# Return self to allow method chaining
		return self
	
	
	@staticmethod
	def _clean_key(key):
		"""Correct English and French formatting edge cases."""
		key = key.title()
		replace_dict = {'_En': '', '_Fr': '', '_': ' ', 'Of': 'of', 'On': 'on', 'Gccampus': 'GCcampus'}
		for old, new in replace_dict.items():
			key = key.replace(old, new)
		return key
