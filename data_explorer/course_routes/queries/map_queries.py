from data_explorer.db import query_mysql


class Map:
	"""Data for the Maps tab."""
	def __init__(self, lang, table_year, fiscal_year, course_code):
		self.lang = lang
		self.table_year = table_year
		self.fiscal_year = fiscal_year
		self.course_code = course_code
		self.offerings = None
		self.learners = None
	
	
	def load(self):
		"""Run all queries and process all raw data."""
		self._offering_cities()
		self._learner_cities()
		# Return self to allow method chaining
		return self
	
	
	def _offering_cities(self):
		"""Returns a list of cities in which offerings took place. Each nested
		list holds city name, number of offerings, latitude, and longitude.
		"""
		field_name = 'offering_city_{0}'.format(self.lang)
		# Sort by count so that when overlapping markers are combined by function
		# _combine_overlapping_cities_hashed, it's the city with the largest count into
		# which all others all merged
		query = """
			SELECT {0}, COUNT(offering_id), offering_lat, offering_lng
			FROM offerings
			WHERE
				course_code = %s
				AND
				offering_status IN ('Open - Normal', 'Delivered - Normal')
				AND
				fiscal_year = %s
			GROUP BY 1
			ORDER BY 2 DESC;
		""".format(field_name)
		results = query_mysql(query, (self.course_code, self.fiscal_year))
		# Process into format required by Highcharts
		results = [[element for element in tup] for tup in results if tup[2] is not None]
		results = self._combine_overlapping_cities_hashed(results)
		self.offerings = results
	
	
	def _learner_cities(self):
		"""Returns a list of cities in which learners are located. Each nested
		list holds city name, number of learners, latitude, and longitude.
		"""
		field_name = 'learner_city_{0}'.format(self.lang)
		table_name = 'lsr_{0}'.format(self.table_year)
		# Sort by count so that when overlapping markers are combined by function
		# _combine_overlapping_cities_hashed, it's the city with the largest count into
		# which all others all merged
		query = """
			SELECT {0}, COUNT(DISTINCT learner_id), learner_lat, learner_lng
			FROM {1}
			WHERE course_code = %s AND reg_status = 'Confirmed'
			GROUP BY 1
			ORDER BY 2 DESC;
		""".format(field_name, table_name)
		results = query_mysql(query, (self.course_code,))
		# Process into format required by Highcharts
		results = [[element for element in tup] for tup in results if tup[2] is not None]
		results = self._combine_overlapping_cities_hashed(results)
		self.learners = results
	
	
	@staticmethod
	def _combine_overlapping_cities_hashed(my_list, verbose=False):
		"""If two cities' markers overlap, combine them into a single entry.
		
		Parameters
		----------
		
		my_list: list
			List of lists. Each nested list has form ['city_name', count,
			latitude, longitude].
		
		verbose: boolean, default False
			Print names of cities being merged.
		
		Explanation: Use latitude and longitude rounded to N_DIGITS to create
		a PKEY for each city. Rounding will cause nearby cities to have the
		same PKEY.
		
		Largest city chosen: As SQL queries make use of 'ORDER BY COUNT() DESC',
		the	largest	cities appear and are logged first. This means that e.g. 2
		occurrences of Kanata will be merged into Ottawa's 30 occurrences.
		"""
		N_DIGITS = 3
		merge_dict = {}
		for elem in my_list:
			city_name = elem[0]
			count = elem[1]
			# Python's 'round' internal func uses technique 'round half to even'
			# https://en.wikipedia.org/wiki/Rounding#Round_half_to_even
			lat = round(elem[2], N_DIGITS)
			lng = round(elem[3], N_DIGITS)
			pkey = str(lat) + str(lng)
			# Log first occurrence
			if pkey not in merge_dict:
				# Log non-rounded values for maximum accuracy
				merge_dict[pkey] = [city_name, count, float(elem[2]), float(elem[3])]
			# If lat/lng already logged, combine cities
			else:
				if verbose:
					print(f'Merging {city_name} into {merge_dict[pkey][0]}')
				merge_dict[pkey][1] += count
		# Return merge_dict's values in list
		results = [value for value in merge_dict.values()]
		return results
