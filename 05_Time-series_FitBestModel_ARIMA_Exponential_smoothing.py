#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 21:04:55 2022

@author: lisahu
"""

#——————— 164.Preparing data for Time-Series —————————
import warnings
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

time_series = pd.read_csv('timeseries_rev.csv', parse_dates=True)

# set date as index
time_series.info()
time_series['date'] = pd.to_datetime(time_series['date'])
time_series = time_series.set_index('date')

monthly_series = time_series.total_revenue.resample('M').sum()
monthly_series.plot()

#—————166. Get Time-Series Components——————
components = sm.tsa.seasonal_decompose(monthly_series)
components.plot()
# 定义trend, seasonality
trend = components.trend
seasonality = components.seasonal
remainder = components.resid

#——————169. Arima Model: Check stationarity —————
# 平稳性检测方法一：时序图
## 创建平均标准差和实际值图，通过图形查看稳定性
monthly_series.plot()
monthly_series.rolling(window=12).mean().plot() #12个月平均值图
monthly_series.rolling(window=12).std().plot() #12个月标准差图
# 获得P值，检测稳定性
ad_fuller_test = sm.tsa.stattools.adfuller(monthly_series, autolag='AIC')
ad_fuller_test
'''
Out[11]: 
(-3.6538709279975996,  
 0.004810825530872371,  #--> P值为0.0048，小于1%， 表示此模型稳定性高
 9,
 15,
 {'1%': -3.9644434814814815,
  '5%': -3.0849081481481484,
  '10%': -2.6818144444444445},
 418.7649518406608)
'''
#——————170.Arima in Python——————
# 平稳性检测方法二：相关图
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# 绘制Autucorrelation 自相关图图形
plot_acf(monthly_series)
# 绘制partical correlations 偏相关图
plot_pacf(monthly_series, lags=11)

# 比较4个模型AIC值，取AIC最小值的模型
# 1、MA模型
model_ma = sm.tsa.statespace.SARIMAX(monthly_series, order=(0,0,1))
results_ma = model_ma.fit()
results_ma.aic #结果AIC：735.7906414433098

# 2、AR模型
model_ar = sm.tsa.statespace.SARIMAX(monthly_series, order=(1,0,0))
results_ar = model_ar.fit()
results_ar.aic  #结果AIC：703.4620739015523

# 3、ARMA模型
model_arma = sm.tsa.statespace.SARIMAX(monthly_series, order=(1,0,1))
results_arma = model_arma.fit()
results_arma.aic  #结果AIC：702.16039524085

# 4、ARIMA模型
model_arima = sm.tsa.statespace.SARIMAX(monthly_series, order=(1,1,1))
results_arima = model_arima.fit()
results_arima.aic  #结果AIC：672.0261771707899
#比较上述4个AIC值，可知ARIMA模型的值最小，因此采用ARIMA模型
results_arima.plot_diagnostics(figsize=(15,12))
'''
- 在Standardized residual图中，理想是围绕0轴波动。
- Histogram plus estimated density图中，理想是hist直方图与线型图相差较小
- Q-Q图中，理想是点与线共线
- Correlogram图中，理想是值在置信区间内波动
从该图结论中，可看出即使采用ARIMA模型，结果仍有较大偏差。在下一部分将进一步优化最优模型
'''

#——————172. Grid search——————
import itertools
P=D=Q=p=d=q= range(0,3)
S=12
# 得出pdqPDQ所有组合
combinations = list(itertools.product(p,d,q,P,D,Q))
# 得出对应的arima orders， 对应combination的p,d,q组合值
arima_order = [(x[0],x[1],x[2]) for x in combinations]
# 得出seasonal orders, 对应combination的P，D, Q组合值
seasonal_order = [(x[3],x[4],x[5],S) for x in combinations]

#————173. For looping ARIMA——————
# 使用for循环，匹配arima order, seasonal order, 和所有组合combination。寻找出最优模型对应的组合结果
results_data = pd.DataFrame(columns=['p','d','q','P','D','Q','AIC'])
# length of combinations
len(combinations) # 有729长度的组合
for i in range(len(combinations)):
    try:  #也许有些部分数据确实，所以建议使用try，测试error
        model = sm.tsa.statespace.SARIMAX(monthly_series, order=arima_order[i]
                                      , seasonal_order=seasonal_order[i])
        result = model.fit()
        results_data.loc[i,'p'] = arima_order[i][0] 
        results_data.loc[i,'d'] = arima_order[i][1]
        results_data.loc[i,'q'] = arima_order[i][2]
        results_data.loc[i,'P'] = seasonal_order[i][0]
        results_data.loc[i,'D'] = seasonal_order[i][1]
        results_data.loc[i,'Q'] = seasonal_order[i][2]
        results_data.loc[i,'AIC'] = result.aic
    except:
        continue

results_data[results_data.AIC == min(results_data.AIC)]
# 得出最小AIC对应的组合
'''
     p  d  q  P  D  Q  AIC
87   0  1  0  0  2  0  2.0
168  0  2  0  0  2  0  2.0
有两种组合形式
'''
best_model = sm.tsa.statespace.SARIMAX(monthly_series, order=(0,1,0),
                                       seasonal_order=(0,2,0,12))
# Fitting the best model
results = best_model.fit()
monthly_series
fiting = results.get_prediction(start = '2009-12-31')
fiting_mean = fiting.predicted_mean # 生成往期自2009年每月的实际值
forecast = results.get_forecast(steps=12) #预测后12个月的值
forecast_mean = forecast.predicted_mean #生成平均预测值

# 下面两行同时运行，生成初始两条线型图
fiting_mean.plot(label='Fitting') #平均预测的以往值
monthly_series.plot(label = 'Actual') # 实际值
forecast_mean.plot(label = 'Forecast') #平均预测未来值
plt.legend(loc='upper left')

# Measure accuracy 测量精准度
mean_absolute_error = abs(monthly_series - fitting_mean).mean()
#——————177. ARIMA比较——————
model_arima = sm.tsa.statespace.SARIMAX(monthly_series, order=(1,1,1))
results_arima = model_arima.fit()
results_arima.aic  #结果AIC：672.0261771707899

fitting = results_arima.get_prediction(start='2009-12-31')
fitting_arima = fitting.predicted_mean

mae_arima= abs(monthly_series - fitting_arima).mean()  # 211749.27702660885
rmse_arima= np.sqrt((monthly_series - fitting_arima)**2).mean()

#——————178. Single Exponential Smoothing——————
# HOLT method
# Holt-Winter's additive method

#————179. Exponential smoothing in python—————
import statsmodels as sm
sm.tsa.holtwinters.ExponentialSmoothing

model_expo1 = sm.tsa.holtwinters.ExponentialSmoothing(monthly_series, trend='add', seasonal='add'
                                                      , seasonal_periods=12)
model_expo2 = sm.tsa.holtwinters.ExponentialSmoothing(monthly_series, trend='mul', seasonal='add'
                                                      , seasonal_periods=12)
model_expo3 = sm.tsa.holtwinters.ExponentialSmoothing(monthly_series, trend='add', seasonal='mul'
                                                      , seasonal_periods=12)
model_expo4 = sm.tsa.holtwinters.ExponentialSmoothing(monthly_series, trend='mul', seasonal='mul'
                                                      , seasonal_periods=12)
results_1 = model_expo1.fit()
results_2 = model_expo2.fit()
results_3 = model_expo3.fit()
results_4 = model_expo4.fit()
# 通过summary表，可查询优化结果
results_1.summary()
results_2.summary()
results_3.summary()
results_4.summary()

#————180. Comparing exponential smoothing models—————
# 比较上面四个results，找出最小的MA值
fit1 = model_expo1.fit().predict(0,len(monthly_series))
fit2 = model_expo2.fit().predict(0,len(monthly_series))
fit3 = model_expo3.fit().predict(0,len(monthly_series))
fit4 = model_expo4.fit().predict(0,len(monthly_series))

mae1 = abs(monthly_series - fit1).mean() #75981.76746969954
mae2 = abs(monthly_series - fit2).mean() #73725.45030311609
mae3 = abs(monthly_series - fit3).mean() #78956.68397137325
mae4 = abs(monthly_series - fit4).mean() #75808.64751879484
#mae2最小，所以根据model2进行预测
forecast = model_expo2.fit().predict(0,len(monthly_series)+12)
# 绘制实际预测图
monthly_series.plot(label='Actual')
forecast.plot(label='Forecast')
plt.legend(loc='upper left')
# 相比之前的初始预测图，此修正过的图形更精准匹配实际量

