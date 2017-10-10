import oauth2 as oauth
import urllib2 as urllib
import csv
import json
import MySQLdb
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

def fetchsamples():
  company = "microsoft"
  url = "https://stream.twitter.com/1.1/statuses/filter.json?track=" + company + "&lang=en"
  parameters = []
  response = twitterreq(url, "GET", parameters)

  for line in response:
    #print line.strip()
    
    try:
      json_data = json.loads(line.strip())
    except:
      continue

    try:
      id_str = json_data['id_str'].encode('utf-8') 
    except:
      continue
    
    created_at = json_data['created_at'].encode('utf-8')
    text = json_data['text'].encode('utf-8')
    username = json_data['user']['screen_name'].encode('utf-8')
    
    try:
      location = json_data['user']['location'].encode('utf-8')
    except:
      location = ""
    
    try:
      followers_count = json_data['user']['followers_count']
    except:
      followers_count = -1
    
    try:
      friends_count = json_data['user']['friends_count']
    except:
      friends_count = -1
    
    try:
      listed_count = json_data['user']['listed_count']
    except:
      listed_count = -1
    
    try:
      language = json_data['user']['lang'].encode('utf-8')
    except:
      language = ""
    
    try:
      retweet_count = json_data['retweet_count']
    except:
      retweet_count = -1
    
    try:
      favorite_count = json_data['favorite_count']
    except:
      favorite_count = -1
    
    timestamp = json_data['timestamp_ms']

    inactive=15

    try:
      longitude=json_data["user"]["coordinates"]["coordinates"].split(',')[0]
    except:
      longitude=1

    try:
      latitude=json_data["user"]["coordinates"]["coordinates"].split(',')[1]
    except:
      latitude=1

    


    arr = [username, text, location, followers_count, friends_count, listed_count, language, retweet_count, favorite_count, id_str, created_at, company]
    writer.writerow(arr)

    try:
      c = db.cursor()
      c.execute("INSERT INTO tweet (username, text, location, followers_count, friends_count, listed_count, language, retweet_count, favorite_count, id_str, created_at, company,inactive,longitude,latitude) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
              (username, text, location, int(followers_count), int(friends_count), int(listed_count), language, int(retweet_count), int(favorite_count), id_str, created_at, company,int(inactive),int(longitude),int(latitude)))
      c.close()
      db.commit()
    except MySQLdb.Error as e:
      db.rollback()
      print "Error"
      print e
    if language=="en":
      print username, text, location, followers_count, friends_count, listed_count, language, retweet_count, favorite_count, id_str, created_at, company  

if __name__ == '__main__':
  f = open("tweets.csv", "ab")
  writer = csv.writer(f,delimiter=',')
  db = MySQLdb.connect("localhost","root","","twitter_stocks")
  
  fetchsamples()
