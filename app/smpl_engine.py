# K-fold cross validation for the sentiment analysis
# Collin Kersten (cakerste) & Zach Haas (zrhaas)
from _csv import reader
import csv
from sklearn.cluster import KMeans
from sklearn import preprocessing
import numpy as np
import os

def intializeData(filename):
    date = []
    stmt = []
    perc = []
    with open(filename, 'r', encoding="utf8") as csvDataFile:
        csvReader = reader(csvDataFile)
        x = False
        for row in csvReader:
            if x:
                date.append(str(row[1][0:10]))
                stmt.append(row[4])
                perc.append(row[3])
            else:
                x = True
    dataRaw = np.array([date, stmt, perc]).transpose()
    stmtDic = {}  
    for row in dataRaw:
        if not str(row[0]) in stmtDic:
            #Pos, Neg, Perc
            stmtDic[row[0]] = [0, 0, row[2]]
        if row[1] == 'Positive':
            stmtDic[row[0]][0] += 1
        else:
            stmtDic[row[0]][1] += 1
        
    finalMatrix = preprocessing.normalize(np.array(list(stmtDic.values())), axis= 0, norm='max')
    print(finalMatrix)
    return finalMatrix

path = './data/sentiment'
stmtDataFiles = []
with os.scandir(path) as entries:
    for entry in entries:
        if entry.is_file() and entry.name != "sample.csv":
            stmtDataFiles.append(path + "/" + entry.name)

preProcMatrixs = list()
for filename in stmtDataFiles:
    print(filename)
    preProcMatrixs.append(intializeData(os.path.abspath(filename)))







"""
with open('model.csv', 'w') as output_file:
    scores_file = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    scores_file.writerow(scores)
"""


"""
# Use 10 folds
kfold = StratifiedKFold(n_splits=10)
# Use KNN as the classifier
knn = KNeighborsClassifier(n_neighbors=5)
"""
""" 
for train_index, test_index in kfold.split(x, y):
    x_train_fold = x[train_index]
    x_test_fold = x[test_index]
    y_train_fold = y[train_index]
    y_test_fold = y[test_index]
    knn.fit(x_train_fold, y_train_fold)
    print('accuracy: ', knn.score(x_test_fold, y_test_fold))
    scores.append(knn.score(x_test_fold, y_test_fold))
"""