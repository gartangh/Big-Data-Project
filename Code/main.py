import pickle
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Tuple, Union

import nltk
import tweepy
from filters import filter_by_hashtag, filter_by_hashtags_all, filter_by_hashtags_any, filter_before, filter_at, filter_after, filter_between, \
	filter_by_country_code, filter_by_country_codes, filter_by_continent, filter_by_continents, sort_by_date_ascending, \
	sort_by_date_descending, group_by_country_code, group_by_continent
from geopy import GoogleV3
from nltk import re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.tree import DecisionTreeClassifier
from tweet import Tweet
from visualization import visualize


def main():
	print()
	########################
	# 1. GET NEW DATASET
	# 2. ADD LOCATIONS
	# 3. TRAIN CLASSIFIERS
	# 4. MAKE PREDICTIONS
	# 5. FILTER, SORT, GROUP
	# 6. VISUALIZE
	########################

	####################
	# 1. GET NEW DATASET
	####################
	print('\n1. GET NEW DATASET')
	# read Twitter tokens
	consumer_key, consumer_secret, access_token, access_token_secret = read_twitter_tokens('tokens/twitter_tokens.txt')
	# connect with the Twitter API
	twitter_api: tweepy.API = connect_to_twitter_api(consumer_key, consumer_secret, access_token, access_token_secret)
	# define keywords
	# define keywords
	# COVID_KEYWORDS: List[str] = [
	# 	'corona', 'covid', 'quaranteen', 'home', 'stay', 'inside', 'virology', 'doctor', 'nurse', 'virus', 'grandma',
	# 	'vaccin', 'sars', 'alone', 'strongtogether', 'elbow', 'mouth mask', 'protective equipment', 'hospitalization',
	# 	'increas', 'death', 'dead', 'impact', 'ICU', 'intensive care', 'applause', 'stay healthy', 'take care', 'risk',
	# 	'risk group', 'environment',
	# 	'U+1F637',  # Medical Mask Emoji
	# 	'U+1F691',  # Amublance Emoji
	# 	'U+1F92E',  # Vomiting Emoji
	# 	'U+1F912',  # Thermometer Emoji
	# ]
	# COVID_FAKE_KEYWORDS: List[str] = [
	# 	'coronascam', 'fakecorona', 'fake', 'coronahoax', 'hoaxcorona', 'gooutside', 'donotstayhome''fuckvirology',
	# 	'donttrustvirologists', 'coronadoesntexist', 'chinesevirushoax',
	# ]
	keywords: Dict[str, int] = {
		'covid': 10,  # get 100 tweets with 'covid' in it
		'corona': 10,  # get 100 tweet with 'corona' in it
		'coronahoax': 10,  # get tweets 100 with 'coronahoax' in it
	}
	# get new dataset
	new_dataset: List[Tweet] = get_new_tweets(twitter_api, keywords)
	print(f'First tweet:\n{new_dataset[0]}')
	# save new dataset
	save_tweets(new_dataset, 'tweets/new_dataset.pickle')

	##################
	# 2. ADD LOCATIONS
	##################
	# print('\n2. ADD LOCATION TO THOSE TWEETS')
	# # read Google token
	# geocoding_api_key: str = read_google_token('tokens/google_token.txt')
	# # initialize Google API
	# google_api: GoogleV3 = GoogleV3(api_key=geocoding_api_key)
	# # add location to tweets when possible
	# num_tweets_with_location_before: int = 0
	# num_tweets_with_location_after: int = 0
	# for tweet in new_dataset:
	# 	if tweet.country_code is not None and tweet.continent is not None:
	# 		num_tweets_with_location_before += 1
	# 	tweet.add_location(google_api)
	# 	if tweet.country_code is not None and tweet.continent is not None:
	# 		num_tweets_with_location_after += 1
	# print(f'Number of tweets with location before: {num_tweets_with_location_before}')
	# print(f'Number of tweets with location after: {num_tweets_with_location_after}')
	# # save new dataset with locations included
	# save_tweets(new_dataset, 'tweets/new_dataset.pickle')

	######################
	# 3. TRAIN CLASSIFIERS
	######################
	print('\n3. TRAIN CLASSIFIERS')
	# load train dataset
	train_dataset = load_tweets('tweets/train_dataset.pickle')
	# pre-process train dataset
	X: List[str] = [tweet.text for tweet in train_dataset]
	X: List[str] = preprocess_corpus(X)
	labels: List[bool] = [tweet.denier for tweet in train_dataset]

	# train on part of the data
	# train, validation split
	X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2)
	# vectorize
	vectorizer: CountVectorizer = CountVectorizer()
	X_train = vectorizer.fit_transform(X_train)
	X_test = vectorizer.transform(X_test)

	# create Complement Naive Bayes classifier
	naive_bayes_classifier = ComplementNB()
	# train Complement Naive Bayes classifier
	naive_bayes_classifier = naive_bayes_classifier.fit(X_train, y_train)
	# validate Complement Naive Bayes classifier
	naive_bayes_accuracy: float = naive_bayes_classifier.score(X_test, y_test)
	print(f'Naive Bayes accuracy:\t{naive_bayes_accuracy * 100:>3.2f}%')
	# save Naive Bayes classifier
	save_model(naive_bayes_classifier, 'models/naive_bayes.pickle')

	# create Decision Tree classifier
	decision_tree_classifier = DecisionTreeClassifier()
	# train Decision Tree classifier
	decision_tree_classifier = decision_tree_classifier.fit(X_train, y_train)
	# validate Decision Tree classifier
	decision_tree_accuracy: float = decision_tree_classifier.score(X_test, y_test)
	print(f'Decision Tree accuracy:\t{decision_tree_accuracy * 100:>3.2f}%')
	# save Decision Tree classifier
	save_model(decision_tree_classifier, 'models/decision_tree.pickle')

	# retrain best model on all of the data
	# vectorize
	vectorizer: CountVectorizer = CountVectorizer()
	X: List[str] = vectorizer.fit_transform(X)
	best_model = ComplementNB().fit(X, labels) \
		if naive_bayes_accuracy >= decision_tree_accuracy \
		else DecisionTreeClassifier().fit(X, labels)
	# save best mode
	save_model(best_model, 'models/best_model.pickle')

	#####################
	# 4. MAKE PREDICTIONS
	#####################
	print('\n4. USE CLASSIFIERS')
	# load test dataset
	test_dataset = load_tweets('tweets/test_dataset.pickle')

	# pre-processing
	X: List[str] = [tweet.text for tweet in test_dataset]
	X: List[str] = preprocess_corpus(X)
	# vectorize
	X = vectorizer.transform(X)
	# make predictions
	y = best_model.predict(X)

	# add predictions to tweet
	for tweet, label in zip(test_dataset, y):
		tweet.denier = label

	########################
	# 5. FILTER, SORT, GROUP
	########################
	print('\n5. USE VARIOUS FILTERS')
	# use filters
	tweets_filtered_by_hashtag: List[Tweet] = filter_by_hashtag(test_dataset, '#coronahoax')
	tweets_filtered_by_hashtags_all: List[Tweet] = filter_by_hashtags_all(test_dataset, ['#corona', '#coronahoax'])
	tweets_filtered_by_hashtags_any: List[Tweet] = filter_by_hashtags_any(test_dataset, ['#corona', '#coronahoax', '#coronavirus', '#covid19'])
	tweets_filtered_before: List[Tweet] = filter_before(test_dataset, datetime(2020, 4, 19, 18, 58, 46))
	tweets_filtered_at: List[Tweet] = filter_at(test_dataset, datetime(2020, 4, 19, 18, 58, 46))
	tweets_filtered_after: List[Tweet] = filter_after(test_dataset, datetime(2020, 4, 19, 18, 58, 46))
	tweets_filtered_between: List[Tweet] = filter_between(test_dataset, datetime(2020, 4, 19, 18, 0, 0), datetime(2020, 4, 19, 19, 0, 0))
	tweets_filtered_by_country_code: List[Tweet] = filter_by_country_code(test_dataset, 'US')
	tweets_filtered_by_country_codes: List[Tweet] = filter_by_country_codes(test_dataset, ['US', 'GB'])
	tweets_filtered_by_continent: List[Tweet] = filter_by_continent(test_dataset, 'Europe')
	tweets_filtered_by_continents: List[Tweet] = filter_by_continents(test_dataset, ['Europe', 'North America'])
	tweets_sorted_by_date_ascending: List[Tweet] = sort_by_date_ascending(test_dataset)
	tweets_sorted_by_date_descending: List[Tweet] = sort_by_date_descending(test_dataset)
	tweets_grouped_by_country_code: defaultdict = group_by_country_code(test_dataset)
	tweets_grouped_by_continent: defaultdict = group_by_continent(test_dataset)

	##############
	# 6. VISUALIZE
	##############
	print('\n6. VISUALIZE')
	# continents
	CONTINENTS: Dict[str, str] = {
		'Asia': 'asia',
		'Europe': 'europe',
		'Africa': 'africa',
		'North America': 'north_america',
		'South America': 'south_america',
		'Oceania': 'oceania',
		'Antarctica': 'antartica',
	}

	# create series to plot
	num_tweets_per_country_per_continent_absolute = defaultdict(lambda: defaultdict(int))
	num_tweets_per_country_absolute = defaultdict(lambda: defaultdict(int))
	num_tweets_per_continent_absolute = defaultdict(lambda: defaultdict(int))
	for tweet in test_dataset:
		if tweet.has_location():
			country_code: str = tweet.country_code.lower()
			continent: str = CONTINENTS[tweet.continent]

			num_tweets_per_country_per_continent_absolute[tweet.continent][country_code] += 1
			num_tweets_per_country_absolute['World'][country_code] += 1
			num_tweets_per_continent_absolute['World'][continent] += 1

	# visualize plots
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


