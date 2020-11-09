# K-fold cross validation for the sentiment analysis
# Collin Kersten (cakerste) & Zach Haas (zrhaas)
import csv
import os

import numpy as np
import pandas as pd
from _csv import reader
from matplotlib import pyplot as plt
from sklearn import preprocessing
from sklearn.cluster import DBSCAN, KMeans


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
    finalMatrix = preprocessing.scale(np.array(list(stmtDic.values())), axis= 0)
    return finalMatrix

def myKMean(data):
    data = np.array(data)
    kmeans = KMeans(n_clusters=3).fit(data)
    return(kmeans.labels_)

# DBSCAN
def mydbscan(data):
    data = np.array(data)
    print(data)
    db = DBSCAN(eps=0.9, min_samples=2).fit(data)
    labels = db.labels_
    print(labels)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    #print('Number of clusters: ', n_clusters)
    #print('Noise: ', n_noise)
    return(labels)

def mscatter(x,y,ax=None, m=None, **kw):
    import matplotlib.markers as mmarkers
    if not ax: ax=plt.gca()
    sc = ax.scatter(x,y,**kw)
    if (m is not None) and (len(m)==len(x)):
        paths = []
        for marker in m:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(
                        marker_obj.get_transform())
            paths.append(path)
        sc.set_paths(paths)
    return sc

def plotData(matrix, labels, name):
    markers = ['o', 'v', 's', 'P', '^', 'x', '<' ,"D" , '>']
    x,y,z = zip(*matrix)
    m = list()
    for label in labels:
        m.append(markers[label])
    fig, ax = plt.subplots()
    scatter = mscatter(x,y, c=z, m=m, ax=ax, cmap="Greys", edgecolor="k")
    plt.colorbar(scatter, label="Standardized Percent Stock Change")
    plt.title(name)
    plt.xlabel("Standardized Number of Positive Tweets")
    plt.ylabel("Standardized Number of Negitive Tweets")
    print(matrix)
    # plt.show()

def log_data(model_type, matrix, labels, name):
    ticker = name.replace("./data/sentiment/", "").replace("_stmt.csv", "")
    if (os.path.exists(f"data/model/{ticker}_twt.csv", )):
        output = pd.read_csv(f"data/model/{ticker}_twt.csv", index_col="id")
    else:
        output = pd.DataFrame(columns=["group", "percent_chg", "num_positive", "num_negative"])

    for index, row in enumerate(matrix):
        num_positive, num_negative, percent_chg = (*row,)
        group = labels[index]
        new_record = {"group": group, "percent_chg": percent_chg,
                      "num_positive": num_positive, "num_negative": num_negative}
        output = output.append(new_record, ignore_index=True)
    output.to_csv(f"data/model/{ticker}_{model_type}.csv", index_label="id")

#Start main
path = './data/sentiment'
stmtDataFiles = []
with os.scandir(path) as entries:
    for entry in entries:
        if entry.is_file() and entry.name != "sample.csv":
            stmtDataFiles.append(path + "/" + entry.name)

preProcMatrixs = list()
for filename in stmtDataFiles:
    preProcMatrixs.append(intializeData(os.path.abspath(filename)))


plotData(preProcMatrixs[-1], myKMean(preProcMatrixs[-1]), "Test")
for i in range(len(preProcMatrixs)):
    matrix = preProcMatrixs[i]
    labels = myKMean(preProcMatrixs[i])
    name = stmtDataFiles[i]
    log_data("k_mean", matrix, labels, name)
    plotData(matrix, labels, name)
#mydbscan(preProcMatrixs[-1])
for i in range(len(preProcMatrixs)):
    matrix = preProcMatrixs[i]
    labels = mydbscan(preProcMatrixs[i])
    name = stmtDataFiles[i]
    log_data("db_scan", matrix, labels, name)
    plotData(matrix, labels, name)
