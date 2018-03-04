#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 22:37:06 2017
@author: hudie
"""

import sys
sys.path.append('../')
import qreg
import numpy as np
import pandas as pd
from pandas import DataFrame,Series
import os
import re
import matplotlib.pyplot as plot
plot.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plot.rcParams['axes.unicode_minus']=False #用来正常显示负号

from WindPy import *
from datetime import *
w.start()

codesList = ["000001.SZ","600000.SH","600015.SH","600016.SH","600036.SH",
             "601166.SH","601288.SH","601328.SH","601398.SH","601818.SH",
             "601939.SH","601988.SH","601998.SH","002142.SZ","002807.SZ",
             "002839.SZ","600908.SH","600919.SH","600926.SH","601009.SH",
             "601128.SH","601169.SH","601229.SH","601997.SH","603323.SH",
             "601318.SH","601336.SH","601601.SH","601628.SH","000166.SZ",
             "000416.SZ","000686.SZ","000728.SZ","000750.SZ","000776.SZ",
             "000783.SZ","000987.SZ","002500.SZ","002670.SZ","002673.SZ",
             "002736.SZ","002797.SZ","600030.SH","600061.SH","600109.SH",
             "600369.SH","600621.SH","600837.SH","600909.SH","600958.SH",
             "600999.SH","601099.SH","601198.SH","601211.SH","601375.SH",
             "601377.SH","601555.SH","601688.SH","601788.SH","601878.SH",
             "601881.SH","601901.SH","000001.SZ","600000.SH","600015.SH",
             "600036.SH","600016.SH","601166.SH","601288.SH","601328.SH",
             "601398.SH","601818.SH","601939.SH","601988.SH","601998.SH",
             "002142.SZ","002807.SZ","002839.SZ","600908.SH","600919.SH",
             "600926.SH","601009.SH","601128.SH","601169.SH","601229.SH",
             "601997.SH","603323.SH","601318.SH","601336.SH","601601.SH",
             "601628.SH","000166.SZ","000416.SZ","000686.SZ","000728.SZ",
             "000750.SZ","000776.SZ","000783.SZ","000987.SZ","002500.SZ",
             "002670.SZ","002673.SZ","002736.SZ","002797.SZ","600030.SH",
             "600061.SH","600109.SH","600369.SH","600621.SH","600837.SH",
             "600909.SH","600958.SH","600999.SH","601099.SH","601198.SH",
             "601211.SH","601375.SH","601377.SH","601555.SH","601688.SH",
             "601788.SH","601878.SH","601881.SH","601901.SH"]

MESingle = {}
LEVSingle = {}
for code in codesList:
    res = w.wsd(code, "close,sec_name,trade_code,total_shares,tot_assets,tot_equity",\
                "2007-01-01", "2017-08-29", "unit=1;rptType=1;currencyType=;Period=W;PriceAdj=F")
    tempData = res.Data
    time = res.Times
    MESingle[tempData[1][0]] = []
    LEVSingle[tempData[1][0]] = []
    price = Series(tempData[0])
    stock = Series(tempData[3])
    asset = Series(tempData[4])
    equity = Series(tempData[5])
    ME = price*stock
    LEV = asset/equity
#    ret = np.log(price/price.shift(1))
    MESingle[tempData[1][0]] = ME
    LEVSingle[tempData[1][0]] = LEV
   

MESingle = DataFrame(MESingle)
LEVSingle = DataFrame(LEVSingle).fillna(method='backfill')
retSingle = MESingle*LEVSingle
'''处理缺失值'''
nrows, ncols = retSingle.shape
totalMissingData = retSingle.isnull().sum().sort_values(ascending=False)
percentMissingData = (retSingle.isnull().sum()/retSingle.isnull().count()).sort_values(ascending=False)
missingData = pd.concat([totalMissingData,percentMissingData], axis=1, keys=['Total', 'Percent'])
sys.stdout.write('head information \n')
#print(missingData.head(int(ncols)))
delColumns = percentMissingData > 0.85 #从国泰君安保留起
for columns in list(delColumns.keys()):
    try:
        if delColumns[columns]:
            del retSingle[columns]
    except KeyError:
        continue
names = retSingle.keys()
retSingle.dropna(axis=0, how='all',inplace=True)
startIndex = np.max(np.where(retSingle['国泰君安'].isnull()==True))
retSingle = retSingle.iloc[startIndex:,:]

weight = np.array(1/np.sum(retSingle.shift(1),axis=1))
noNorMVC = np.array(retSingle-retSingle.shift(1))
MVCsingle = np.zeros(list(noNorMVC.shape))
for i in range(2,noNorMVC.shape[0]):
    MVCsingle[i,:] = noNorMVC[i,:]*weight[i]
MVCsingle = 100*MVCsingle[2:,:]  
MVCTotal = np.sum(MVCsingle,axis=1)

def getListFiles(path):
    rootList = []
    dirList = []
    fileList = []
    for root, dirs, files in os.walk(path):
        rootList.append(root)
        dirList.append(dirs)
        fileList.append(files)
    return rootList,dirList,fileList

rootList,dirList,fileList = getListFiles('./')
matchWord = '.xlsx'
pattern = re.compile(matchWord)
rawXDict = {}
for file in fileList[0]:                    
    match = pattern.search(file)
    if match:
         rawXDict[file] = pd.read_excel(file,sheet_name = 'Sheet1').iloc[:,1]
xVariable = {}
xVariable['counterPartyLiquiditySpread'] = rawXDict['银行质押3m.xlsx'] - rawXDict['国债收益3m.xlsx']
xVariable['futureVolatility'] = rawXDict['沪深300期权波动率.xlsx']
xVariable['3mBond'] = rawXDict['国债收益3m.xlsx']
xVariable['yieldCurve'] = rawXDict['国债收益10y.xlsx'] - rawXDict['国债收益3m.xlsx']
xVariable['creditSpread'] = rawXDict['铁道债3y.xlsx'] - rawXDict['国债收益3y.xlsx']
xVariable['hs300'] =  100*np.log(rawXDict['沪深300.xlsx']/rawXDict['沪深300.xlsx'].shift(1)).dropna()

xVariable = DataFrame(xVariable)
xVariable = np.array(xVariable)

m,n = MVCsingle.shape
VaRq = np.zeros([m,n])
VaRm = np.zeros([m,n])
CoVaR = np.zeros([m,n])
VaRsysM = np.zeros([m,n])
deltaCoVaR = np.zeros([m,n])
xVariable = np.column_stack((np.ones([m,1]), xVariable[:m,:]))
mx,nx = xVariable.shape


def funcSingle(beta, x):
    return beta[0]*x[:,0]+beta[1]*x[:,1]+beta[2]*x[:,2]+beta[3]*x[:,3]+beta[4]*x[:,4]+beta[5]*x[:,5]+beta[6]*x[:,6]

def funcTotal(beta, x):
    return beta[0]*x[:,0]+beta[1]*x[:,1]+beta[2]*x[:,2]+beta[3]*x[:,3]+beta[4]*x[:,4]+beta[5]*x[:,5]+beta[6]*x[:,6]+beta[7]*x[:,7]

Beta_VaRsysM = qreg.quantile_regression(funcSingle,xVariable,MVCTotal,[1,1,1,1,1,1,1],q_value = 0.5).x   
VaRsysM = Beta_VaRsysM[0]*xVariable[:,0]+Beta_VaRsysM[1]*xVariable[:,1]+Beta_VaRsysM[2]*xVariable[:,2]+Beta_VaRsysM[3]*xVariable[:,3]+\
    Beta_VaRsysM[4]*xVariable[:,4]+Beta_VaRsysM[5]*xVariable[:,5]+Beta_VaRsysM[6]*xVariable[:,6]    
for i in range(n):
    Beta_VaRq = qreg.quantile_regression(funcSingle,xVariable,MVCsingle[:,i],[1,1,1,1,1,1,1],q_value = 0.05).x
    VaRq[:,i] =  Beta_VaRq[0]*xVariable[:,0]+Beta_VaRq[1]*xVariable[:,1]+Beta_VaRq[2]*xVariable[:,2]+Beta_VaRq[3]*xVariable[:,3]+\
    Beta_VaRq[4]*xVariable[:,4]+Beta_VaRq[5]*xVariable[:,5]+Beta_VaRq[6]*xVariable[:,6]                         
    XVariable = np.column_stack((xVariable, MVCsingle[:,i]))
    Beta_CoVaR = qreg.quantile_regression(funcTotal,XVariable,MVCTotal,[1,1,1,1,1,1,1,1],q_value = 0.05).x
    CoVaR[:,i] = Beta_CoVaR[0]*XVariable[:,0]+Beta_CoVaR[1]*XVariable[:,1]+Beta_CoVaR[2]*XVariable[:,2]+Beta_CoVaR[3]*XVariable[:,3]+\
    Beta_CoVaR[4]*XVariable[:,4]+Beta_CoVaR[5]*XVariable[:,5]+Beta_CoVaR[6]*XVariable[:,6]+Beta_CoVaR[7]*VaRq[:,i]
    deltaCoVaR[:,i] = CoVaR[:,i] - VaRsysM
deltaCoVaR = -deltaCoVaR
deltaCoVaR = DataFrame(deltaCoVaR.T, index = list(names)).T
deltaCoVaR.to_excel('deltaCoVaR.xlsx',sheet_name = 'Sheet1') 
print(np.mean(deltaCoVaR.iloc[1:,:],axis=0).sort_values())
