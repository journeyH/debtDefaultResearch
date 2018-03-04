#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 09:57:33 2017

@author: hudie
"""

import pandas as pd
from pandas import DataFrame,Series
import sys
sys.path.append('F:\\GFsummer2017')
import numpy as np
import re
import processingData
from imp import reload
reload(processingData)

from WindPy import *
from datetime import *
w.start()

'''待处理样本数据集 '''
allCorporateBonds = pd.read_excel('F:\\GFsummer2017\\到期公司债.xlsx',sheet_name = 'Sheet1')
allCorporateBonds = allCorporateBonds[:-2]
allCorporateBonds.rename(columns = {'到期日期↓' : '到期日期'}, inplace=True)
'''违约样本数据集'''
defaultFrame = pd.read_excel('F:\\GFsummer2017\\违约债券报表.xlsx',sheet_name = 'Sheet1')
defaultName = defaultFrame['名称'].dropna()
debtRemainIndex = []
matchWord = [r'[^S]CP',r'MTN',r'PPN',r'SCP']
for index in range(len(defaultName)):
    text = defaultName[index]
    count = 0
    for subPattern in matchWord:
        pattern = re.compile(subPattern)
        match = pattern.search(text)
        if match:
            continue
        else:
            count += 1
            if count == len(matchWord):
               debtRemainIndex.append(index)
defaultDebtRemain = defaultFrame.iloc[debtRemainIndex]
defaultdebtCorporateBonds = defaultDebtRemain['Wind债券二级分类'] == '一般企业债'
defaultdebtABS = defaultDebtRemain['Wind债券二级分类'] == '证监会主管ABS'
defaultdebtNAN = defaultDebtRemain['Wind债券二级分类'].isnull()
defaultdebtCBABSNAN = (defaultdebtCorporateBonds | defaultdebtABS) | defaultdebtNAN
defaultDebt = defaultDebtRemain[~defaultdebtCBABSNAN]
'''将待处理样本数据集中的到期日期变为违约样本数据集中的违约日期，并对违约样本编码1 对未违约样本编码0'''
label = {}
label['label'] = []
allCorDefault = []
for i,maturitycode in enumerate(allCorporateBonds['证券代码']):
    count = 0
    for j,defaultcode in enumerate(defaultDebt['代码']):
        if defaultcode == maturitycode:
            allCorporateBonds['到期日期'].iloc[i] =  defaultDebt['发生日期'].iloc[j]
            label['label'].append(1)
            allCorDefault.append(allCorporateBonds.iloc[i])
            count += 1
            break #对于某只债券二次违约的只匹配第一违约
    if count == 0:
         label['label'].append(0)
allCorDefault = DataFrame(allCorDefault)
allCorporateBonds = pd.concat([allCorporateBonds,DataFrame(label)], axis=1)   
'''计算已发行债券总数'''
corSum = allCorporateBonds['公司发行证券一览']
corSumNum = []
for bonds in corSum:
    bondsList = re.split(';',bonds)
    corSumNum.append(len(bondsList))
corSumNum = DataFrame(corSumNum, columns = ['已发债总数'])
allCorporateBonds = pd.concat([allCorporateBonds,corSumNum], axis=1) 
'''获取财务数据,注释掉的语句即可，但是数据量太大，获取时间很长，这里用已经获取储存的文件读入'''
financialfeatures = pd.read_excel('F:\\GFsummer2017\\financialfeatures1.xlsx')
allCorporateBonds = pd.concat([allCorporateBonds,financialfeatures], axis=1)
financialfeatures.dropna(how = 'all',inplace = True)
allCorporateBonds = allCorporateBonds.iloc[list(financialfeatures.index)]
allCorporateBonds = pd.concat([allCorporateBonds,allCorDefault], axis=0)
allCorporateBonds.drop_duplicates(subset=['证券代码'], keep='first', inplace=True)
allCorporateBonds['label'].fillna(1, inplace = True)

'''处理缺失值'''
nrows, ncols = allCorporateBonds.shape
totalMissingData = allCorporateBonds.isnull().sum().sort_values(ascending=False)
percentMissingData = (allCorporateBonds.isnull().sum()/allCorporateBonds.isnull().count()).sort_values(ascending=False)
missingData = pd.concat([totalMissingData,percentMissingData], axis=1, keys=['Total', 'Percent'])
sys.stdout.write('head information \n')
print(missingData.head(int(0.5*ncols)))
delColumns = percentMissingData > 0.15
for columns in list(delColumns.keys()):
    try:
        if delColumns[columns]:
            del allCorporateBonds[columns]
    except KeyError:
        continue

'''
加入对应时间的宏观变量
'''
'''get timeseries data'''
#1         
gdpCountry = w.edb('M0000541',"2010-08-03", "2017-08-03","Fill=Previous")
gdpCountryData = np.array(gdpCountry.Data)
gdpCountryTime = list(gdpCountry.Times)
gdpCountryData = DataFrame(gdpCountryData.T, columns = list(gdpCountry.Codes), index = gdpCountryTime)

#2 
CPI = w.edb('M0000729',"2010-08-03", "2017-08-03","Fill=Previous")
CPIData = np.array(CPI.Data)
CPITime = list(CPI.Times)
CPIData = DataFrame(CPIData.T, columns = list(CPI.Codes), index = CPITime)

#3
housePrice,housePriceTime = processingData.readWindExcel(u'F:\GFsummer2017\data\房价.xls')
#housePrice为月度数据，换算成半年度涨跌幅数据 共有80个月，13.3个半个年 
housePriceData,housePriceTime = processingData.frequencyDeal(housePrice,13,6)

#4 社会融资规模(TSF)
tsf, tsfTime = processingData.readWindExcel(u'F:\GFsummer2017\data\社会融资规模增速.xls')

#5 委托贷款增速
entrustLoan, entrustLoanTime = processingData.readWindExcel(u'F:\GFsummer2017\data\委托贷款.xls')

#6 信托贷款增速
trustLoan, trustLoanTime = processingData.readWindExcel(u'F:\GFsummer2017\data\信托贷款.xls')

#7 未贴现银行承兑汇票增速
undiscounted, undiscountedTime =  processingData.readWindExcel(u'F:\GFsummer2017\data\未贴现银行承兑汇票.xls')


#8 M2
M2,M2Time = processingData.readWindExcel(u'F:\GFsummer2017\data\货币供应量.xls')
M2Data,M2Time = processingData.frequencyDeal(M2,11,6)

#9 oil price
oilPrice, oilPriceTime = processingData.readWindExcel(u'F:\GFsummer2017\data\油价数据.xls')
oilPrice = DataFrame(oilPrice['OPEC:一揽子原油价格'])
#oilprice为日度数据，换算成半年度涨跌幅数据 共有1683天 13.4个半个年 因此每个区间大概为126天
oilPriceData,oilPriceTime = processingData.frequencyDeal(oilPrice,13,126)

#10 11 12 nterest rate corridor (IRC)利率走廊数据  
IRC,IRCTime = processingData.readWindExcel(u'F:\GFsummer2017\data\利率走廊数据.xls')
reverseRepo = DataFrame(IRC['逆回购利率:7天'])
excessReserve = DataFrame(IRC['超额存款准备金率(超储率):金融机构'])
SLF =  DataFrame(IRC['常备借贷便利(SLF)利率:7天'])

#上证指数
stock,stockTime = processingData.readWindExcel(u'F:\GFsummer2017\data\上证指数.xlsx')
stock = DataFrame(stock['收盘价(元)'])
stock = np.log(stock/stock.shift(1))
stock = stock[1:]
stockTime = stockTime[1:]

'''get panel data'''
#1
gdp = w.edb("M0048668,M0049108,M0048912,M0049080,M0049047,M0049034,M0049006,M0048972,M0048698,M0049014,\
      M0049148,M0048736,M0048752,M0049024,M0049071,M0048988,M0048997,M0048824,M0048862,M0048903,\
      M0048720,M0049098,M0048884,M0049130,M0049113,M0049088,M0048773,M0049062,M0049057,M0049119,\
      M0048949", "2010-08-03", "2017-08-03","Fill=Previous")
gdpData = np.array(gdp.Data)
gdpTime = list(gdp.Times)
gdpData = DataFrame(gdpData.T, columns = list(gdp.Codes), index = gdpTime)
gdpData.rename(columns = {"M0048668":'北京','M0049108':'天津','M0048912':'河北','M0049080':'山西',\
                          'M0049047':'内蒙古','M0049034':'辽宁','M0049006':'吉林','M0048972':'黑龙江',\
                          'M0048698':'上海','M0049014':'江苏','M0049148':'浙江','M0048736':'安徽',\
                          'M0048752':'福建','M0049024':'江西','M0049071':'山东','M0048988':'湖北',\
                          'M0048997':'湖南','M0048824':'广东','M0048862':'广西','M0048903':'海南',\
      'M0048720':'重庆','M0049098':'四川','M0048884':'贵州','M0049130':'云南','M0049113':'西藏',\
      'M0049088':'陕西','M0048773':'甘肃','M0049062':'青海','M0049057':'宁夏','M0049119':'新疆',\
      'M0048949':'河南'}, inplace = True)


#2
industry, industryTime = processingData.readWindExcel(u'F:\GFsummer2017\data\wind四级行业指数.xls')
#industry为日度数据，换算成半年度涨跌幅数据 共有4260天 35.4个半个年 因此每个区间大概为121天
industryData,industryTime = processingData.frequencyDeal(industry,35,121)
    

#3 地方财政收入 - 支出  
fisical = w.edb("M0025044,M0025868,M0025070,M0025900,M0025096,M0025932,\
      M0025122,M0025964,M0025148,M0025996,M0025174,M0026028,M0025200,M0026060,M0025226,M0026092,\
      M0025252,M0026124,M0025278,M0026156,M0025304,M0026188,M0025330,M0026220,M0025356,M0026252,\
      M0025382,M0026284,M0025408,M0026316,M0025434,M0026348,M0025460,M0026380,M0025486,M0026412,\
      M0025512,M0026444,M0025538,M0026476,M0025564,M0026508,M0025590,M0026540,M0025616,M0026572,\
      M0025642,M0026604,M0025668,M0026636,M0025694,M0026668,M0025720,M0026700,M0025746,M0026732,\
      M0025772,M0026764,M0025798,M0026796,M0025824,M0026828","2010-08-03", "2017-08-03","Fill=Previous")
fisicalTime = list(fisical.Times)
fisicalData  = np.array(fisical.Data).T
nrowsFisicalData, ncolsFisicalData = fisicalData.shape
fisicalNet = {}
fisicalCode = list(fisical.Codes)
for i in range(0,ncolsFisicalData,2):
    tempCode = fisicalCode[i]
    fisicalNet[tempCode] = []
    tempData = list(fisicalData[:,i] - fisicalData[:,(i+1)])
    fisicalNet[tempCode] = tempData
fisicalPd = DataFrame(fisicalNet, index = fisicalTime)
fisicalPd.rename(columns = {"M0025044":'北京','M0025070':'天津','M0025096':'河北',\
      'M0025122':'山西','M0025148':'内蒙古','M0025174':'辽宁','M0025200':'吉林','M0025226':'黑龙江',\
      'M0025252':'上海','M0025278':'江苏','M0025304':'浙江','M0025330':'安徽','M0025356':'福建',\
      'M0025382':'江西','M0025408':'山东','M0025434':'河南','M0025460':'湖北','M0025486':'湖南',\
      'M0025512':'广东','M0025538':'广西','M0025564':'海南','M0025590':'重庆','M0025616':'四川',\
      'M0025642':'贵州','M0025668':'云南','M0025694':'西藏','M0025720':'陕西','M0025746':'甘肃',\
      'M0025772':'青海','M0025798':'宁夏','M0025824':'新疆'}, inplace = True)

'''seachBench'''
maturityDate = list(allCorporateBonds['到期日期'])
provinces = allCorporateBonds['省份'] 
industries = allCorporateBonds[list(allCorporateBonds.keys())[48]]
#frequency = [3, 1, 3, 12],timeList是月度:1，季度:3，半年:6，还是年:12   
timeList = [(CPITime,1),(gdpCountryTime,3),(housePriceTime,6),(tsfTime,12),(M2Time,6),(oilPriceTime,6),\
            (IRCTime,6),(IRCTime,6),(IRCTime,6),(stockTime,6),(entrustLoanTime,12),(trustLoanTime,12),(undiscountedTime,12)]   
dataList = [CPIData,gdpCountryData,housePriceData,tsf,M2Data,oilPriceData,reverseRepo,excessReserve,SLF,stock,entrustLoan,trustLoan,undiscounted] 
nameList = ['CPI','gdpCountry','houseprice','tsf','M2','oilPrice','reverseRepo','excessReserve','SLF','stock','entrustLoan','trustLoan','undiscounted']  

timePanelList = [(fisicalTime,12),(gdpTime,3),(industryTime,6)]
dataPanelList = [fisicalPd,gdpData,industryData]
namePanelList = ['fisical','gdp','industry']
searchBench = [provinces,provinces,industries]
matchNumberMinList = [0,0,9]
matchNumberMaxList = [2,2,None] #正则化选择pattern.match

addDict = processingData.timeSeriesMatch(timeList, dataList, nameList, maturityDate)
addDictPanel = processingData.panelMatch(timePanelList, dataPanelList, namePanelList, searchBench, maturityDate,matchNumberMinList,matchNumberMaxList)

allCorporateBondsnp = np.array(allCorporateBonds)
nrow,ncol = allCorporateBondsnp.shape
columns = list(allCorporateBonds.keys())
index = list(range(nrow))
allCorporateBonds = DataFrame(allCorporateBondsnp, columns = columns, index = index)
allCorporateBonds = pd.concat([allCorporateBonds,DataFrame(addDict),DataFrame(addDictPanel)], axis=1)
allCorporateBonds.to_excel('sample.xlsx',sheet_name = 'Sheet1')
