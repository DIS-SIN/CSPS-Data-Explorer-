import pandas as pd
from flask_babel import gettext
from data_explorer.db import query_mysql


class Comments:
	"""Fetch comments for the API."""
	def __init__(self, lang, course_code, short_question, fiscal_year, stars, limit, offset):
		self.lang = lang
		self.course_code = course_code
		self.short_question = short_question
		self.fiscal_year = fiscal_year
		self.stars = stars
		self.limit = limit
		self.offset = offset
		# Raw data returned by query
		self.raw = None
		# Processed data
		self.processed = None
	
	
	def load(self):
		"""Run query and process raw data."""
		self.raw = self._load_raw()
		self.processed = self._process_raw()
		# Return self to allow method chaining
		return self
	
	
	def _load_raw(self):
		"""Query the DB and extract all comments of a given type for
		self.course_code.
		"""
		field_name = 'offering_city_{0}'.format(self.lang)
		query = """
			SELECT text_answer, {0}, fiscal_year, quarter, stars, nanos
			FROM comments
			WHERE
				course_code = %s
				AND
				short_question = %s
				AND
				(fiscal_year = %s OR %s = '')
				AND
				(stars = %s OR %s = '')
			ORDER BY 4 DESC, 5 DESC
			LIMIT %s OFFSET %s;
		""".format(field_name)
		results = query_mysql(query, (self.course_code,
									  self.short_question,
									  self.fiscal_year, self.fiscal_year,
									  self.stars, self.stars,
									  int(self.limit), int(self.offset)))
		results = pd.DataFrame(results, columns=['text_answer', 'offering_city',
												 'fiscal_year', 'quarter', 'stars', 'nanos'])
		# Account for learners who didn't submit stars with their comments
		results['stars'].fillna(0, inplace=True)
		# Return False if course has received no feedback
		return False if results.empty else results
	
	
	def _process_raw(self):
		""" Parse raw data with Pandas and process into form required for API.
		Return False if course has received no comments.
		"""
		# Explicitely checking 'if df is False' rather than 'if not df' as
		# DataFrames do not have a truth value
		if self.raw is False:
			return False
		results_processed = []
		# Unpack tuple as some fields require customization
		for row in self.raw.itertuples(index=False):
			text_answer = row[0]
			# Account for English vs French title formatting
			offering_city = self._format_title(row[1])
			fiscal_year = row[2]
			# Account for e.g. 'Q2' being 'T2' in FR
			quarter = row[3].replace('Q', 'T') if self.lang == 'fr' else row[3]
			stars = int(row[4])
			nanos = row[5]
			# Reassemble and append
			tup = (text_answer, offering_city, fiscal_year, quarter, stars, nanos)
			results_processed.append(tup)
		return results_processed
	
	
	def _format_title(self, my_string):
		"""Correct English and French formatting edge cases."""
		if self.lang == 'fr':
			s = my_string.title()
			s = s.replace('Région De La Capitale Nationale (Rcn)', 'Région de la capitale nationale (RCN)').replace("En Ligne", "En ligne").replace("'S", "'s")
			return s
		else:
			s = my_string.title()
			s = s.replace('(Ncr)', '(NCR)').replace("'S", "'s")
			return s


class CommentCounts:
	"""Fetch number of comments by star for a given course code, question,
	and fiscal year for the API.
	"""
	def __init__(self, course_code, short_question, fiscal_year):
		self.course_code = course_code
		self.short_question = short_question
		self.fiscal_year = fiscal_year
		# Raw data returned by query
		self.raw = None
		# Processed data
		self.processed = None
	
	
	def load(self):
		"""Run query and process raw data."""
		self.raw = self._load_raw()
		self.processed = self._process_raw()
		# Return self to allow method chaining
		return self
	
	
	def _load_raw(self):
		"""Query the DB and extract number of comments by star."""
		query = """
			SELECT stars, COUNT(survey_id)
			FROM comments
			WHERE
				course_code = %s
				AND
				short_question = %s
				AND
				(fiscal_year = %s OR %s = '')
			GROUP BY 1;
		"""
		results = query_mysql(query, (self.course_code, self.short_question,
									  self.fiscal_year, self.fiscal_year))
		return dict(results)
	
	
	def _process_raw(self):
		"""Ensure all stars from 1-5 present in dict."""
		stars = range(1, 6)
		results_processed = {star: self.raw.get(star, 0) for star in stars}
		return results_processed


class Categorical:
	"""Data for the Categorical section of the Comments tab."""
	def __init__(self, lang, course_code):
		self.lang = lang
		self.course_code = course_code
		# Raw data returned by query
		self.categorical_data = None
		# Processed data
		self.expectations = None
		self.recommend = None
		self.gccampus = None
		self.videos = None
		self.blogs = None
		self.forums = None
		self.job_aids = None
	
	
	def load(self):
		"""Run query and process raw data."""
		self.categorical_data = self._load_all_categorical()
		# Parse with Pandas and process into form required by Highcharts
		self.expectations = self._load_categorical('12. Expectations Met')
		self.recommend = self._load_categorical('13. Recommend learning Activity')
		self.gccampus = self._load_categorical('14. GCCampus Usage')
		self.videos = self._load_categorical('15. Videos')
		self.blogs = self._load_categorical('16. Blogs')
		self.forums = self._load_categorical('17. Forums')
		self.job_aids = self._load_categorical('18. Job aids')
		# Return self to allow method chaining
		return self
	
	
	def _load_all_categorical(self):
		"""Query the DB and extract all categorical question data for a given course code."""
		field_name = 'text_answer_{0}'.format(self.lang)
		query = """
			SELECT original_question, {0}, COUNT({0})
			FROM ratings
			WHERE
				course_code = %s
				AND
				original_question IN (
					'12. Expectations Met', '13. Recommend learning Activity', '14. GCCampus Usage',
					'15. Videos', '16. Blogs', '17. Forums', '18. Job aids'
				)
			GROUP BY 1, 2
			ORDER BY 1 ASC;
		""".format(field_name)
		results = query_mysql(query, (self.course_code,))
		results = pd.DataFrame(results, columns=['original_question', 'text_answer', 'count'])
		# Return False if course has received no feedback
		return False if results.empty else results
	
	
	def _load_categorical(self, question):
		"""Extract and process results for a categorical question from the raw
		data. Returns False if course has received no feedback of that type.
		"""
		# Explicitely checking 'if df is False' rather than 'if not df' as
		# DataFrames do not have a truth value
		if self.categorical_data is False:
			return False
		data_filtered = self.categorical_data.loc[self.categorical_data['original_question'] == question, :]
		results_processed = []
		for row in data_filtered.itertuples(index=False):
			# Unpack tuple as some fields require customization
			answer = row[1]
			count = row[2]
			# Reassemble and append
			dict_ = {'name': answer, 'y': count}
			results_processed.append(dict_)
		return results_processed if results_processed else [{'name': gettext('No response'), 'y': 1}]
