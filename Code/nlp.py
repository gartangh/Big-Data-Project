import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.naive_bayes import MultinomialNB
import nltk
from nltk.corpus import stopwords
import re

def naive_bayes(X_train, X_test, y_train, y_test):
    """
    Trains a Naive Bayes Classifier

    Parameters
    ----------
    X_train : 2D matrix
        training features
    X_test : 2D matrix
        test features
    y_train : list
        training labels
    y_test : list
        test labels

    Returns
    -------
    score : double
        accuracy of naive bayes model
    """
    model_bayes = MultinomialNB()
    model_bayes = model_bayes.fit(X_train, y_train)
    y_predict = model_bayes.predict(X_test)
    accuracy_bayes = model_bayes.score(X_test, y_test)
    print('Naive Bayes accuracy:' + '\t' + repr(accuracy_bayes))
    return accuracy_bayes


def decision_tree(X_train, X_test, y_train, y_test):
    """
    Trains a Decision Tree Classifier

    Parameters
    ----------
    X_train : 2D matrix
        training features
    X_test : 2D matrix
        test features
    y_train : list
        training labels
    y_test : list
        test labels

    Returns
    -------
    score : double
        accuracy of decision tree model
    """
    model_tree = tree.DecisionTreeClassifier(
        random_state=1)  # Setting random_state = 1, to remove randomness in fitting.
    model_tree = model_tree.fit(X_train, y_train)
    y_predict = model_tree.predict(X_test)
    accuracy_tree = model_tree.score(X_test, y_test)
    print('Decision Tree accuracy:' + '\t' + repr(accuracy_tree))
    return accuracy_tree


def main():
    """
    Apply Natural language processing to all given tweets.
    """

    # STEP 1: READ PICKLE -----------------------------------------------
    with open(tweets_fake_path, 'rb') as f:
        tweets_fake = pickle.load(f)

    with open(tweets_fake_2_path, 'rb') as f:
        tweets_fake_2 = pickle.load(f)

    with open(tweets_notfake_2_path, 'rb') as f:
        tweets_not_fake = pickle.load(f)

    with open(tweets_notfake_path, 'rb') as f:
        tweets_not_fake_2 = pickle.load(f)

    # Options for debugging purposes
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)
    # ------------------------------------------------------------------

    # STEP 2: CREATE DATAFRAMES ----------------------------------------
    df_fake = pd.DataFrame.from_records([tweet.to_dict() for tweet in tweets_fake])
    df_fake_2 = pd.DataFrame.from_records([tweet.to_dict() for tweet in tweets_fake_2])
    df_notfake = pd.DataFrame.from_records([tweet.to_dict() for tweet in tweets_not_fake])
    df_notfake_2 = pd.DataFrame.from_records([tweet.to_dict() for tweet in tweets_not_fake_2])
    # ------------------------------------------------------------------

    # STEP 3: Manually Identify acceptors and deniers ------------------
    fake_deniers = [1, 1, 0, 1, 0, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 0, 1, 1, 1, 1, 1,
                    1, 1, 1, 0, 1, 1, 1, 1, 1, 1,
                    0, 1, 1, 1, 0, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    0, 0, 1, 1, 1, 1, 0, 0, 0, 0,

                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 1, 1
                    ]
    fake_deniers_2 = [1] * len(df_fake_2)
    notfake_deniers = [0] * len(df_notfake)
    notfake_deniers_2 = [0] * len(df_notfake_2)

    fake_deniers.extend(fake_deniers_2)
    fake_deniers.extend(notfake_deniers)
    fake_deniers.extend(notfake_deniers_2)

    df = df_fake.append(df_fake_2)
    df = df.append(df_notfake)
    df = df.append(df_notfake_2)

    fake_deniers = [str(d) for d in fake_deniers]
    df['denier'] = fake_deniers
    df.reset_index()
    # ------------------------------------------------------------------

    # STEP 4: CREATE CORPUS AND LABELS ---------------------------------
    df_denier = df[df['denier'] == '1']
    df_acceptor = df[df['denier'] == '0']

    corpus = []
    labels = []
    for index, row in df.iterrows():
        corpus.append(row.text)
        labels.append(row.denier)
    # ------------------------------------------------------------------

    # STEP 5: GET MATRIX X ---------------------------------------------
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    # ------------------------------------------------------------------

    # STEP 6: TRAIN TEST SPLIT -----------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(X, labels)
    # ------------------------------------------------------------------

    # STEP 7: BASE CLASSIFIERS -----------------------------------------
    accuracy_naive_bayes = naive_bayes(X_train, X_test, y_train, y_test)
    accuracy_decision_tree = decision_tree(X_train, X_test, y_train, y_test)
    # ------------------------------------------------------------------

    # STEP 8: Natural Language Processing ------------------------------
    print("\n*** CORPUS BEFORE ***")
    [print("\t* " + str(l)) for l in corpus[0:5]]


    # Download the English stop words from the NLTK repository.
    nltk.download('stopwords')
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
    print("\n\n*** CORPUS AFTER ***")
    [print("\t* " + str(l)) for l in final_corpus[0:5]]
    # ------------------------------------------------------------------

    # STEP 9: Redo previous steps with new corus CLASSIFIERS -----------
    vectorizer_new = CountVectorizer()
    X_new = vectorizer_new.fit_transform(final_corpus)
    X_train_new, X_test_new, y_train_new, y_test_new = train_test_split(X_new, labels)
    accuracy_naive_bayes_new = naive_bayes(X_train_new, X_test_new, y_train_new, y_test_new)
    accuracy_decision_tree_new = decision_tree(X_train_new, X_test_new, y_train_new, y_test_new)
    # ------------------------------------------------------------------

    # STEP 10: IMPROVEMENT OF TOKENIZATION? ----------------------------
    print("\n\nImprovement Decision Tree: " + str(accuracy_naive_bayes_new - accuracy_naive_bayes))
    print("Improvement Decision Tree: " + str(accuracy_decision_tree_new-accuracy_decision_tree))
    # ------------------------------------------------------------------


if __name__ == "__main__":
    tweets_fake_path: str = 'tweets/nlp/tweets_fake_en_coronascam_fakecorona_100.pickle'
    tweets_fake_2_path: str = 'tweets/nlp/tweets_fake_en_all_446.pickle'
    tweets_notfake_path: str = 'tweets/nlp/tweets_en_corona_covid_100.pickle'
    tweets_notfake_2_path: str = 'tweets/nlp/tweets_en_all_3101.pickle'

    main()
