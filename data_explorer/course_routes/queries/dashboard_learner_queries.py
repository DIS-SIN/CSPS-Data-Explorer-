from flask_babel import gettext
from data_explorer.db import query_mysql
from data_explorer.course_routes.utils import as_string, as_int


class Learners:
	"""Data for the Learners section of the Dashboards tab."""
	def __init__(self, lang, fiscal_year, course_code):
		self.lang = lang
		self.fiscal_year = fiscal_year
		self.course_code = course_code
		self.regs_per_month = None
		self.no_shows_per_month = None
		self.top_classifs = None
		self.top_depts = None
		self.course_title = None
		self.business_type = None
	
	
	def load(self):
		"""Run all learner queries."""
		self._calc_regs_and_no_shows_per_month()
		self._calc_top_classifs()
		self._calc_top_depts()
		self._get_course_tile()
		self._get_business_type()
		# Return self to allow method chaining
		return self
	
	
	def _calc_regs_and_no_shows_per_month(self):
		"""Query number of confirmed regisrations and no-shows per
		month; include months that have 0 of both.
		"""
		field_name = 'month_{0}'.format(self.lang)
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		# Cast SUM to dtype unsigned to prevent MySQL Python connector from
		# returning dtype decimal
		query = """
			SELECT 
				{0},
				COUNT(CASE WHEN (reg_status = 'Confirmed') THEN reg_id END),
				CAST(SUM(no_show) AS UNSIGNED)
			FROM {1}
			WHERE course_code = %s
			GROUP BY 1;
		""".format(field_name, table_name)
		results = query_mysql(query, (self.course_code,))
		results = {tup[0]: (tup[1], tup[2]) for tup in results}
		# Process results into format required by Highcharts
		results_processed_regs = []
		results_processed_no_shows = []
		# Ensure every month is returned, even if count 0
		months = [
			gettext('April'),
			gettext('May'),
			gettext('June'),
			gettext('July'),
			gettext('August'),
			gettext('September'),
			gettext('October'),
			gettext('November'),
			gettext('December'),
			gettext('January'),
			gettext('February'),
			gettext('March')
		]
		for month in months:
			counts = results.get(month, (0, 0))
			results_processed_regs.append([month, counts[0]])
			results_processed_no_shows.append([month, counts[1]])
		self.regs_per_month = results_processed_regs
		self.no_shows_per_month = results_processed_no_shows
	
	
	def _calc_top_classifs(self):
		"""Query the top classifications by number of registrations."""
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		query = """
			SELECT learner_classif, COUNT(learner_classif)
			FROM {0}
			WHERE course_code = %s AND reg_status = 'Confirmed'
			GROUP BY 1
			ORDER BY 2 DESC
			LIMIT 5;
		""".format(table_name)
		results = query_mysql(query, (self.course_code,))
		self.top_classifs = results
	
	
	def _calc_top_depts(self):
		"""Query the top departments by number of registrations."""
		field_name = 'billing_dept_name_{0}'.format(self.lang)
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		query = """
			SELECT {0}, COUNT({0})
			FROM {1}
			WHERE course_code = %s AND reg_status = 'Confirmed'
			GROUP BY 1
			ORDER BY 2 DESC
			LIMIT 5;
		""".format(field_name, table_name)
		results = query_mysql(query, (self.course_code,))
		self.top_depts = results
	
	
	def _get_course_tile(self):
		"""Get course title. In this module as should come from
		the lsr_fiscal_year table rather than the product_info
		table in case the course has registrations but has yet
		to be catalogued by CM."""
		field_name = 'course_title_{0}'.format(self.lang)
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		query = """
			SELECT {0}
			FROM {1}
			WHERE course_code = %s
			LIMIT 1;
		""".format(field_name, table_name)
		results = query_mysql(query, (self.course_code,))
		results = as_string(results)
		self.course_title = results
	
	
	def _get_business_type(self):
		"""Get business type. In this module as should come from
		the lsr_fiscal_year table rather than the product_info
		table in case the course has registrations but has yet
		to be catalogued by CM."""
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		query = """
			SELECT business_type
			FROM {0}
			WHERE course_code = %s
			LIMIT 1;
		""".format(table_name)
		results = query_mysql(query, (self.course_code,))
		results = as_string(results)
		self.business_type = results


class OverallLearnerNumbers:
	"""Data for a given fiscal year of the Overall Numbers table."""
	def __init__(self, fiscal_year, course_code):
		self.fiscal_year = fiscal_year
		self.course_code = course_code
		# Store results in single list so can be iterated through
		# in templates by single for loop. Keeps code lean.
		self.counts = []
	
	
	def load(self):
		"""Run all queries and process all raw data."""
		self._calc_total_regs()
		self._calc_unique_learners()
		self._calc_total_no_shows()
		# Return self to allow method chaining
		return self
	
	
	def _calc_total_regs(self):
		"""Query total number of confirmed registrations."""
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		query = """
			SELECT COUNT(reg_id)
			FROM {0}
			WHERE course_code = %s AND reg_status = 'Confirmed';
		""".format(table_name)
		results = query_mysql(query, (self.course_code,))
		results_processed = (gettext('Registrations'), as_int(results))
		self.counts.append(results_processed)
	
	
	def _calc_unique_learners(self):
		"""Query total number of unique learners."""
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		query = """
			SELECT COUNT(DISTINCT learner_id)
			FROM {0}
			WHERE course_code = %s AND reg_status = 'Confirmed';
		""".format(table_name)
		results = query_mysql(query, (self.course_code,))
		results_processed = (gettext('Unique Learners'), as_int(results))
		self.counts.append(results_processed)
	
	
	def _calc_total_no_shows(self):
		"""Query total number of no-shows."""
		table_name = 'lsr_{0}'.format(self.fiscal_year)
		query = """
			SELECT SUM(no_show)
			FROM {0}
			WHERE course_code = %s;
		""".format(table_name)
		results = query_mysql(query, (self.course_code,))
		results_processed = (gettext('No-Shows'), as_int(results))
		self.counts.append(results_processed)
