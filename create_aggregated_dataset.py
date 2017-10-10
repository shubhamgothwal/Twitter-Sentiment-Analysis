import MySQLdb
import pickle
import nltk
from datetime import datetime, timedelta
from nltk.classify.scikitlearn import SklearnClassifier

host = "localhost"
username = "root"
password = ""
db_name  = "t_stocks"
date_hash = set()
hash_list=[]
month_dict = {
		'January': 1,
		'February': 2,
		'March': 3,
		'April': 4,
		'May': 5,
		'June': 6,
		'July': 7,
		'August': 8,
		'September': 9,
		'October': 10,
		'November': 11,
		'December': 12,
	}


def temp_function():
	conn = MySQLdb.connect(host, username, password, db_name)
	cursor = conn.cursor()
	query = "select * from tweet where language='en' and company='Microsoft' limit 1"
	cursor.execute(query)
	for row in cursor:
		print row



def stage1():
	"""
	Reads the dB for Microsoft tweets and creates date_hash for categorization	
	"""

	conn = MySQLdb.connect(host, username, password, db_name)
	cursor = conn.cursor()
	query = "select * from tweet where language='en' and company='Microsoft'"
	cursor.execute(query)
	
	classifier = get_naive_bayes_pickle()
	bag_of_words = get_bag_of_words()
	
	stage1_list = []
	file = open('file.txt', 'wb')

	for row in cursor:
		curr_time = row[11]
		tmp_arr = curr_time.split(' ')
		curr_time = ' '.join(tmp_arr[:-2])
		curr_time = datetime.strptime(curr_time, '%a %b %d %H:%M:%S')
		curr_time -= timedelta(hours=4)
		
		if curr_time.day not in [17,18,19]:
			continue

		seconds = curr_time.minute*60 + (curr_time.hour-9)*3600 + curr_time.second
		
		d_hash = curr_time.day + curr_time.month*35

		date_hash.add(d_hash)

		tweet_id = row[10]		
		tweet = row[2]	
		retweet_cnt = row[8]
		fav_cnt = row[9]
		tweet_arr = clean_tweet(tweet)
		features = find_features(tweet_arr, bag_of_words)
		sentiment = classifier.classify(features)
		foll_cnt = row[4]

		var = [seconds, sentiment, foll_cnt, retweet_cnt, fav_cnt, d_hash]
		stage1_list.append(var)
		file.write(str(var) + '\n')

	file.close()
	return stage1_list


# Below are helper functions that is used for hashing dates.
# They support dynamic block sizes. i.e. a block size can changed from 
# 30 mins to 60 mins without any change in code.

def no_of_days():
	return len(date_hash)


def get_day(dd):
	i=0
	hash_list=sorted(date_hash)
	for row in hash_list:
		if row == dd:
			return i
		
		i=i+1
	return i


def block_per_day(block):
	return (1 + (7*3600+block-1)/block + 1)


def get_block(secs, block, d_hash):
	if secs <= 0:
		return 1 + get_day(d_hash)*block_per_day(block)
	elif secs > 7*3600:
		return 1 + (7*3600+block-1)/block + 1 + get_day(d_hash)*block_per_day(block)
	else:
		return 1 + 	(secs+block-1)/block + get_day(d_hash)*block_per_day(block)


def no_of_blocks(block):
	return block_per_day(block)*no_of_days()	
	

def get_row(foll,retweet,fav,blockid):
	rng=0
	if foll>100 and foll <= 450:
		rng+= 1
	elif foll > 450 and foll <=1600:
		rng+=2
	elif foll > 1600:
		rng+=3

	if retweet>1 and retweet <= 3:
		rng+=4
	elif retweet>3 and retweet <= 25:
		rng+=8
	elif retweet>25:
		rng+=12

	if fav>0:
		rng+=16

	return 64*(blockid-1) + rng



def build_datastr(block):
	"""
	This code does the actual aggregation based on the category that the tweet belongs.
	It returns a 'datastr_ms.csv' file which is used for the actual training.
	"""
	st1=stage1()

	tot_block = no_of_blocks(block)
	temp=[]
	datastr=[]
	stock=[]
	
	datastr = [[0]*6 for _ in range(64*tot_block)]	
	stock = [0 for _ in range(64*tot_block)]

	with open('stock_ms.txt') as f:
		content = f.readlines()

	content= [x.strip() for x in content] 

	cnt = 0
	tot=0
	sent=0
	for row in st1:
		idx=get_row(row[2],row[3],row[4],get_block(row[0],block,row[5]))
		stock[idx] = int(content[get_block(row[0],block,row[5])-1])
		sent+=1-int(row[1])
		tot=tot+1
		#0 -> neg_foll, 1-> neg_rt, 2-> neg_fav, similarly 3,4,5for pos 
		
		for i in range(2,5):
			for j in range(0,block_per_day(block)):
				if (idx + j*64)< 64*tot_block:
					datastr[idx +j*64][int(row[1])*3 + i - 2] += max(0,row[i])
	
	print sent,tot

	data_arr = []
	stock_arr = []
	featuresets = []
	for row, stock_price in zip(datastr,stock):
		flag = 0
		for item in row:
		    flag += item
		if flag>0:
			data_arr.append(row)
			stock_arr.append(stock_price)
			featuresets.append((row,stock_price))

	with open('datastr_ms.csv', 'wb') as f:
		for row, stock_price in zip(data_arr,stock_arr):
			for item in row:
				f.write(str(item) + ',')
			f.write(str(stock_price))
			f.write('\n') 
	return
	

# Find features of unknown tweets using the bag of words created in sentiment analysis module
def find_features(tweet_arr, word_features):
	features = {}
	data_structure = nltk.FreqDist(tweet_arr)

	#print data_structure
	for w in word_features:
		if data_structure[w] > 0:
			features[w] = data_structure[w]
	return features


def get_naive_bayes_pickle():
	classifier_f = open('naivebayes.pickle', 'rb')
	classifier = pickle.load(classifier_f)
	classifier_f.close()
	return classifier


def get_bag_of_words():
	bag_f = open('bag.pickle', 'rb')
	bag_of_words = pickle.load(bag_f)
	bag_f.close()
	return bag_of_words

	
def clean_tweet(tweet_str):
	from nltk.corpus import stopwords
	stop = set(stopwords.words('english'))
	manual_stopwords = ['-', '.', '..', '...', "i'm", "it's", '&amp;', '&lt;3']

	tweet = tweet_str.strip() #removing starting and trailing white spaces
	tweet = ' '.join(tweet.split()) #converting multiple spaces to single space
	tweet_arr = [j for j in tweet.lower().split() if j not in stop and j not in manual_stopwords]
	return tweet_arr
	

if __name__ == '__main__':
	data = build_datastr(900)
	