#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 21:39:39 2022

@author: lisa_hu
"""
##### Date in Python
##——————————————102 datetime————————————————
import pandas as pd
from datetime import datetime
import numpy as np
retail = pd.read_csv('online_retail2.csv')

## 去重
retail = retail.drop_duplicates()
## 清除空项 NA所在的行
retail = retail.dropna(axis=0, how='any')
## 查询列表信息，可以看到，InvoiceDate的数据类型Dtype是 object,应转为datetime格式
retail.info()

##转化为date time格式
retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'])

## 使用 .dt.可提取任意年月日的值
retail['InvoiceDate'].dt.year
retail['InvoiceDate'].dt.month
retail['InvoiceDate'].dt.week
retail['InvoiceDate'].dt.day


## 根据某一指定日期，改变format。如将12月 改为 December
retail['InvoiceDate'].dt.strftime('%B %Y')
## 最大的日期.max(),最小日期.min()
retail['InvoiceDate'].max() #方法一
retail['InvoiceDate'].min()
## 求日期范围duration
retail['InvoiceDate'].max()-retail['InvoiceDate'].min()



######——————————————103 Last Purchase————————————————
##max date of dataset
max_date = retail.InvoiceDate.max() ##同上，方法二

retail.columns
last_purchase_date = retail.groupby('Customer ID',as_index=False)['InvoiceDate'].max()

last_purchase_date['Recency'] = max_date - last_purchase_date['InvoiceDate']
last_purchase_date['Recency'].describe()
'''
count                           5942
mean     202 days 10:33:55.930663076
std      211 days 21:00:52.495651984
min                  0 days 00:00:00
25%                 24 days 01:41:45
50%                 95 days 12:20:00
75%                380 days 22:12:00   75%客户最近购买的日期是380天前，意味着客户不活跃、流失
max                738 days 02:55:00
'''


### ——————————————104 History Histogram历史数据直方图————————————————
import matplotlib as plt
## Recency转为numeric
last_purchase_date['Recency_days'] = last_purchase_date['Recency'].dt.components['days']
plt.hist(last_purchase_date['Recency_days'])


### ——————————————105 Inter-Arrival Time ————————————————
#获取每个unique customer
customers = np.unique(retail['Customer ID'])
#查看客户数量
len(customers)

#去除retail InvoiceDate里的时秒，只选取年月日
retail['date'] = retail['InvoiceDate'].dt.strftime('%Y-%m-%d')

customer_gouped = retail.groupby(['Customer ID','date'],as_index=False).count()[['Customer ID','date']]
'''
       Customer ID        date
0          12346.0  2009-12-14
1          12346.0  2009-12-18
2          12346.0  2010-01-04
3          12346.0  2010-01-14
4          12346.0  2010-01-22
           ...         ...
38497      18287.0  2010-09-21
38498      18287.0  2010-11-22
38499      18287.0  2011-05-22
38500      18287.0  2011-10-12
38501      18287.0  2011-10-28
'''


### 每个顾客上一次购买日期
inter_data = pd.DataFrame()
for customer in customers:
    c_d = customer_gouped[customer_gouped['Customer ID']==customer]  #筛选每位顾客
    c_d['previous_date']=c_d['date'].shift(1)
    inter_data = pd.concat([inter_data,c_d],axis=0)

inter_data

### duration 距离上一次购买有多长时间
inter_data.info()  #可以看出date和previous_date数据类型是object，所以需要转化成datetime
inter_data['date'] = pd.to_datetime(inter_data['date'])
inter_data['previous_date'] = pd.to_datetime(inter_data['previous_date'])

inter_data['duration'] = inter_data['date'] - inter_data['previous_date']
inter_data['duration'] = inter_data['duration'].dt.components['days']

inter_arrival = inter_data.groupby('Customer ID')['duration'].mean()

''' 每个客户距离上一次购买的平均天数
Customer ID
12346.0     40.000000
12347.0     57.428571
12348.0     90.750000
12349.0    179.250000
12350.0           NaN
   
18283.0     36.388889
18284.0      2.000000
18285.0           NaN
18286.0    123.500000
18287.0    116.000000
Name: duration, Length: 5942, dtype: float64
'''


#####—————————————————————— 108. Resampling ——————————————————————
stocks = pd.read_csv('stocks.csv')
stocks

# 使用info查看数据类型，可见Date数据类型是object，应转化为datetime
stocks.info()

# 在import时就指定index哪个keys。 index_col将第一列设为Date, parse_dates将某一列解析为时间索引
import pandas as pd
stocks = pd.read_csv('stocks.csv',index_col='Date',parse_dates=True)

stocks   #将第一列指定为日期后，便于后续作图
stocks.plot()
stocks['2012'].plot()
stocks['2002':'2013'].plot()
stocks['2003':'2013'].plot()['IBM']


yearly_series_mean = stocks.resample('Y').mean()    #年均库存量
monthly_series_mean = stocks.resample('M').mean()  #月均库存量
quarter_series_mean = stocks.resample('Q').mean()  #季度均库存量
weekly_series_sum = stocks.resample('W').sum()   #周总库存量
daily_series_mean = stocks.resample('D').mean()    #日均库存量

monthly_series_mean.plot()
#sum(), first(), mean(), last()
weekly_series_sum = stocks.resample('W').sum()   #周总库存量



#####—————————————————————— 109. Rolling time series / Moving average ——————————————————————
MSFT = stocks[['MSFT']]

MSFT['rolling_weekly'] = MSFT.rolling(window = 7).mean()
MSFT['rolling_monthly'] = MSFT['MSFT'].rolling(window = 30).mean()

MSFT.plot()   # 从图中可看出，plot图像非常长。以下可修改样本时间段
MSFT['rolling_monthly'].plot()
MSFT['Aug-2011':'Dec-2011'].plot()

### rolling 可用于库存管理




