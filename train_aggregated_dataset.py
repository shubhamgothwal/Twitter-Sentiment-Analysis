import MySQLdb
import pickle
import nltk
from datetime import datetime, timedelta
from nltk.classify.scikitlearn import SklearnClassifier


bin_neg_folls = [0,2,41,104,232,663,1708,5103,21392,447175]
bin_pos_folls = [0,4,44,106,277,1224,2967,13942,237698]
bin_neg_rt = [0,1,4,81]
bin_pos_rt = [0,15]

def binned_features(csv_num_arr):
	#Takes a comma separated string of numbers and returns a dictionary after binning
	array = []
	for num in csv_num_arr:
		array.append(int(num))
	return array;
	feat = []
	idx = 0
	lst=-1
	for elem in bin_neg_folls:
		if array[0] <= elem and array[0]>lst:
			break
		idx += 1
		lst=elem
	
	feat.append(idx)

	idx = 0
	lst = -1
	for elem in bin_neg_rt:
		if array[1] <= elem and array[1]>lst:
			break
		idx += 1
		lst=elem
	feat.append(idx)

	idx = 0
	if array[2]>0:
		idx += 1
	feat.append(idx)

	idx = 0
	lst = -1
	for elem in bin_pos_folls:
		if array[3] <= elem and array[3]>lst:
			break
		idx += 1
		lst=elem
	feat.append(idx)

	idx = 0
	lst = -1
	for elem in bin_pos_rt:
		if array[4] <= elem and array[4]>lst:
			break
		idx += 1
		lst=elem
	feat.append(idx)

	idx = 0
	if array[5]>0:
		idx += 1
	feat.append(idx)

	return feat


X = []
Y = []


with open('datastr_ms.csv', 'rb') as f:
	for line in f:
		line_arr = line.split(',')
		tmp = binned_features(line_arr[:-1])		
		X.append(tmp)
		Y.append(int(line_arr[-1]))

dataset_size = len(X)
t_sz = int(0.75 * dataset_size)
X_train = X[:t_sz]
X_test = X[t_sz:]

Y_train = Y[:t_sz]
Y_test = Y[t_sz:]

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier

tree = DecisionTreeClassifier()
tree.fit(X_train, Y_train)

atree = AdaBoostClassifier(n_estimators=600)
atree.fit(X_train, Y_train)

clf = RandomForestClassifier(n_estimators=2, random_state=1, min_samples_split=2)
clf.fit(X_train, Y_train)

print 'ada boost Acc: {}'.format(atree.score(X_test, Y_test))
print 'rand for Acc: {}'.format(clf.score(X_test, Y_test))
print 'deci tr Acc: {}'.format(tree.score(X_test, Y_test))
