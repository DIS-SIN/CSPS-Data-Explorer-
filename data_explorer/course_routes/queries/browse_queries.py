import pandas as pd
from flask_babel import gettext
from data_explorer.db import query_mysql
from data_explorer.course_routes.forms import _clean_title


class CourseList:
	"""Data for the Browse page, purpose of which is to allow users to 
	browse by Business Line and Provider.
	"""
	def __init__(self, lang):
		self.lang = lang
		self.data = None
		self.business_lines = None
		self.providers = None
	
	
	def load(self):
		"""Run query and process all raw data."""
		self._load_courses()
		self._load_business_lines()
		self._load_providers()
		# Return self to allow method chaining
		return self
	
	
	def _load_courses(self):
		"""Query the DB and store results in DataFrame."""
		# Get course codes from LSR to ensure course has usage and will
		# therefore have an entry in the Data Explorer i.e. no dead links
		query = """
			SELECT DISTINCT c.provider_{0}, c.business_line_{0}, b.course_code, b.course_title_{0}
			FROM (
				SELECT a.course_code, a.course_title_{0}
				FROM (
					SELECT DISTINCT course_code, course_title_{0}
					FROM lsr_last_year
					UNION
					SELECT DISTINCT course_code, course_title_{0}
					FROM lsr_this_year
				) AS a
			) AS b
			LEFT OUTER JOIN product_info AS c
			ON b.course_code = c.course_code
			GROUP BY b.course_code;
		""".format(self.lang)
		results = query_mysql(query)
		results = pd.DataFrame(results, columns=['provider', 'business_line', 'course_code', 'course_title'])
		self.data = results
	
	
	def _load_business_lines(self):
		"""Get list of unique business lines."""
		business_lines = self.data.loc[:, 'business_line']
		business_lines.replace(['', None, 'None'], gettext('<awaiting mapping>'), inplace=True)
		business_lines = business_lines.unique()
		# .unique() returns an ndarray
		business_lines.sort()
		self.business_lines = business_lines
	
	
	def _load_providers(self):
		"""Get list of unique providers."""
		providers = self.data.loc[:, 'provider']
		providers.replace(['', None, 'None'], gettext('<awaiting mapping>'), inplace=True)
		providers = providers.unique()
		# .unique() returns an ndarray
		providers.sort()
		self.providers = providers
	
	
	def _get_courses(self, business_line, provider):
		"""For a given business line and provider, output list of
		associated course codes and course titles.
		"""
		business_line_bool = self.data['business_line'] == business_line
		provider_bool = self.data['provider'] == provider
		courses = self.data.loc[business_line_bool & provider_bool, ['course_code', 'course_title']].values.tolist()
		courses = sorted(courses)
		# Remove course codes from titles
		results_processed = [[course[0], _clean_title(course[1])] for course in courses]
		return results_processed
	
	
	def _get_nested_dicts(self):
		"""Create a nested dictionary based on self.business_lines and self.providers."""
		results = {}
		for business_line in self.business_lines:
			business_line_courses = {}
			for provider in self.providers:
				courses = self._get_courses(business_line, provider)
				if courses:
					business_line_courses[provider] = courses
			if business_line_courses:
				results[business_line] = business_line_courses
		return results
