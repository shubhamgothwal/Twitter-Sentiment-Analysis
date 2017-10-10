import requests
from bs4 import BeautifulSoup
import threading
import MySQLdb


db = MySQLdb.connect("localhost","root","","twitter_stocks")
c = db.cursor()


stockss=["MSFT"]
def f():

	for stockIndex in stockss:
		try:
			url = "https://finance.yahoo.com/quote/"+stockIndex+'/'
			print url
			response = requests.get(url)
			soup = BeautifulSoup(response.text, "html.parser")
			index = soup.find("span","Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)").string
			print index

			c.execute("INSERT INTO indexes (name,value) VALUES (%s,%s);",(stockIndex,index))
			db.commit()
		except:

			print "error"
	    	db.rollback()	   

	threading.Timer(60, f).start()


f()
 
	
