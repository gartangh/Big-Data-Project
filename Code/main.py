import pickle
from collections import defaultdict
from typing import List, Dict

import tweepy
from tweet import Tweet
from visualization import visualize


def main():
	if not LOAD:
		# read API keys
		with open('tokens.txt') as f:
			consumer_key = f.readline().strip()
			consumer_secret = f.readline().strip()
			access_token = f.readline().strip()
			access_token_secret = f.readline().strip()
			geocoding_api_key = f.readline().strip()

		# connect with the twitter api
		api: tweepy.API = connect(consumer_key, consumer_secret, access_token, access_token_secret)

		# initialize geocoding api
		Tweet.init(geocoding_api_key)

		# define number of tweets to retrieve
		num_tweets: int = 100

		# define keywords
		# keywords = COVID_KEYWORDS[:2]  # corona and covid
		keywords = COVID_FAKE_KEYWORDS

		# get all tweets in a list
		tweets: List[Tweet] = get_tweets(api, num_tweets, keywords, language='en')
		with open(tweets_path, 'wb') as f:
			pickle.dump(tweets, f)

		tweets_with_place: List[Tweet] = [tweet for tweet in tweets if tweet.country_code is not None]
		with open(tweets_places_path, 'wb') as f:
			pickle.dump(tweets_with_place, f)
	else:
		with open(tweets_path, 'rb') as f:
			tweets = pickle.load(f)

		with open(tweets_places_path, 'rb') as f:
			tweets_with_place = pickle.load(f)

	print(f'number of tweets: {len(tweets)}')
	# print(tweets[0])
	print(f'number of tweets with a place: {len(tweets_with_place)}')
	# print(tweets_with_place[0])

	num_tweets_per_country_per_continent_absolute = defaultdict(lambda: defaultdict(int))
	num_tweets_per_country_absolute = defaultdict(lambda: defaultdict(int))
	num_tweets_per_continent_absolute = defaultdict(lambda: defaultdict(int))
	for tweet in tweets_with_place:
		country_code: str = tweet.country_code.lower()
		continent: str = CONTINENTS[tweet.continent]

		num_tweets_per_country_per_continent_absolute[tweet.continent][country_code] += 1
		num_tweets_per_country_absolute['World'][country_code] += 1
		num_tweets_per_continent_absolute['World'][continent] += 1

	# visualization
	title = 'Absolute number of tweets per country and per continent'
	series = num_tweets_per_country_per_continent_absolute
	filename = 'num_tweets_per_country_per_continent_absolute'
	visualize(title, series, filename, per_continent=False)

	title = 'Absolute number of tweets per country'
	series = num_tweets_per_country_absolute
	filename = 'num_tweets_per_country_absolute'
	visualize(title, series, filename, per_continent=False)

	title = 'Absolute number of tweets per continent'
	series = num_tweets_per_continent_absolute
	filename = 'num_tweets_per_continent_absolute'
	visualize(title, series, filename, per_continent=True)


def connect(consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str) -> tweepy.API:
	"""
	Connect to the Twitter API.

	Parameters
	----------
	consumer_key : str
	    The consumer key as can be found on the Twitter App Page
	consumer_secret : str
	    The consumer_secret as can be found on the Twitter App Page
	access_token : str
	    The access_token as can be found on the Twitter App Page
	access_token_secret : str
	    The acces_token_secret as can be found on the Twitter App Page

	Returns
	-------
	api : tweepy.API
	    The object to interact with the Twitter API
	"""

	# authenticate using keys
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	# calling the api
	api = tweepy.API(auth, wait_on_rate_limit=True)

	return api


def get_tweets(api: tweepy.API, num_tweets: int, keywords: List[str], language: str = 'en') -> List[Tweet]:
	"""
	Get latest tweets from Twitter and create a list of Tweet Objects.

	Parameters
	----------
	api : tweepy.API
	    The object to interact with the Twitter API
	num_tweets : int
	    The number of tweets to collect
	keywords : List[str]
	    The keywords on which to filter tweets
	language : str
	    The language on which to filter tweets

	Returns
	-------
	tweets : 'tweepy.models.ResultSet
		A list of Tweet objects containing the latest number_of_tweets tweets.
	"""
	tweets = []
	for keyword in keywords:
		searched_tweets = []
		last_id = -1
		while len(searched_tweets) < num_tweets:
			count = num_tweets - len(searched_tweets)
			try:
				new_tweets = api.search(q=f'{keyword} -filter:retweets', lang=language, tweet_mode='extended',
				                        count=count, max_id=str(last_id - 1))
				if not new_tweets:
					break
				searched_tweets.extend(new_tweets)
				last_id = new_tweets[-1].id
			except tweepy.TweepError:
				break
		tweets.extend([Tweet(status) for status in searched_tweets])
		print("Keyword '" + str(keyword) + "' finished with number of tweets = " + str(len(tweets)))

	return tweets


if __name__ == "__main__":
	COVID_KEYWORDS: List[str] = ['corona',
	                             'covid',
	                             'quaranteen',
	                             'home',
	                             'stay',
	                             'inside',
	                             'virology',
	                             'doctor',
	                             'nurse',
	                             'virus',
	                             'grandma',
	                             'vaccin',
	                             'sars',
	                             'alone',
	                             'strongtogether',
	                             'elbow',
	                             'mouth mask',
	                             'protective equipment',
	                             'hospitalization',
	                             'increas',
	                             'death',
	                             'dead',
	                             'impact',
	                             'ICU',
	                             'intensive care',
	                             'applause',
	                             'stay healthy',
	                             'take care',
	                             'risk',
	                             'risk group',
	                             'environment',
	                             'U+1F637',  # Medical Mask Emoji
	                             'U+1F691',  # Amublance Emoji
	                             'U+1F92E',  # Vomiting Emoji
	                             'U+1F912'  # Thermometer Emoji
	                             ]

	COVID_FAKE_KEYWORDS: List[str] = [
		'coronascam',
		'fakecorona',
		'fake',
		'coronahoax',
		'hoaxcorona',
		'gooutside',
		'donotstayhome'
		'fuckvirology',
		'donttrustvirologists',
		'coronadoesntexist',
		'chinesevirushoax'
	]

	CONTINENTS: Dict[str, str] = {
		'Asia': 'asia',
		'Europe': 'europe',
		'Africa': 'africa',
		'North America': 'north_america',
		'South America': 'south_america',
		'Oceania': 'oceania',
		'Antarctica': 'antartica',
	}

	LOAD: bool = True

	tweets_path: str = 'tweets/nlp/tweets_fake_en_all_446.pickle'
	tweets_places_path: str = 'tweets/nlp/tweets_with_place_fake_en_all_446.pickle'

	main()
