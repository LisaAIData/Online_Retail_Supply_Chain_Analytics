#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 12:34:18 2022

@author: lisa_hu
"""
####——————— S10.150 Preparing data for Regression————————
import pandas as pd
import numpy as np
import seaborn as sns
retail_clean = pd.read_csv('retail_clean.csv')

#查看数据类型，将日期转化成datetime格式
retail_clean.info()
retail_clean['InvoiceDate'] = pd.to_datetime(retail_clean['InvoiceDate'])
#创建新date, month, year, week列
retail_clean['date'] = retail_clean['InvoiceDate'].dt.strftime('%Y-%m-%d')
retail_clean['date'] = pd.to_datetime(retail_clean['date'])

retail_clean['month'] = retail_clean.date.dt.month
retail_clean['year'] = retail_clean.date.dt.year
retail_clean['week'] = retail_clean.date.dt.isocalendar().week

retail_clean.columns
retail_clean.month.describe()
'''count    779495.000000
mean          7.417110
std           3.422346
min           1.000000
25%           5.000000
50%           8.000000
75%          11.000000
max          12.000000
Name: month, dtype: float64
'''

time_series = retail_clean.groupby(['week','month','year']).agg(date = ('date','first'),
                                     total_revenue=('Revenue',np.sum)).reset_index().sort_values('date')

sns.lineplot(x='date',y='total_revenue',data=time_series)

time_series.to_csv('lisa_timeseries.csv')


#—————154. Regression in Python —————
from sklearn.linear_model import LinearRegression
# 定义x值，independent variables，创建 trend 列
time_series['trend'] = range(time_series.shape[0])
# 创建month列，数据类型为category
time_series['month'] = time_series['month'].astype('category')
# month列的值是对应date列中的月份
time_series['month'] = time_series['date'].dt.month
##### dropping columns 删除指定列
X = time_series.drop(['week','year','date','total_revenue'], axis=1)
#将x的列名组合成新的列名names
names = pd.get_dummies(X).columns
# x和y赋值
X = pd.get_dummies(X).values
# 定义y值为total_revenue的值
y = time_series.total_revenue.values

# 创建线性回归模型
model = LinearRegression()
model.fit(X, y)
# 查看回归参数，coefficient值
model.get_params() 
model.coef_
# 获得dict1每trend月份对应的coef系数值
dict1 = list(zip(names,model.coef_))
#创建prediction列表并赋值
prediction = model.predict(X)
time_series['prediction'] = prediction

# 创建实际与预测营收图表
import matplotlib.pyplot as plt
###日期与实际总收益图
plt.plot(time_series.date, time_series.total_revenue, label = 'Actual')
###日期与预测收益图
plt.plot(time_series.date, time_series.prediction, label = 'Prediction')
plt.legend(loc='upper left')
plt.show()

#——————156.Forecasting——————
max_date = time_series.date.max()
# 创建时间范围的dates列表，以周为单位
dates = pd.DataFrame({'date' : pd.date_range('2011-12-12','2012-02-05', freq='w')})
''' 输出：
     date
0 2011-12-18
1 2011-12-25
2 2012-01-01
3 2012-01-08
4 2012-01-15
5 2012-01-22
6 2012-01-29
7 2012-02-05
'''
# 新增拼接列：将新创建的date列，拼接到原先的time_series列中。
time_series = pd.concat([time_series,dates], axis=0)
#与上文相同 定义x值，independent variables，创建 trend 列
time_series['trend'] = range(time_series.shape[0])
# 创建month列，数据类型为category
time_series['month'] = time_series['month'].astype('category')
# month列的值是对应date列中的月份
time_series['month'] = time_series['date'].dt.month
##### dropping columns 删除指定列
X = time_series.drop(['week','year','date','total_revenue'], axis=1)
#将x的列名组合成新的列名names
names = pd.get_dummies(X).columns
# x和y赋值
X = pd.get_dummies(X).values
# 创建prediction函数和列表
prediction  = model.predict(X)
time_series['prediction'] = prediction

###日期与实际总收益图
plt.plot(time_series.date, time_series.total_revenue, label = 'Actual')
###日期与预测收益图
plt.plot(time_series.date, time_series.prediction, label = 'Prediction')
plt.legend(loc='upper left')
plt.show()
