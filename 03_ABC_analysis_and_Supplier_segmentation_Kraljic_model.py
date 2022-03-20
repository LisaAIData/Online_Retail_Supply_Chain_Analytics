#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 14:54:17 2022

@author: lisa_hu
"""

####———————————————— S9.132 Transforming the data for excel——————————————
# 配置环境
import pandas as pd
import numpy as np
import seaborn as sns
import inventorize as inv

retail = pd.read_csv('online_retail2.csv')
 
retail = retail.drop_duplicates()
retail = retail.dropna()
retail = retail[retail.Quantity>0]

 #创建新retail_clean文件csv格式，excel格式exl
retail_clean = retail.copy()
retail_clean['Revenue'] = retail['Price']*retail['Quantity']
retail_clean.to_csv('retail_clean.csv')

retail_clean.columns
# 新表grouped根据不同产品分类，并计算总销量和总营业额
grouped = retail_clean.groupby('Description'
                        ).agg(total_sales_quantity = ('Quantity', np.sum),
                              total_revenue = ('Revenue', np.sum)).reset_index()

# 保存表grouped                         
grouped.to_csv('lisa_for_abc.csv')

#####——————————————————————————135. ABC analysis ABC分类法————————————————————————————
grouped
# 只根据总销量分类的ABC三类产品
a = inv.ABC(grouped[['Description','total_sales_quantity']])
a
a.Category.value_counts()
'''
C    2881
B    1245
A    1157
Name: Category, dtype: int64
'''
# ABC三类产品的柱状图
sns.countplot(x='Category',data=a)
# ABC三类产品的总销量直方图
sns.barplot(x='Category',y='total_sales_quantity',data=a)

###——————————————————————136. Multi-Criteria ABC analysis———————————————
# 根据总销量和总营业额分类的ABC三类产品
b = inv.productmix(grouped['Description'], grouped['total_sales_quantity'], grouped['total_revenue'])
b.columns
b.product_mix.value_counts()
'''
C_C    2394  # 有2394个产品既是C类总销量，也是C类总营业额
A_A     775  # 有775个产品既是A类总销量，也是A类总营业额
B_B     632
C_B     413  # 有413个产品既是C类总销量，但是B类总营业额
B_C     325
A_B     317
B_A     288
C_A      74
A_C      65
'''
# 绘制柱状图
sns.countplot(x='product_mix', data=b)
sns.barplot(x='product_mix',y='sales',data=b) #根据销量的柱状图
sns.barplot(x='product_mix',y='revenue',data=b) #根据营业额的柱状图

### ——————————————————————137. Multi-Criteria ABC analysis with STORE and Department level ———————————————
retail_clean.groupby(['Country','Description']).agg(total_sales=('Quantity', np.sum),
                                                    total_revenue=('Revenue',np.sum)).reset_index()

  ## Manipulation of data to multi-criteria
# 表by_store根据国家和产品分类，计算总销量和总营业额
by_store = retail_clean.groupby(['Country','Description']).agg(total_sales=('Quantity', np.sum),
                                                    total_revenue=('Revenue',np.sum)).reset_index()
# 根据产品，国家，总销量，总营业额进行ABC产品分类
mix_storeincountries = inv.productmix_storelevel(by_store['Description'], 
                          by_store['total_sales'], 
                          by_store['total_revenue'], 
                          by_store['Country'])

mix_storeincountries.columns
# 以店铺来源国和产品ABC分类，计算不同国家店铺的ABC类产品数量
product_mix = mix_storeincountries.groupby(['storeofsku','product_mix']).count().reset_index().iloc[:,0:3]
# 例如，查看来自澳大利亚店铺的ABC产品分类
product_mix[product_mix.storeofsku == 'Australia']


### ——————————————————————138. Supplier segmentation 供应商区分———————————————
''' 
 在供应商区分中，采用供应链管理的卡拉杰克矩阵模型（Kraljic Matrix），将供应商分为四种类型，leverage, strategic, non-critical, bottleneck。

 cost/profit impact     leverage items       Strategic items
                        Non-critial items    Bottleneck items
                                 Risk/Complexity(numbers of suppliers)
'''

# Kraljic其中一个供应商评价维度是risk，即有危险和无危险。因此，假设supplier=0 意味low risk/low cost；supplier=0.5意味risky/high profit
import pandas as pd
import numpy as np
import seaborn as sns
import inventorize3 as inv
supplier = pd.read_csv('supplier_data.csv')
supplier.head()
supplier.columns

supplier['risk_index'] = supplier['availability'] + supplier['no_suppliers'] + supplier['standard'] + supplier['price_fluctuation']

supplier['value_index'] = supplier['price'] * supplier['Quantity']
supplier.value_index.describe()              
'''
count    2.400000e+01
mean     5.064812e+06
std      4.847504e+06
min      1.189500e+05
25%      7.975622e+05
50%      3.011452e+06
75%      8.499426e+06
max      1.399081e+07
Name: value_index, dtype: float64

可以看出50%（中位数）是在300000。 可定义低于300,000为low value, 高于300000是high value
'''

###  Visualizing Kraljic Matrix
def category(x,y):
    if ((x>=3000000) & (y>= 1)):
        return 'Strategic item'
    if ((x>=3000000) & (y<= 1)):
        return 'Bottleneck item'
    if ((x<=3000000) & (y>= 1)):
        return 'Leverage item'
    if ((x<=3000000) & (y<= 1)):
        return 'Non-critical item'

for i in range(supplier.shape[0]):
    supplier.loc[i,'category'] = category(supplier.loc[i,'value_index'], 
                                          supplier.loc[i,'risk_index'])

supplier.category.value_counts()
# 得出Kraljic的零售店供应商分类
sns.scatterplot(x = 'value_index', y='risk_index', data=supplier, hue='category')
