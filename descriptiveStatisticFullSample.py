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
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import StratifiedShuffleSplit
import scipy.stats as stats
from pylab import *
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
nrows, ncols = X.shape
X.get_dtype_counts()
findCategory = X.dtypes == object
categoricalFeatures = X.loc[:,findCategory]
numericFeatures = X.loc[:,~findCategory]
#numericFeatures = StandardScaler().fit_transform(numericFeatures)
mean_vals = numericFeatures.mean()
sd_vals = numericFeatures.std()
numericFeatures = (numericFeatures - mean_vals)/sd_vals
categoryCount = {}
for feature in categoricalFeatures:
    categoryCount[feature] = []
    categoryCount[feature] = categoricalFeatures[feature].value_counts()
#
#numeric qq plot
for feature in numericFeatures:
    stats.probplot(numericFeatures[feature],dist='norm',plot=plot)
    feature = u"%s" %(feature) #加上u unicode进行编码 为了读取中文
    plot.title(feature)
    plot.show()

#parallel coordinate plot
plot.figure(figsize=[20,10])
for i in range(nrows):
    if y[i] == 0:
        pcolor = 'blue'
    else:
        pcolor= 'red'
    dataRow = numericFeatures.iloc[i,:]
    dataRow.plot(color=pcolor)
plot.xticks(np.arange(numericFeatures.shape[1]),range(numericFeatures.shape[1]))
plot.xlabel('Attribute Index')
plot.ylabel('Attribute Values')
plot.show()
attributeList = [2,5,8,9,13,15,17,29,33,35,38,40,41,54,55]
for i in attributeList:
    attribute = numericFeatures.iloc[:,i]
    plot.scatter(attribute,y,alpha=0.5,s=120)
    plot.xlabel(numericFeatures.keys()[i])
    plot.ylabel('label')
    plot.show()

corMat = DataFrame(data.corr())
plot.pcolor(corMat)
plot.show()
labelAbs = DataFrame(abs(corMat['label']))
labelAbsTemp = labelAbs.sort_values(by=['label'],ascending=False)
print(labelAbsTemp)
corMat['label'][labelAbsTemp[:20].index]
highcorr = corMat[np.abs(corMat)>0.75]
highcorr.sort_values(by=list(highcorr.keys()),ascending=False,inplace=True)

#将省份和行业去掉 原因 1.算法对类别数目的要求 2不重要：相关性等
del X['省份']  
del X['所属Wind行业名称\r']    
highcorrDel = ['quick','current','ocftoshortdebt','ocficftocurrentdebt','longdebttodebt',\
               'intdebttototalcap','tangibleassettodebt','equitytototalcapital',\
               'non_currentassetsturn']
for delvar in highcorrDel:
    del X[delvar]
