#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 12:17:46 2022

@author: lisahu
"""
#————Customer Recency————
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

retail = pd.read_csv('retail_clean.csv')
# convert date
retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate']) #convert to datetime
retail['date'] = retail['InvoiceDate'].dt.strftime('%Y-%m-%d')
retail['date'] = pd.to_datetime(retail['date'])
# get the last purchase date of the whole orders
max_date = retail['date'].max()
# each customer's recency purchase date
retail.columns
customers_recency = retail.groupby('Customer ID').agg(last_date = ('date','max')).reset_index()
# the time period between each customer's recency date and the whole order's last purchase
customers_recency['recency'] = max_date - customers_recency['last_date']
customers_recency['recency'] = customers_recency['recency'].astype('string').str.replace('days','').astype(int) #convert datetype

#————Frequency————
freq2 = retail.groupby('Customer ID').date.count().reset_index() #count purchase date as frequency
freq2.columns = ['Customer ID','Frequency']

#————Monetary Value————
# get the total revenue for each invoice for each customer
money1 = retail.groupby(['Customer ID', 'Invoice']).agg(revenue = ('Revenue','sum')).reset_index()  
# Average monetary value
money2 = money1.groupby('Customer ID').agg(monetary_average = ('revenue','mean')).reset_index()

# Ranking customers 
customers_recency['rank_recency'] = customers_recency['recency'].rank(pct=True)  #rank based on percentage(PCT=True)
freq2['freq_rank'] = freq2['Frequency'].rank(ascending=False,pct=True) 
money2['monet_rank'] = money2['monetary_average'].rank(ascending=False,pct=True)
#join 
all_data = pd.merge(customers_recency,freq2, how='left', on='Customer ID')
all_data = pd.merge(all_data, money2, how='left', on='Customer ID')
# group customers based on percentage
bins = [0,0.5,1] #segment rank percentage
names = ['1','2'] # ranking customers, 1:first group, 2:second group, 3:third group

final = pd.DataFrame(customers_recency['Customer ID'])
# assign categories for three measurement for each customer
final['frequency'] = pd.cut(freq2['freq_rank'], bins, labels=names).astype('string')
final['recency'] = pd.cut(customers_recency['rank_recency'], bins, labels=names).astype('string')
final['monetary_value'] = pd.cut(money2['monet_rank'], bins, labels=names).astype('string')
# calculate the sum of category rank value
final['freq_rec_money'] = final['frequency'] + final['recency'] + final['monetary_value']

all_data['freq_rec_money'] = final['freq_rec_money']
# Visualization
import seaborn as sns
fig = sns.countplot(x='freq_rec_money',data=all_data)
fig.set_xticklabels(fig.get_xticklabels(),rotation=45) #rotation 45 degree for x-labels


