from collections import defaultdict
from datetime import datetime
from typing import List

from tweet import Tweet


def filter_by_hashtag(tweets: List[Tweet], hashtag: str) -> List[Tweet]:
	"""
		Filter tweets by hashtag.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	hashtag : str
	    The hashtag on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects with the provided hashtag
	"""
	return [tweet for tweet in tweets if tweet.has_hashtag(hashtag)]


def filter_by_hashtags_all(tweets: List[Tweet], hashtags: List[str]) -> List[Tweet]:
	"""
		Filter tweets by hashtag.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	hashtags : List[str]
	    The hashtags on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects with all of the provided hashtags
	"""
	return [tweet for tweet in tweets if tweet.has_hashtags(hashtags)]


def filter_by_hashtags_any(tweets: List[Tweet], hashtags: List[str]) -> List[Tweet]:
	"""
		Filter tweets by hashtag.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	hashtags : List[str]
	    The hashtags on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects with any of the provided hashtags
	"""
	filtered_tweets = []
	for tweet in tweets:
		for hashtag in tweet.hashtags:
			if hashtag in hashtags:
				filtered_tweets.append(tweet)
				break
	return filtered_tweets


def filter_after(tweets: List[Tweet], after: datetime) -> List[Tweet]:
	"""
		Filter tweets by datetime.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	after: datetime
	    The datetime on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted after the provided datetime
	"""
	return [tweet for tweet in tweets if tweet.datetime > after]


def filter_before(tweets: List[Tweet], before: datetime) -> List[Tweet]:
	"""
		Filter tweets by datetime.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	before: datetime
	    The datetime on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted before the provided datetime
	"""
	return [tweet for tweet in tweets if tweet.datetime < before]


def filter_at(tweets: List[Tweet], at: datetime) -> List[Tweet]:
	"""
		Filter tweets by datetime.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	at: datetime
	    The datetime on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted at the provided datetime
	"""
	return [tweet for tweet in tweets if tweet.datetime == at]


def filter_between(tweets: List[Tweet], after: datetime, before: datetime) -> List[Tweet]:
	"""
		Filter tweets by datetime.

	This is equivalent to calling filter_after and filter_before after one another.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	after: datetime
	    The datetime on which to filter tweets
	before: datetime
	    The datetime on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted between the provided datetimes
	"""
	return [tweet for tweet in tweets if after <= tweet.datetime <= before]


def filter_by_country_code(tweets: List[Tweet], country_code: str) -> List[Tweet]:
	"""
		Filter tweets by location.

	Parameters
	----------
	tweets : List[Tweet]
		The list of tweets
	country_code: str
		The country code on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted from country with the provided country code
	"""
	return [tweet for tweet in tweets if tweet.country_code == country_code]


def filter_by_country_codes(tweets: List[Tweet], country_codes: List[str]) -> List[Tweet]:
	"""
		Filter tweets by location.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	country_codes: List[str]
	    The country codes on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted from countries with the provided country codes
	"""
	return [tweet for tweet in tweets if tweet.country_code in country_codes]


def filter_by_continent(tweets: List[Tweet], continent: str) -> List[Tweet]:
	"""
		Filter tweets by location.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	continent: str
	    The continent on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted from the provided continent
	"""
	return [tweet for tweet in tweets if tweet.continent == continent]


def filter_by_continents(tweets: List[Tweet], continents: List[str]) -> List[Tweet]:
	"""
		Filter tweets by location.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets
	continents: List[str]
	    The continents on which to filter tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, tweeted from the provided continents
	"""
	return [tweet for tweet in tweets if tweet.continent in continents]


def sort_by_date_ascending(tweets: List[Tweet]) -> List[Tweet]:
	"""
		Sort tweets by datetime.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, sorted in ascending order
	"""
	return sorted(tweets, key=lambda tweet: tweet.datetime, reverse=False)


def sort_by_date_descending(tweets: List[Tweet]) -> List[Tweet]:
	"""
		Sort tweets by datetime.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets

	Returns
	-------
	List[Tweet]
		A list of Tweet objects, sorted in descending order
	"""
	return sorted(tweets, key=lambda tweet: tweet.datetime, reverse=True)


def group_by_country_code(tweets: List[Tweet]) -> defaultdict:
	"""
		Group tweets by location.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets

	Returns
	-------
	defaultdict
		A dictionary of country codes to lists of Tweet objects, grouped by country code
	"""
	split: defaultdict = defaultdict(list)
	[split[tweet.country_code].append(tweet) for tweet in tweets if tweet.country_code is not None]

	return split


def group_by_continent(tweets: List[Tweet]) -> defaultdict:
	"""
		Group tweets by location.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets

	Returns
	-------
	defaultdict
		A dictionary of continent to lists of Tweet objects, grouped by continent
	"""
	split: defaultdict = defaultdict(list)
	[split[tweet.continent].append(tweet) for tweet in tweets if tweet.continent is not None]

	return split


def group_by_denier(tweets: List[Tweet]) -> defaultdict:
	"""
		Group tweets by denier.

	Parameters
	----------
	tweets : List[Tweet]
	    The list of tweets

	Returns
	-------
	defaultdict
		A dictionary of booleans to lists of Tweet objects, grouped by denier
	"""
	split: defaultdict = defaultdict(list)
	[split[tweet.denier].append(tweet) for tweet in tweets if tweet.denier is not None]

	return split
