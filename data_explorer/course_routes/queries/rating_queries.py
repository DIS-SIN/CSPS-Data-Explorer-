import pandas as pd
from data_explorer.db import query_mysql


class Ratings:
	"""Data for the Ratings section of the Comments tab."""
	def __init__(self, course_code, fiscal_year):
		self.course_code = course_code
		self.fiscal_year = fiscal_year
		self.data = None
		self.processed = None
	
	
	def load(self):
		"""Run all queries and process all raw data."""
		self.data = self._load_ratings()
		self.processed = self._process_ratings()
		# Return self to allow method chaining
		return self
	
	
	def _load_ratings(self):
		"""Query the DB and extract all ratings data for a given course code."""
		query = """
			SELECT original_question, month_en, AVG(numerical_answer), COUNT(survey_id)
			FROM ratings
			WHERE
				course_code = %s
				AND
				fiscal_year = %s
				AND
				original_question IN (
					'3. Satisfaction - Level of detail of the content',
					'4. Satisfaction - Quality of the content',
					'5. Satisfaction - Language quality of the materials (English or French)',
					'6. Satisfaction - Quality of the graphics',
					'7. Satisfaction  Ease of navigation',
					'10. Before this learning activity',
					'11. After this learning activity',
					'20. This learning activity is a valuable use of my time',
					'21. This learning activity is relevant to my job',
					'22. This learning activity is contributing to my performance on the job',
					'23. I can apply what I have learned on the job'
				)
			GROUP BY 1, 2;
		"""
		results = query_mysql(query, (self.course_code, self.fiscal_year))
		results = pd.DataFrame(results, columns=['original_question', 'month', 'average', 'count'])
		# Return False if course has received no feedback
		return False if results.empty else results
	
	
	def _process_ratings(self):
		"""Extract and process results for all possible ratings from the raw data.
		Returns False if course has received no feedback of that type.
		"""
		# Explicitely checking 'if df is False' rather than 'if not df' as
		# DataFrames do not have a truth value
		if self.data is False:
			return {}
		# Get list of questions for which the course has answers
		questions = self.data.loc[:, 'original_question'].unique()
		# Process into form required by Highcharts
		results_processed = {}
		for question in questions:
			data_filtered = self.data.loc[self.data['original_question'] == question, ['month', 'average', 'count']]
			monthly_values = _get_monthly_values(data_filtered)
			results_processed[question] = monthly_values
		return results_processed


class OverallSatisfaction:
	"""Data for the Overall Satisfaction section of the Comments tab. Display results
	for either the old 1 to 5 question or the new 1 to 10 Nanos question, depending
	of value of bool 'old_survey'.
	"""
	def __init__(self, course_code, fiscal_year, old_survey=False):
		self.course_code = course_code
		self.fiscal_year = fiscal_year
		self.old_survey = old_survey
		self.data = None
		self.processed = None
	
	
	def load(self):
		"""Run query and process raw data."""
		self.data = self._load_raw()
		self.processed = self._process_raw()
		# Return self to allow method chaining
		return self
	
	
	def _load_raw(self):
		"""Query the DB and extract all overall satisfaction data for a
		given course code.
		"""
		original_question = 'Overall Satisfaction' if self.old_survey else '1. Satisfaction Overall'
		query = """
			SELECT month_en, AVG(numerical_answer), COUNT(survey_id)
			FROM ratings
			WHERE
				course_code = %s
				AND
				fiscal_year = %s
				AND
				original_question = '{0}'
			GROUP BY 1;
		""".format(original_question)
		results = query_mysql(query, (self.course_code, self.fiscal_year))
		results = pd.DataFrame(results, columns=['month', 'average', 'count'])
		# Return False if course has received no feedback
		return False if results.empty else results
	
	
	def _process_raw(self):
		"""Extract and process results for all possible ratings from the raw data.
		Returns False if course has received no feedback of that type.
		"""
		# Explicitely checking 'if df is False' rather than 'if not df' as
		# DataFrames do not have a truth value
		if self.data is False:
			return []
		# Process into form required by Highcharts
		results_processed = _get_monthly_values(self.data)
		return results_processed


def _get_monthly_values(df):
	"""Accepts a Panda's DataFrame with columns ['month', 'average', and 'count'].
	Returns	a list of dicts ensuring all possible months have values. Months
	not listed in DataFrame assigned average and count of 0."""
	months = ['April', 'May', 'June', 'July', 'August', 'September',
			  'October', 'November', 'December', 'January', 'February', 'March']
	monthly_values = []
	for month in months:
		df_month = df.loc[df['month'] == month, :]
		try:
			average = float(round(df_month.iloc[0]['average'], 2))
			count = int(df_month.iloc[0]['count'])
		except IndexError:
			average = None
			count = None
		monthly_values.append({'y': average, 'count': count})
	return monthly_values
