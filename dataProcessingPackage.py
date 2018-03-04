#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 09:03:13 2017
timeSeriesMatch按照样本的时间 在数据集中匹配相应的数据
panelMatch以按照样本某个特征 在数据集中匹配相应时间和特征的数据
readWindExcel
frequencyDeal
getFeaturesWind
@author: hudie
"""
import pandas as pd
from pandas import DataFrame,Series
import sys
import numpy as np
import re
from datetime import *
from imp import reload 

from WindPy import *
from datetime import *
w.start()

#frequency = [3, 1, 3, 12],timeList是月度:1，季度:3，半年:6，还是年:12
   
#将时间序列数据按照allcororatebonds中债券到期的时间选出来，并按照其排列顺序排列
#timeList, dataList,nameList 必须一一对应，长度一样
def timeSeriesMatch(timeList, dataList, nameList, maturityDate):
    addDict = {}
    for i, timeset in enumerate(timeList):
        frequency = timeset[1]
        time = timeset[0]
        data = dataList[i]
        name = nameList[i]
        addDict[name] = []
        if data.shape[0] == len(time):
            for j, maturity in enumerate(maturityDate):
                tempdate = [] #*****记得设为空 不然得到的CPI都一样 因为list接着append
                maturity = str(maturity)[:10]        
                if str(min(time))[:10] > maturity:
                   tempdata = data.iloc[time.index(min(time))].values[0]
                   addDict[name].append(tempdata)
                else:
                    for k, date in enumerate(time):
                        date = str(date)[:10]
                        if maturity > date:
                            tempdate.append(date)
                    tempdate.sort() #date 一定要是一个上升的趋势 才能对上time和data的index
                    if frequency == 1:
                        tempdata = data.iloc[max(tempdate.index(max(tempdate)) -6,0)].values[0]
                    elif frequency == 3:
                        tempdata = data.iloc[max(tempdate.index(max(tempdate)) -2,0)].values[0]
                    elif frequency == 6:
                        tempdata = data.iloc[max(tempdate.index(max(tempdate)) -1,0)].values[0]
                    else:
                        tempdata = data.iloc[max(tempdate.index(max(tempdate)),0)].values[0] 
                    addDict[name].append(tempdata)
        else:
            print('错误：数据时间与时间列表长度不符合！')
    return addDict
        
#读取面板数据 timepanellist datapanellist namepanellist searchbench 必须一一对应 长度一致 matchnumber是指从数据集字段名称的哪里开始匹配
def panelMatch(timePanelList, dataPanelList, namePanelList, searchBench, maturityDate, matchNumberMinList, matchNumberMaxList):
    addDictPanel = {}
    for i in range(len(searchBench)):
        provinces = searchBench[i] 
        fisicalPd = dataPanelList[i]
        fisicalTime = timePanelList[i][0]
        frequency = timePanelList[i][1]
        namePanel = namePanelList[i]
        matchNumberMin = matchNumberMinList[i]
        matchNumberMax = matchNumberMaxList[i]
        addDictPanel[namePanel] = []
        for j, province in enumerate(provinces):
            tempdate = []
            maturityPanel = str(maturityDate[j])[:10]
            for key in fisicalPd.keys():
                matchWord = key[matchNumberMin:matchNumberMax]
                pattern = re.compile(matchWord)
                match = pattern.match(str(province))
                if match:
                    dataPanel = fisicalPd[key] 
                    if str(min(fisicalTime))[:10] > maturityPanel:
                        tempdata = dataPanel.iloc[fisicalTime.index(min(fisicalTime))]
                        addDictPanel[namePanel].append(tempdata)
                    else:
                        for fisicaldate in fisicalTime:
                            if maturityPanel > str(fisicaldate)[:10]:
                                tempdate.append(fisicaldate)
                        tempdate.sort()
                        if frequency == 1:
                            tempdata = dataPanel.iloc[max(tempdate.index(max(tempdate))-6,0)]
                        elif frequency == 3:
                            tempdata = dataPanel.iloc[max(tempdate.index(max(tempdate))-2,0)]
                        elif frequency == 6:
                            tempdata = dataPanel.iloc[max(tempdate.index(max(tempdate))-1,0)]
                        else:
                            tempdata = dataPanel.iloc[max(tempdate.index(max(tempdate)),0)]
                        addDictPanel[namePanel].append(tempdata)
                #前提是第一次的时候match对了，如果与pattern的开头一样的话
                if len(tempdate) != 0:
                    break                
            if len(tempdate) == 0:
                addDictPanel[namePanel].append(None)
    return addDictPanel

#从WIND上提取数据的格式较为统一
def readWindExcel(path):
    data = pd.read_excel(path, header=0, sheet_name = 'sheet1')
    data = data[1:-2]
    dataTime = list(data['指标名称'])
    del data['指标名称']
    columns = data.keys()
    datanp = np.array(data)
    data = DataFrame(datanp, columns = columns, index = dataTime)
    return data, dataTime

def frequencyDeal(price,period,days):
    priceData = []
    priceIndex = []
    for i in range(period):
        priceData.append((price.iloc[(i+1)*days] - price.iloc[i*days])/price.iloc[i*days])
        priceIndex.append(price.index[(i+1)*days])
    priceData = DataFrame(priceData, index = priceIndex)
    priceTime = [i.date() for i in priceIndex]
    return priceData,priceTime

def getFeaturesWind(features, forwardYear, maturityDate, allCorporateBonds):
    featureDict = {}
    for feature in features:
        index = 0
        for md in maturityDate:
            tempMonth = 0
            mdstr = str(md)[:10]
            mddate = md.date()
            month = mddate.month
            tempYear = mddate.year
            if month <= 6:
                tempMonth = 6 + month    
                tempYear = tempYear - (forwardYear + 1)
            else:
                tempMonth = month - 6
                tempYear = tempYear - forwardYear
            beginDateStr = str(tempYear) + '-' + str(tempMonth) + '-'+'01'
            debtCode = allCorporateBonds['证券代码'][index]
            data = w.wsd(debtCode, feature, beginDateStr, mdstr , "Period=Q")
            featureSeries = Series(data.Data[0])
            featureSeriesNotNull = featureSeries.dropna()
            if len(featureSeriesNotNull) == 0:
                featureNum = None
            else:
                featureNum = featureSeries[max(featureSeriesNotNull.index)]
            if not (feature in featureDict):
                featureDict[feature] = []
            featureDict[feature].append(featureNum)
            index += 1
            print(index)
    return DataFrame(featureDict)

def financialfeatures(forwardYear,maturityDate,allCorporateBonds):
    features = ["netprofitmargin","optoebt","deductedprofittoprofit","operateincometoebt",\
            "roa_yearly","ocftoinveststockdividend","ocftoop","ocftoassets",\
            "ocftodividend","debttoassets","deducteddebttoassets","longcapitaltoinvestment",\
            "assetstoequity","catoassets","currentdebttoequity","intdebttototalcap",\
            "equitytototalcapital","currentdebttodebt","current","quick",\
            "cashratio","cashtocurrentdebt","ocftointerest","ocftoquickdebt",\
            "tangibleassettodebt","tangibleassettonetdebt","debttotangibleequity",\
            "ebitdatodebt","ocftoshortdebt","ocftonetdebt","ocficftocurrentdebt",\
            "ocficftodebt","ebittointerest","longdebttoworkingcapital","longdebttodebt",\
            "netdebttoev","interestdebttoev","ebitdatointerestdebt","ebitdatointerest",\
            "tltoebitda","cashtostdebt","invturn","arturn","caturn","operatecaptialturn",\
            "faturn","non_currentassetsturn","apturn","yoyprofit","yoynetprofit_deducted",\
            "yoyocf","maintenance","yoy_cash","yoy_fixedassets","yoycf","yoydebt","roe","z_score"]
    searchDict = {"netprofitmargin":'销售净利率',"optoebt":'主营业务比率',"deductedprofittoprofit":'扣除非经常损益后的净利润/净利润',"operateincometoebt":'经营活动净收益/利润总额',\
            "roa_yearly":'年化ROA',"ocftoinveststockdividend":'现金满足投资比率',"ocftoop":'现金营运指数',"ocftoassets":'全部资金回收率',\
            "ocftodividend":'现金股利保障倍数',"debttoassets":'资产负债率',"deducteddebttoassets":'剔除预收款项后的资产负债率',"longcapitaltoinvestment":'长期资产合适率',\
            "assetstoequity":'权益乘数',"catoassets":'流动资产/总资产',"currentdebttoequity":'流动负债权益比',"intdebttototalcap":'带息债务/全部投入资本',\
            "equitytototalcapital":'归属母公司股东的权益/全部投资资本',"currentdebttodebt":'流动负债/负债合计',"current":'流动比率',"quick":'速动比率',\
            "cashratio":'保守速动比率',"cashtocurrentdebt":'现金比率',"ocftointerest":'现金流量利息保障倍数',"ocftoquickdebt":'现金到期债务比',\
            "tangibleassettodebt":'有形资产/负债合计',"tangibleassettonetdebt":'有形资产/净债务',"debttotangibleequity":'有形净值债务率',\
            "ebitdatodebt":'息税折旧摊销前利润/负债合计',"ocftoshortdebt":'经营活动产生的现金流量净额/流动负债',"ocftonetdebt":'经营活动产生的现金流量净额/净债务',"ocficftocurrentdebt":'非筹资性现金净流动/流动负债',\
            "ocficftodebt":'非筹资性现金净流动/负债总额',"ebittointerest":'已获利息倍数（EBIT/利息费用）',"longdebttoworkingcapital":'长期债务/营运资金',"longdebttodebt":'长期负债占比',\
            "netdebttoev":'净债务/股权价值',"interestdebttoev":'带息债务/股权价值',"ebitdatointerestdebt":'EBITDA/带息债务',"ebitdatointerest":'EBITDA/利息费用',\
            "tltoebitda":'全部债务/EBITDA',"cashtostdebt":'货币资金/短期债务',"invturn":'存货周转率',"arturn":'应收账款周转率',"caturn":'流动资产周转率',"operatecaptialturn":'营运资产周转率',\
            "faturn":'固定资产周转率',"non_currentassetsturn":'非流动资产周转率',"apturn":'应付账款周转率',"yoyprofit":'净利润（同比增长率）',"yoynetprofit_deducted":'归属母公司股东的净利润-扣除非经营损失（同比增长率）',\
            "yoyocf":'经营活动产生的现金流净额（同比增长率)',"maintenance":'资本项目规模维持率',"yoy_cash":'货币资金增长率',"yoy_fixedassets":'固定资产投资扩张率',"yoycf":'现金净流量（同比增长率）',"yoydebt":'总负债（同比增长率）',"roe":'净资产收益率',"z_score":'z值'}
#    forwardYear = 1
#    maturityDate = list(allCorporateBonds['到期日期'])
    res =  getFeaturesWind(features, forwardYear,maturityDate, allCorporateBonds)
return res
