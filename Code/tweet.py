from datetime import datetime
from typing import List, Union

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
			a list of hashtags
		datetime : datetime
			the date and time at which the tweet was created
		country_code : Union[str, None]
			the country code of the country where the tweet was created (2 capital letters e.g. BE for Belgium)
		continent : Union[str, None]
			the name of the continent where the tweet was created (2 capital letters e.g. EU for Europe)

		denier : Union[bool, None]
			the type of the tweet (True = denier, False = acceptor, and None = unknown)
		"""
		self.status: Status = status

		self.text: str = status.full_text
		self.name: str = status.author.name
		self.username: str = f'@{status.author.screen_name}'
		self.hashtags: List[str] = status.entities['hashtags']
		self.datetime: datetime = status.created_at
		self.country_code: Union[str, None] = status.place.country_code if status.place is not None else None
		self.continent: Union[str, None] = convert_continent_code_to_continent_name(
			country_alpha2_to_continent_code(status.place.country_code)) if status.place is not None else None

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

	# hashtags
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

	# date and time
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

	# denier vs acceptor
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
