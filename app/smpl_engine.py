# K-fold cross validation for the sentiment analysis
# Collin Kersten (cakerste) & Zach Haas (zrhaas)
from _csv import reader
import csv
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier

# Use 10 folds
kfold = StratifiedKFold(n_splits=10)
# Use KNN as the classifier
knn = KNeighborsClassifier(n_neighbors=5)

x = []
y = []
scores = []
filename = ''

with open(filename) as csvDataFile:
    csvReader = reader(csvDataFile)
    for row in csvReader:
        x.append(row[2])
        y.append(row[1])

for train_index, test_index in kfold.split(x, y):
    x_train_fold = x[train_index]
    x_test_fold = x[test_index]
    y_train_fold = y[train_index]
    y_test_fold = y[test_index]
    knn.fit(x_train_fold, y_train_fold)
    print('accuracy: ', knn.score(x_test_fold, y_test_fold))
    scores.append(knn.score(x_test_fold, y_test_fold))

with open('model.csv', 'w') as output_file:
    scores_file = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    scores_file.writerow(scores)