def read_twitter_tokens(path: str) -> Tuple[str, str, str, str]:
	"""
	Read Twitter tokens from a text file.

	Parameters
	----------
	path : str
	    The path to the text file

	Returns
	-------
	str
	    A tuple of Twitter tokens
	"""
	with open(path) as file:
		consumer_key: str = file.readline().strip()
		consumer_secret: str = file.readline().strip()
		access_token: str = file.readline().strip()
		access_token_secret: str = file.readline().strip()

		return consumer_key, consumer_secret, access_token, access_token_secret


def read_google_token(path: str) -> str:
	"""
	Read Google token from a text file.

	Parameters
	----------
	path : str
	    The path to the text file

	Returns
	-------
	str
	    The Google token
	"""
	with open(path) as file:
		geocoding_api_key: str = file.readline().strip()

		return geocoding_api_key


def connect_to_twitter_api(consumer_key: str, consumer_secret: str, access_token: str,
                           access_token_secret: str) -> tweepy.API:
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


def get_new_tweets(twitter_api: tweepy.API, keywords: Dict[str, int], language: str = 'en') -> List[Tweet]:
	"""
	Get latest tweets from Twitter and create a list of Tweet Objects.

	Parameters
	----------
	twitter_api : tweepy.API
	    The object to interact with the Twitter API
	keywords : Dict[str,int]
	    The keywords on which to filter tweets and their corresponding number of tweets to retrieve
	language : str
	    The language on which to filter tweets

	Returns
	-------
	tweets : List[Tweet]
		A list of Tweet objects containing the latest tweets
	"""
	tweets = []
	for keyword, number in keywords.items():
		searched_tweets = []
		last_id = -1
		while len(searched_tweets) < number:
			count = number - len(searched_tweets)
			try:
				new_tweets = twitter_api.search(q=f'{keyword} -filter:retweets', lang=language, tweet_mode='extended',
				                                count=count, max_id=str(last_id - 1))
				if not new_tweets:
					break
				searched_tweets.extend(new_tweets)
				last_id = new_tweets[-1].id
			except tweepy.TweepError:
				break
		tweets.extend([Tweet(status) for status in searched_tweets])
		print(f'\tKeyword \'{keyword}\' finished, got {len(searched_tweets)} new tweets')

	print(f'Got {len(tweets)} new tweets in total')

	return tweets


