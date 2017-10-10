import random
import csv
import nltk
from nltk.corpus import stopwords
import pickle

from nltk.classify.scikitlearn import SklearnClassifier
#from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
#from sklearn.svm import LinearSVC

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')


stop = set(stopwords.words('english'))
manual_stopwords = ['-', '.', '..', '...', "i'm", "it's", '&amp;', '&lt;3']
bag_size = 5000
dataset = []


# Reading the CSV file of 1.5 million tweets and removing the stopwords and creating dataset

with open('sentiment.csv', 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')

	num_rows = 1500000
	i = 0
	all_words = []
	stopchars = ['.', ',', '..', '...', ':', '!', '!!', '!!!', ')', '(', '?', ';']

	for row in reader:
		tweet = row['SentimentText'].strip().encode('utf-8') #removing starting and trailing white spaces
		tweet = ' '.join(tweet.split()) #converting multiple spaces to single space
		new_tweet_arr = []
		
		for word in tweet.split(' '):
		    new_word = []
		    for char in word.lower():
		        if(char not in stopchars):
		            new_word.append(char)
		    new_word = ''.join(new_word)
		    new_tweet_arr.append(word)

		tweet_arr = [j for j in new_tweet_arr if j not in stop and j not in manual_stopwords]


		all_words.extend(tweet_arr)
		dataset.append((tweet_arr,row['Sentiment']))		
		i += 1

		if i == num_rows:
			break


all_words = nltk.FreqDist(all_words)
print all_words.most_common(25)


word_features = []

for ff,ss in all_words.most_common(bag_size):
	word_features.append(ff)

def find_features(tweet_arr):
	features = {}
	data_structure = nltk.FreqDist(tweet_arr)

	for w in word_features:
		if data_structure[w] > 0:
			features[w] = data_structure[w]
	return features


# Converting cleaned dataset into trainable featuresets

featuresets = [(find_features(tweet_arr), sentiment) for (tweet_arr, sentiment) in dataset]
training_set = featuresets[:1200000]
testing_set = featuresets[1200000:]


# Training the features using Naive Bayes Classifier and Multinomial NB Classifier
# and saving it using pickle

classifier = nltk.NaiveBayesClassifier.train(training_set)
save_classifier = open("naivebayes.pickle", "wb")
pickle.dump(classifier, save_classifier)
save_classifier.close()
print ("Naive Bayes ACC: ", (nltk.classify.accuracy(classifier, testing_set))*100)
classifier.show_most_informative_features(50)


MNB_classifier = SklearnClassifier(MultinomialNB())
MNB_classifier.train(training_set)
save_MNB_classifier = open("mnb.pickle", "wb")
pickle.dump(MNB_classifier, save_MNB_classifier)
save_MNB_classifier.close()

print ("MultinomialNB ACC: ", (nltk.classify.accuracy(MNB_classifier, testing_set))*100)
