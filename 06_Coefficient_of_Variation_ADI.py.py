#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 14:13:49 2022

@author: lisahu
"""
#——————189. Holidays————————
import pandas as pd
retail = pd.read_csv('retail_clean.csv')
# 查看retail数据
retail.info()
# 转换Invoice Date数据类型
retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'])
# 创建新列，表示在周的第几天
retail['dayofweek'] = retail['InvoiceDate'].dt.dayofweek
# 查看周天总数
retail['dayofweek'].value_counts()
retail['date'] = retail['InvoiceDate'].dt.strftime('%Y-%m-%d')
retail['date'] = pd.to_datetime(retail['date'])
''' 0是周一，1是周二 。。。 6是周日。 
3    156012
1    134028
2    130782
6    130141
0    124957
4    103175
5       400
In this case, 假设 no holidays
'''
#——————190.Coefficient of Variation Squared (CV²) ——————
# the square of the Coefficient of Variation (CV²) measures the variation in quantities.
retail_grouped = retail.groupby(['Description','date']).agg(total_sales=('Quantity','sum')).reset_index()
cv_data = retail_grouped.groupby('Description').agg(average=('total_sales','mean'),
                                                    sd=('total_sales','std')).reset_index()
cv_data['cv_squared'] = (cv_data['sd']/cv_data['average'])**2

#——————191.Average Demand Interval (ADI)——————
#Average Demand Interval (ADI) measures the demand regularity in time by computing the average interval between two demands.
product_by_date = retail.groupby(['Description','date']).agg(count=('Description','count')).reset_index()
skus = product_by_date.Description.unique()
# 每个产品上一次购买的日期与这次购买的日期
empty_dataframe = pd.DataFrame()
for sku in skus:
    a = product_by_date[product_by_date.Description == sku]
    a['previous_date'] = a['date'].shift(1)
    empty_dataframe = pd.concat([empty_dataframe, a], axis=0)
    
empty_dataframe['Duration'] = empty_dataframe['date'] - empty_dataframe['previous_date']
# 转换duration日期格式
empty_dataframe['duration'] = empty_dataframe['Duration'].astype('string').str.replace('days','')
empty_dataframe['duration'] = pd.to_numeric(empty_dataframe['duration'], errors='coerce')

ADI = empty_dataframe.groupby('Description').agg(ADI = ('duration', 'mean')).reset_index()
adi_cv = pd.merge(ADI,cv_data)

def category(dataframe):
    a=0
    if((dataframe['ADI']<= 1.34) & (dataframe['cv_squared']<= 0.49)):
        a='Smooth'
    if((dataframe['ADI']>= 1.34) & (dataframe['cv_squared']>= 0.49)):
        a='Lumpy'
    if((dataframe['ADI']< 1.34) & (dataframe['cv_squared']> 0.49)):
        a='Erratic'
    if((dataframe['ADI']> 1.34) & (dataframe['cv_squared']< 0.49)):
        a='Intermittent'
    return a

adi_cv['category'] = adi_cv.apply(category, axis=1)

import seaborn as sns
sns.scatterplot(x='cv_squared', y='ADI', hue='category', data=adi_cv)

# 检查0，0意味着仅购买一次
adi_cv[adi_cv.category==0]

adi_cv.category.value_counts()
'''
Lumpy           4246
Intermittent     726
0                210
Erratic           91
Smooth            10
'''
