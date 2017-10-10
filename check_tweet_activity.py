import oauth2 as oauth
import urllib2 as urllib
from multiprocessing import Pool, TimeoutError
import time
import multiprocessing
import os
import csv
import datetime
import json
import MySQLdb
from threading import Thread
from functools import partial
from time import sleep	
from keys import consumer_key, consumer_secret, access_token, access_token_secret

_debug = 0

oauth_token    = oauth.Token(key=access_token, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url, 
                                             parameters=parameters)

  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)

  response = opener.open(url, encoded_post_data)
  return response

def fetchsamples(id,rt,fv,inactive):

	url = "https://api.twitter.com/1.1/statuses/show.json?id="+id
	parameters = []
	response = twitterreq(url, "GET", parameters)
	

	for line in response:
#print line.strip()
		try:
			json_data = json.loads(line.strip())
		except:
			continue

		try:
			retweet_count = json_data['retweet_count']
		except:
			retweet_count = -1

		try:
			favorite_count = json_data['favorite_count']
		except:
			favorite_count = -1

		if(retweet_count==-1 or favorite_count==-1):
			print "Tweet deleted"
			inactive=1200
		else:
			crt=retweet_count-rt
			cfv=favorite_count-fv
			change=crt+cfv

			if (change==0): inactive=inactive*4
			elif(change<10): inactive=inactive*2
			elif (change>10 and inactive>15): inactive=inactive/2
			elif (change>50 and inactive>30): inactive=inactive/4

		curr=datetime.datetime.now().strftime("%Y-%B-%d %I:%M")

		try:
			query="UPDATE tweet SET retweet_count=%s ,favorite_count=%s ,inactive=%s WHERE id_str=%s"%(int(retweet_count),int(favorite_count),int(inactive),id)
			query2="INSERT into tweetactivity (id_str,curr_time,retweet_count,favorite_count) values (%s,'%s',%s,%s)"%(id,curr,int(retweet_count),int(favorite_count))
			#print query2
			c = db.cursor()
			c.execute(query)
			c.execute(query2)
			c.close()
			db.commit()
		except MySQLdb.Error as e:
			print e
			db.rollback()
			print "Error in DB"
#db.close()

	#print id,retweet_count,favorite_count
	print ".",


def multi_run_wrapper(args):
   return fetchsamples(*args)


if __name__ == '__main__':
	db = MySQLdb.connect("localhost","root","","twitter_stocks")
	
	time = 0

	while (time>-1):
		a = datetime.datetime.now().replace(microsecond=0)
		sleeptime=60*15
		time=time+15
		#time=240
		print "Current Time",time
		c = db.cursor()
		if (time%240==0):
			current_checks=c.execute("select id_str,retweet_count,favorite_count,inactive,id from tweet where inactive in (15,30,60,120,240) and created_at like 'Mon Apr 03%'") 
		elif (time%120==0):
			current_checks=c.execute("select id_str,retweet_count,favorite_count,inactive,id from tweet where inactive in (15,30,60,120) and created_at like 'Mon Apr 03%'") 
		elif (time%60==0):
			current_checks=c.execute("select id_str,retweet_count,favorite_count,inactive,id from tweet where inactive in (15,30,60) and created_at like 'Mon Apr 03%'")
		elif (time%30==0):
			current_checks=c.execute("select id_str,retweet_count,favorite_count,inactive,id from tweet where inactive in (15,30) and created_at like 'Mon Apr 03%'")
		elif (time%15==0):
			current_checks=c.execute("select id_str,retweet_count,favorite_count,inactive,id from tweet where inactive=15 and created_at like 'Mon Apr 03%'")
	#db.close()
		count=0
		data=c.fetchall()
		c.close()
		tweetlist=[ ]
		for row in data:
			#fetchsamples(c[])
			tweetlist.append((row[0],row[1],row[2],row[3]))

		print tweetlist
		try:
			p = multiprocessing.Pool(10)
			p.map(multi_run_wrapper, tweetlist)
			
		except:
			print "ERROR SSL"
			sleep(60)
			flag=1

			#time=time-15
			#sleeptime=0
		p.close()
		p.join()
		b = datetime.datetime.now().replace(microsecond=0)
		tottime=int((b-a).total_seconds())
		print "Total time to run is :",tottime
		print "Sleep Time is :",(sleeptime-tottime)
		curr=datetime.datetime.now().strftime("%I:%M")
		print curr
		if(sleeptime-tottime>0):
			sleep(sleeptime-tottime)

