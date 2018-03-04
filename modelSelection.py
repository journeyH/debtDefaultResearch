#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 19:41:25 2018

@author: hudie
"""
import sys
sys.path.append('F:\\GFsummer2017')
import pandas as pd
from pandas import DataFrame,Series
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model, svm, ensemble, neural_network
from sklearn.metrics import precision_recall_curve, auc,f1_score
from sklearn.model_selection import StratifiedShuffleSplit
import matplotlib.pyplot as plot
import classifierStat
from imp import reload
reload(classifierStat)
plot.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plot.rcParams['axes.unicode_minus']=False #用来正常显示负号

rawData = pd.read_excel('F:\\GFsummer2017\\sample.xlsx', sheet_name = 'sheet1')
data = rawData.iloc[:,2:]
y = data['label']
del data['label']
X = data
data = pd.concat([X,y],axis=1)
ySVM = []
for yi in y:
    if yi == 1:
        ySVM.append(yi)
    else:
        ySVM.append(-1)
ySVM = np.array(ySVM)
#将省份和行业去掉 原因 1.算法对类别数目的要求 2不重要：相关性等
del X['省份']  
del X['所属Wind行业名称\r']    
highcorrDel = ['quick','current','ocftoshortdebt','ocficftocurrentdebt','longdebttodebt',\
               'intdebttototalcap','tangibleassettodebt','equitytototalcapital',\
               'non_currentassetsturn']
for delvar in highcorrDel:
    del X[delvar]     
X = pd.get_dummies(X)
Xfillna = X.fillna(X.mean())   
XfillnaMean = Xfillna.mean()
XfillnaStd = Xfillna.std()
yMean = y.mean()
yStd = y.std()
Xfillna = (Xfillna - XfillnaMean)/XfillnaStd
yNor = (y - yMean)/yStd
names = list(Xfillna.keys())
Xfillna = np.array(Xfillna)
yNor = np.array(yNor)

#lasso feeture engineering
nameList = classifierStat.enetModel(Xfillna,yNor,0.9,names)
nameListChoose = nameList[:30]

for iName in names:
    if not(iName in nameListChoose):
        del X[iName]
Xfillna = X.fillna(X.mean())   
XfillnaMean = Xfillna.mean()
XfillnaStd = Xfillna.std()
Xfillna = (Xfillna - XfillnaMean)/XfillnaStd
namesAfter = list(Xfillna.keys())
Xfillna = np.array(Xfillna)
y = np.array(y)
X = np.array(X)       
#k fold cv and 分层抽样
cv = StratifiedShuffleSplit(n_splits=5, test_size=0.3,random_state=0)
#数据、训练、选参数、样本外PRC

penalChooseList = []
Clist = []
f1ChooseList = []
for i,C in enumerate((1000,100,10,1,0.1)):   
#for C in [0.003*(3**i) for i in range(20)]:
    print(C)
    prcList = []
    f1Score = []
    Clist.append(C)
    for train, test in cv.split(Xfillna,ySVM): 
        #l2 penalized logistic regression C 要加1000000表示没penalized
        #classifier = linear_model.LogisticRegression(C=C,penalty='l2',tol=0.001)
        #svm
        classifier = svm.SVC(C=C,kernel='linear',tol=0.00001)
        #nn
        #classifier = neural_network.MLPClassifier(hidden_layer_sizes=(1,),activation='logistic',alpha=C)
        classifier.fit(Xfillna[train],ySVM[train])
        predictions = classifier.predict(Xfillna[test])
        precision, recall, thresholds = precision_recall_curve(ySVM[test],predictions)
        prc_auc = auc(recall, precision)
        prcList.append(prc_auc)

    penalChooseList.append(np.mean(prcList))
withoutPenalized = penalChooseList[0]
maxPRC =  max(penalChooseList)
CBest = Clist[penalChooseList.index(maxPRC)]
print(maxPRC,CBest,withoutPenalized)

#gradient boosting 
def findBestGBM(Xfillna,y):
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.3,random_state=0)
    saveDict = {}
    saveDict['nEst'] = []
    saveDict['depth'] = []
    saveDict['learnRate'] = []
    saveDict['meanprc'] = []
    for nEst in list(range(100,2001,100)):
        for depth in list(range(1,6)):
            for learnRate in [0.003*(3**i) for i in range(9)]:
                maxFeatures = int(np.sqrt(Xfillna.shape[1]))
                
                prcList = []
                for train, test in cv.split(Xfillna,y): 
                    classifier = ensemble.GradientBoostingClassifier(
                            n_estimators=nEst, max_depth=depth,
                            learning_rate=learnRate,max_features=maxFeatures)
                    classifier.fit(Xfillna[train],y[train])
                    predictions = classifier.predict(Xfillna[test])
                    precision, recall, thresholds = precision_recall_curve(y[test],predictions)
                    prc_auc = auc(recall, precision)
                    prcList.append(prc_auc)
                saveDict['meanprc'].append(np.mean(prcList))
                saveDict['nEst'].append(nEst)
                saveDict['depth'].append(depth)   
                saveDict['learnRate'].append(learnRate)
                print(np.mean(prcList),nEst,depth,learnRate)
    maxPRC =  max(saveDict['meanprc'])
    maxPRCIndex = saveDict['meanprc'].index(maxPRC)
    nEstBest = saveDict['nEst'][maxPRCIndex]
    depthBest = saveDict['depth'][maxPRCIndex]
    learnRateBest = saveDict['learnRate'][maxPRCIndex]
    print(maxPRC,nEstBest,depthBest,learnRateBest)
    return maxPRC,nEstBest,depthBest,learnRateBest
maxPRC,nEstBest,depthBest,learnRateBest = findBestGBM(Xfillna,y)

cv = StratifiedShuffleSplit(n_splits=1, test_size=0.01,random_state=0)

#最优模型GDBT 特征重要性求解
for train, test in cv.split(Xfillna,y): 
    bestClassifier = ensemble.GradientBoostingClassifier(
                            n_estimators=1100, max_depth=2,
                            learning_rate=0.003,max_features=int(np.sqrt(Xfillna.shape[1])))
    bestClassifier.fit(Xfillna[train],y[train])
    predictions = bestClassifier.predict(Xfillna[test])
    precision, recall, thresholds = precision_recall_curve(y[test],predictions)
    prc_auc = auc(recall, precision)
    print(prc_auc)
param = bestClassifier.get_params()
featureImportance = bestClassifier.feature_importances_
estimations = bestClassifier.estimators_
# normalize by max importance
featureImportance = featureImportance / featureImportance.max()
#plot importance of top 15
idxSorted = np.argsort(featureImportance)[15:30]
idxTemp = np.argsort(featureImportance)[::-1]
print(idxTemp)
barPos = np.arange(idxSorted.shape[0]) + .5
plot.barh(barPos, featureImportance[idxSorted], align='center')
plot.yticks(barPos, np.array(namesAfter)[idxSorted])
plot.xlabel('Variable Importance')
plot.show()

#RF
saveDict = {}
saveDict['nEst'] = []
saveDict['depth'] = []
saveDict['meanprc'] = []
for nEst in list(range(100,2001,100)):
    for depth in list(range(1,6)):
            maxFeatures = int(np.sqrt(Xfillna.shape[1]))
            
            prcList = []
            for train, test in cv.split(Xfillna,y): 
                classifier = ensemble.RandomForestClassifier(
                        n_estimators=nEst, max_depth=depth,
                        max_features=maxFeatures)
                classifier.fit(Xfillna[train],y[train])
                predictions = classifier.predict(Xfillna[test])
                precision, recall, thresholds = precision_recall_curve(y[test],predictions)
                prc_auc = auc(recall, precision)
                prcList.append(prc_auc)
            saveDict['meanprc'].append(np.mean(prcList))
            saveDict['nEst'].append(nEst)
            saveDict['depth'].append(depth)   
            print(prcList,np.mean(prcList),nEst,depth)
maxPRC =  max(saveDict['meanprc'])
maxPRCIndex = saveDict['meanprc'].index(maxPRC)
nEstBest = saveDict['nEst'][maxPRCIndex]
depthBest = saveDict['depth'][maxPRCIndex]
print(maxPRC,nEstBest,depthBest)  
