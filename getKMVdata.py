#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 14:54:22 2017

@author: Administrator
"""
import pandas as pd
from pandas import DataFrame,Series
import sys
import numpy as np
import re
from datetime import *
from imp import reload 
import scipy.io as sio

from WindPy import *
from datetime import *
w.start()

#国债1年期收益率
data5 = w.wsd("CGB1Y.WI", "close,wgsd_liabs_curr,wgsd_liabs_lt,wgsd_stkhldrs_eq", "2011-01-01", "2017-08-24", "unit=1;rptType=1;currencyType=;PriceAdj=F")
riskFreeRate = DataFrame(data5.Data).T[0]

codesList = ["002506.SZ","002306.SZ","000659.SZ","600188.SH","600795.SH","002594.SZ","600783.SH"]
nameList = ['chaori','xiange','zhongfu','chongzhou','guoli','biyadi','luxinzhai']
beginTime = "2011-01-01"
endTime = "2017-08-24"
def KMVDataWind(codesList,nameList,beginTime,endTime,riskFreeRate):
    inputDict = {}
    for i,code in  enumerate(codesList):
        dataWind = w.wsd(code, "close,wgsd_liabs_curr,wgsd_liabs_lt,wgsd_stkhldrs_eq", \
                         beginTime, endTime, "unit=1;rptType=1;currencyType=;PriceAdj=F")
        data = DataFrame(dataWind.Data).T
        dataTime = DataFrame(dataWind.Times)
        inputDict[nameList[i]] = {}
        inputDict[nameList[i]]['debt'] = []
        inputDict[nameList[i]]['equity'] = []
        inputDict[nameList[i]]['sigma'] = []
        inputDict[nameList[i]]['riskFreeRate'] = []
        inputDict[nameList[i]]['time'] = []
        inputDict[nameList[i]]['tau'] = []
        dataIndex = list(data.iloc[:,1:4].dropna().index)
        dataIndex.insert(0,0)
        price = data[0]
        currentDebt = data[1][dataIndex[1:]]
        longDebt = data[2][dataIndex[1:]]
        equity = data[3][dataIndex[1:]]
        time = dataTime[0][dataIndex[1:]]
        debt = currentDebt + 0.5*longDebt
        debt = debt.shift(-1)
        ndataIndex = len(dataIndex)
        stdList = []
        rateList = []
        tauList = []
        for j in range(ndataIndex-1):
            std = np.std(price[dataIndex[j]:dataIndex[j+1]])*np.sqrt(252)
            stdList.append(std)
            rate = np.mean(riskFreeRate[dataIndex[j]:dataIndex[j+1]])
            rateList.append(rate)
            tau = (dataIndex[j+1]-dataIndex[j])/252
            tauList.append(tau)
        tauSeries = Series(tauList).shift(-1)
        inputDict[nameList[i]]['tau'].append(tauSeries)
        inputDict[nameList[i]]['debt'].append(debt)
        inputDict[nameList[i]]['equity'].append(equity)
        inputDict[nameList[i]]['sigma'].append(stdList)
        inputDict[nameList[i]]['riskFreeRate'].append(rateList)     
        inputDict[nameList[i]]['time'].append(time)
    return inputDict
inputDict =  KMVDataWind(codesList,nameList,beginTime,endTime,riskFreeRate)
sio.savemat('F:\\GFsummer2017\\inputDict.mat', inputDict)  
