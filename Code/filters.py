from collections import defaultdict
from datetime import datetime
from typing import List

from tweet import Tweet


def filter_by_hashtag(tweets: List[Tweet], hashtag: str) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.has_hashtag(hashtag)]


def filter_by_hashtags_all(tweets: List[Tweet], hashtags: List[str]) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.has_hashtags(hashtags)]


def filter_by_hashtags_any(tweets: List[Tweet], hashtags: List[str]) -> List[Tweet]:
	filtered_tweets = []
	for tweet in tweets:
		for hashtag in tweet.hashtags:
			if hashtag in hashtags:
				filtered_tweets.append(tweet)
				break
	return filtered_tweets


def filter_before(tweets: List[Tweet], before: datetime) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.datetime < before]


def filter_at(tweets: List[Tweet], at: datetime) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.datetime == at]


def filter_after(tweets: List[Tweet], after: datetime) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.datetime > after]


def filter_between(tweets: List[Tweet], after: datetime, before: datetime) -> List[Tweet]:
	return [tweet for tweet in tweets if after <= tweet.datetime <= before]


def filter_by_country_code(tweets: List[Tweet], country_code: str) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.country_code == country_code]


def filter_by_country_codes(tweets: List[Tweet], country_codes: List[str]) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.country_code in country_codes]


def filter_by_continent(tweets: List[Tweet], continent: str) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.continent == continent]


def filter_by_continents(tweets: List[Tweet], continents: List[str]) -> List[Tweet]:
	return [tweet for tweet in tweets if tweet.continent in continents]


def sort_by_date_ascending(tweets: List[Tweet]) -> List[Tweet]:
	return sorted(tweets, key=lambda tweet: tweet.datetime, reverse=False)


def sort_by_date_descending(tweets: List[Tweet]) -> List[Tweet]:
	return sorted(tweets, key=lambda tweet: tweet.datetime, reverse=True)


def group_by_country_code(tweets: List[Tweet]) -> defaultdict:
	split: defaultdict = defaultdict(list)
	[split[tweet.country_code].append(tweet) for tweet in tweets if tweet.country_code is not None]

	return split


def group_by_continent(tweets: List[Tweet]) -> defaultdict:
	split: defaultdict = defaultdict(list)
	[split[tweet.continent].append(tweet) for tweet in tweets if tweet.continent is not None]

	return split


def group_by_denier(tweets: List[Tweet]) -> defaultdict:
	split: defaultdict = defaultdict(list)
	[split[tweet.denier].append(tweet) for tweet in tweets if tweet.denier is not None]

	return split
