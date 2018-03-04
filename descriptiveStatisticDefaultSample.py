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

'''违约样本描述性统计'''
default = pd.read_excel('F:\\GFsummer2017\\债券违约报表依据发行人删减.xlsx',sheet_name = 'Sheet1')
List2014 = []
List2015 = []
List2016 = []
List2017 = []
for i,time in enumerate(default['发生日期']):
    intTime = int(str(time)[:4])
    if intTime < 2015:
        List2014.append(default.iloc[i,:])
    elif 2015<=intTime<2016:
        List2015.append(default.iloc[i,:])
    elif 2016<=intTime<2017:
        List2016.append(default.iloc[i,:])
    else:
        List2017.append(default.iloc[i,:])
frame2014 = DataFrame(List2014)      
frame2015 = DataFrame(List2015)  
frame2016 = DataFrame(List2016)  
frame2017 = DataFrame(List2017)           

plot.figure(figsize=[10,10])
plot.pie(default['所属wind行业'].value_counts(),labels=default['所属wind行业'].value_counts().keys())
plot.barh(range(15),default['所属wind行业'].value_counts()[:15])  
plot.yticks(range(15),np.array(default['所属wind行业'].value_counts().index)[:15])

plot.figure(figsize=[10,10])
plot.pie(default['省份'].value_counts(),labels=default['省份'].value_counts().keys())
plot.barh(range(15),default['省份'].value_counts()[:15])  
plot.yticks(range(15),np.array(default['省份'].value_counts().index[:15]))
