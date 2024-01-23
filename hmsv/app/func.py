import pmdarima as pm
import pandas as pd

def dataResize(data):

  resizeDataList = []

  for idx in range(len(data)):

      resizeDataList.append(data[idx] / 1000000)

  return resizeDataList


def useAutoArima(trainData, m=4):

  arimaModel = pm.auto_arima(trainData, m=m, trace=False)

  return arimaModel


def predictionData(model, periodsNum): ## periodsNum : 모델의 예측 값 개수

  predData = model.predict(n_periods=periodsNum, return_conf_int=True)

  return predData


def dateConvert(data):

  convertList = []

  for i in data.index:

    temp = pd.to_datetime(i)
    convertList.append(temp.strftime('%Y-%m'))

  return convertList


def totalYear(data):

  tempList = []

  for date in data.index:
    tempList.append(int(date[:4]))

  return list(set(tempList))


def sumQuarterly(data, annual, columnName=0):

  annualDict = {}
  totalYearList = totalYear(data)

  if annual == '09':

    for year in totalYearList:

      dictKey = year
      quarterlyList = []

      for month in ['-09', '-06', '-03', '-12']:

        if month == '-12': 
          year -= 1
        
        checkDate = str(year)+month

        if checkDate in data.index:

          quarterlyList.append(data.loc[checkDate, columnName])
      
      annualDict[dictKey] = quarterlyList

  elif annual == '06':

    for year in totalYearList:

      dictKey = year
      quarterlyList = []

      for month in ['-06', '-03', '-12', '-09']:

        if month == '-12' or month == '-09': 
          year -= 1
        
        checkDate = str(year)+month

        if checkDate in data.index:

          quarterlyList.append(data.loc[checkDate, columnName])
      
      annualDict[dictKey] = quarterlyList

  elif annual == '03':

    for year in totalYearList:

      dictKey = year
      quarterlyList = []

      for month in ['-03', '-12', '-09', '-06']:

        if month != '-03': 
          year -= 1
        
        checkDate = str(year)+month

        if checkDate in data.index:

          quarterlyList.append(data.loc[checkDate, columnName])
      
      annualDict[dictKey] = quarterlyList

  elif annual == '12':

    for year in totalYearList:

      dictKey = year
      quarterlyList = []

      for month in ['-12', '-09', '-06', '-03']:
        
        checkDate = str(year)+month

        if checkDate in data.index:

          quarterlyList.append(data.loc[checkDate, columnName])
      
      annualDict[dictKey] = quarterlyList
  
  return annualDict