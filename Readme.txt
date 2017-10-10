System Requirements
-------------------
This code runs on Ubuntu system above version 14 and Python 2.7.
MySQL database version >= 5.5+

sudo apt-get install mysql-server
sudo apt-get install python-pip
sudo pip install nltk
	- Then in python console, type 'nltk.download()' and download everything
sudo pip install sklearn
sudo pip install MySQL-python


Database Credentials
--------------------
Username: 'root'
Password: ''
Host: 'localhost'
Database Name: 'twitter_stocks'
Import the 'dump.sql' file to the database of this name.


Data Collection Module
----------------------
- MySql DB which is available as 'dump.sql' can be imported so as to effectively run the script.

- 'check_tweet_activity.py' is the script which tracks the tweets activity. 
  It requires API keys of twitter which are to be saved in 'keys2.py'.
  API keys can be obtained from official twitter account keys setup.

- 'twitter_stream.py' is used to stream the tweets using Twitter Streaming API and it also requires keys to be saved in 'keys.py'. 

- 'get_stock_price.py' is used to scrape the stock market value from Yahoo finance. 
  The name of the stock to be scraped should be specified in the "stockss" list and it will be retrieved 

- API KEYS GENERATION - https://apps.twitter.com/

- All the requirements can be met using pip install <library_name>


Sentiment Analysis Module
-------------------------

- The raw dataset of 1.5 million tweets with is sentiments is stored in the file 'sentiment.csv'.
- The file 'sentiment_analysis_module.py' is used to read the dataset and train it using Naive Bayes Classifier
  and Multinomial NB Classifier. The trained classifier is saved in 'naivebayes.pickle' and 'mnb.pickle'.

The Naive Bayes pickle file is then used directly by the Category Based Tweet Categorization approach that is done next.


Category Based Tweet Aggregation Module
---------------------------------------

- 'create_aggregated_dataset.py' reads the tweet from database and calculates their sentiments from the trained model stored in
  'naivebayes.pickle', categorises the daily tweets into blocks and saves them in 'datastr_ms.csv'

- 'train_aggregated_dataset.py' reads 'datastr_ms.csv' and trains the model with Random Forest, Decision Tree.

- 'bag.pickle' contains 5000 most frequent words which were used as features for Sentiment Analysis module.


Team Members
-----------

Aakash Rana (U13CO063)
Adesh Kala (U13CO080)
Shubham Gothwal (U13CO081)
A. Abishek (U13CO084)
