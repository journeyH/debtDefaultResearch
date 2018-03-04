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

def enetModel(Xfillna,yNor,l1_ratio,names):
    alphas, coefs, _ = linear_model.enet_path(Xfillna,yNor,l1_ratio = 1.0, \
                                              fit_intercept=False, return_models=False)
    plot.plot(alphas,coefs.T)
    plot.xlabel('alpha')
    plot.ylabel('Coefficients')
    plot.title('Coefficient curves for debt classify data')
    plot.axis('tight')
    plot.semilogx()
    ax = plot.gca()
    ax.invert_xaxis()
    plot.show()
    
    nattr, nalpha = coefs.shape    
    #find coefficient ordering
    nzList = []
    for iAlpha in range(1,nalpha):
        coefList = list(coefs[:,iAlpha])
        nzCoef = [index for index in range(nattr) if coefList[index] != 0.0]
        for q in nzCoef:
                if not(q in nzList):
                    nzList.append(q)
    nameList = [names[nzList[i]] for i in range(len(nzList))]
    print('Attribute Ordered by How Early They Enter the Model')
    print(nameList)
return nameList