def save_tweets(tweets: List[Tweet], path: str) -> None:
	"""
	Save tweets to a pickle file.

	Parameters
	----------
	tweets : List[Tweet]
		The tweets to be saved
	path : str
	    The path to the pickle file
	"""
	with open(path, 'wb') as file:
		pickle.dump(tweets, file)
		print(f'Saved {len(tweets)} tweets to {path}')


def load_tweets(path: str) -> List[Tweet]:
	"""
	Load tweets from a pickle file.

	Parameters
	----------
	path : str
	    The path to the pickle file

	Returns
	-------
	List[Tweets]
	    The list of tweets, loaded from the pickle file
	"""
	with open(path, 'rb') as file:
		tweets: List[Tweet] = pickle.load(file)
		print(f'Loaded {len(tweets)} tweets from {path}')

		return tweets


def save_model(model: Union[ComplementNB, DecisionTreeClassifier], path: str) -> None:
	"""
	Save model to a pickle file.

	Parameters
	----------
	model : Union[ComplementNB, DecisionTreeClassifier]
		The model to be saved
	path : str
	    The path to the pickle file
	"""
	with open(path, 'wb') as file:
		pickle.dump(model, file)
		print(f'Saved model to {path}')


def load_model(path: str) -> Union[ComplementNB, DecisionTreeClassifier]:
	"""
	Load a model from a pickle file.

	Parameters
	----------
	path : str
	    The path to the pickle file

	Returns
	-------
	Union[ComplementNB, DecisionTreeClassifier]
	    The model, loaded from the pickle file
	"""
	with open(path, 'rb') as file:
		model: Union[ComplementNB, DecisionTreeClassifier] = pickle.load(file)
		print(f'Loaded model from {path}')

		return model


