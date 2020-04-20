from datetime import datetime
from typing import List, Union, Dict, Any

from geopy import GoogleV3
from pycountry_convert import country_alpha2_to_continent_code, convert_continent_code_to_continent_name
from tweepy.models import Status


class Tweet:
	"""
	A wrapper around tweepy's Status object.
	"""

	def __init__(self, status: Status):
		"""
		Constructs a new Tweet object from a tweepy's Status object.

		Parameters
		----------
		status : Status
			the provided status

		Properties
		----------
		status : Status
			the provided status

		text : str
			the text
		name : str
			the full name of the author
		username : str
			the username of the author, with the '@' upfront
		hashtags : List[str]
			a list of hashtags, with the '#' upfront
		datetime : datetime
			the date and time at which the tweet was created

		country_code : Union[str, None]
			the country code of the country where the tweet was created (2 capital letters e.g. BE for Belgium)
		continent_name : Union[str, None]
			the name of the continent where the tweet was created (2 capital letters e.g. EU for Europe)

		denier : Union[bool, None]
			the type of the tweet (True = denier, False = acceptor, and None = unknown)
		"""
		self.status: Status = status

		self.text: str = status.full_text
		self.name: str = status.author.name
		self.username: str = f'@{status.author.screen_name}'
		self.hashtags: List[str] = [f'#{hashtag["text"]}' for hashtag in status.entities['hashtags']]
		self.datetime: datetime = status.created_at

		self.country_code: Union[str, None] = None
		self.continent: Union[str, None] = None
		self.add_location(None)

		self.denier: Union[bool, None] = None

	def __str__(self) -> str:
		"""
		Pretty-prints a Tweet object.

		Returns
		-------
		str
			pretty-print of the tweet
		"""
		return f'{self.text}\n \
				Author:\t{self.name}\n \
		        Username:\t{self.username}\n \
		        Country code:\t{self.country_code}\n \
		        Continent:\t{self.continent}\n \
		        Denier?\t{self.denier}'

	def has_hashtag(self, hashtag: str) -> bool:
		"""
		Checks if this tweet contains the provided hashtag.

		Parameters
		----------
		hashtag : str
			the provided hashtag

		Returns
		-------
		bool
			True if the provided hashtag is in the tweet's list of hashtags, else False
		"""
		# check parameters
		assert hashtag is not None, 'Invalid hashtag: hashtag cannot be None'
		assert hashtag is not '', 'Invalid hashtag: hashtag cannot be an empty string'

		return hashtag in self.hashtags

	def has_hashtags(self, hashtags: List[str]) -> bool:
		"""
		Checks if this tweet contains all the provided hashtags.

				Parameters
		----------
		hashtags : List[str]
			the provided hashtags

		Returns
		-------
		bool
			True if all provided hashtags are in the tweet's list of hashtags, else False
		"""
		assert hashtags is not None, 'Invalid hashtags: hashtags cannot be None'
		assert hashtags != [], 'Invalid hashtags: hashtags cannot be an empty list'

		for hashtag in hashtags:
			# check parameters
			assert hashtag is not None, 'Invalid hashtag: hashtag cannot be None'
			assert hashtag is not '', 'Invalid hashtag: hashtag cannot be an empty string'

			if hashtag not in self.hashtags:
				return False

		return True

	def __eq__(self, other) -> bool:
		"""
		Check if the tweet happened at the same time as the other tweet.

		Used for time-based sorting.

		Parameters
		----------
		other : Tweet
			the other tweet, against which the tweet is compared

		Returns
		-------
		True if the tweet happened at the same time as the other tweet, else False
		"""
		return self.datetime == other.datetime

	def __ne__(self, other) -> bool:
		"""
		Check if the tweet happened at the same time as the other tweet.

		Used for time-based sorting.

		Parameters
		----------
		other : Tweet
			the other tweet, against which the tweet is compared

		Returns
		-------
		True if the tweet happened at the same time as the other tweet, else False
		"""
		return not (self == other)

	def __lt__(self, other) -> bool:
		"""
		Check if the tweet happened before the other tweet.

		Used for time-based sorting.

		Parameters
		----------
		other : Tweet
			the other tweet, against which the tweet is compared

		Returns
		-------
		True if the tweet happened before the other tweet, else False
		"""
		return self.datetime < self.datetime

	def __le__(self, other) -> bool:
		"""
		Check if the tweet happened before or at the same time as the other tweet.

		Used for time-based sorting.

		Parameters
		----------
		other : Tweet
			the other tweet, against which the tweet is compared

		Returns
		-------
		True if the tweet happened before or at the same time as the other tweet, else False
		"""
		return self.datetime <= self.datetime

	def __gt__(self, other) -> bool:
		"""
		Check if the tweet happened after the other tweet.

		Used for time-based sorting.

		Parameters
		----------
		other : Tweet
			the other tweet, against which the tweet is compared

		Returns
		-------
		True if the tweet happened after the other tweet, else False
		"""
		return self.datetime > self.datetime

	def __ge__(self, other) -> bool:
		"""
		Check if the tweet happened after or at the same time as the other tweet.

		Used for time-based sorting.

		Parameters
		----------
		other : Tweet
			the other tweet, against which the tweet is compared

		Returns
		-------
		True if the tweet happened after or at the same time as the other tweet, else False
		"""
		return self.datetime >= self.datetime

	def is_denier(self) -> bool:
		"""
		Checks if this tweet is classified as a denier.

		Returns
		-------
		bool
			True if the tweet's type is Type.DENIER, else False
		"""
		return self.denier is True

	def is_acceptor(self) -> bool:
		"""
		Checks if this tweet is classified as an acceptor.

		Returns
		-------
		bool
			True if the tweet's type is Type.ACCEPTOR, else False
		"""
		return self.denier is False

	def is_unknown(self) -> bool:
		"""
		Checks if this tweet is not yet classified.

		Returns
		-------
		bool
			True if the tweet's type is Type.UNKNOWN, else False
		"""
		return self.denier is None

	def to_dict(self):
		"""
		Used to create a pandas dataframe from a list of Tweets.

		Returns
		-------
		dictionary
			dictionary to create pandas dataframe
		"""
		return {
			'name': self.name,
			'username': self.username,
			'hashtags': self.hashtags,
			'datetime': self.datetime,
			'country_code': self.country_code,
			'continent': self.continent,
			'denier': self.denier,
			'text': self.text
		}

	def add_location(self, google_api: Union[GoogleV3, None]) -> None:
		"""
		Adds a location to this tweet by first adding the country code and then the continent name.

		A location is defined by a country code and a continent's name.

		Parameters
		----------
		google_api : GoogleV3
			the Google geolocation API
		"""
		# add the country code first
		self.add_country_code(google_api)
		# then add the continent's name
		self.add_continent_name()

	def add_country_code(self, google_api: Union[GoogleV3, None]) -> None:
		"""
		Adds a country code to this tweet.

		Parameters
		----------
		google_api : GoogleV3
			the Google geolocator API
		"""
		if self.has_country_code():
			# already has country code
			return

		if self.status.place is not None \
				and self.status.place.country_code is not None \
				and len(self.status.place.country_code) == 2:
			# get country code from tweet's status
			self.country_code: str = self.status.place.country_code
			return

		if google_api is not None \
				and self.status.author.location is not None \
				and self.status.author.location != '':
			# use place form author by looking it op on Google's geolocation api
			try:
				location: Any = google_api.geocode(query=self.status.author.location)
				if location is not None \
						and location.raw is not None \
						and location.raw['address_components'] is not None:
					address_component: List[Dict[str, str]] = location.raw['address_components']
					country_code: Union[str, None] = address_component[-1]['short_name'] if 'country' in \
					                                                                        address_component[-1][
						                                                                        'types'] else None
					if country_code is None:
						country_code: Union[str, None] = address_component[-2]['short_name'] if 'country' in \
						                                                                        address_component[-2][
							                                                                        'types'] else None

					self.country_code: Union[str, None] = country_code
					return
			except:
				self.country_code: None = None
				return

		self.country_code: None = None
		return

	def add_continent_name(self) -> None:
		"""
		Adds a continent name to this tweet.
		"""
		if self.has_continent_name():
			# already has a continent name
			return

		if self.country_code is None or len(self.country_code) != 2:
			# incorrect country code
			self.continent: None = None
			return

		if self.country_code == 'AQ':
			# special case
			self.continent: str = 'Antarctica'
			return

		try:
			# return continent name from country code
			self.continent: str = convert_continent_code_to_continent_name(
				country_alpha2_to_continent_code(self.country_code))
			return
		except:
			# return None if this fails
			self.continent: None = None
			return

	def has_location(self) -> bool:
		"""
		Checks if this tweet has a location.

		A location is defined by a country code and a continent's name.

		Returns
		-------
		bool
			True if the tweet has a location else False
		"""
		if self.has_country_code() and self.has_continent_name():
			# has a location
			return True

		# has no location
		return False

	def has_country_code(self) -> bool:
		if self.country_code is not None and len(self.country_code) == 2:
			# has country code
			return True

		# has no country code
		return False

	def has_continent_name(self) -> bool:
		if self.continent is not None and self.continent != '':
			# has a continent name
			return True

		# has no continent name
		return False