def preprocess_corpus(corpus: List[str]) -> List[str]:
	"""
    Preprocess nlp corpus

    Parameters
    ----------
    corpus : List[str]
        list of tweet texts

    Returns
    -------
    final_corpus : List[str]
        list of tweet texts, but processed
    """
	# Download the English stop words from the NLTK repository.
	nltk.download('stopwords', quiet=True)
	# Removing the links from the tweets (starting with https:// until a space)
	corpus_no_url = [re.sub('(https://)\S*(\s|$)', '', line) for line in corpus]
	# Removing stopwords from English language
	stopWords = set(stopwords.words('english'))
	corpus_no_stops_no_url = [" ".join([re.sub('\n', "", l) for l in line.split(" ") if l not in stopWords]) for line in
	                          corpus_no_url]
	# Removing @...
	corpus_noAt_no_stops_no_url = [re.sub('(@)\S*(\s|$)', '', line) for line in corpus_no_stops_no_url]
	# Remove #
	corpus_noht_noAt_no_stops_no_url = [re.sub('#', '', line) for line in corpus_noAt_no_stops_no_url]
	# Set lowercase
	corpus_lowercase = [line.lower() for line in corpus_noht_noAt_no_stops_no_url]
	# Remove numbers
	corpus_no_numbers = [re.sub('[0-9]+', '', line) for line in corpus_lowercase]
	final_corpus = corpus_no_numbers

	# if debug_prints:
	#     print("\n*** CORPUS BEFORE ***")
	#     [print("\t* " + str(l)) for l in corpus[0:5]]
	#     print()
	#
	#     print("\n\n*** CORPUS AFTER ***")
	#     [print("\t* " + str(l)) for l in final_corpus[0:5]]
	#     print()

	return final_corpus


if __name__ == "__main__":
	main()
