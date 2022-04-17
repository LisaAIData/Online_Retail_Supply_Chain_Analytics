#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 19:17:13 2022

@author: lisahu
"""
#——————Queue Theory 排队论——————
import numpy as np
lambda1 = 1 # 假设每时段平均到达量 average arrival rate 是 1
mean_service = 1 # 假设每时段平均客户服务量(e.g.mean service rate) 是 1
sd=0.2 # 假设标准差为20%
# 设400名顾客的随机到达时间
arrival_time = np.random.exponential(1, 400).cumsum()
# 设服务时间是平均值为1，标准差为0.2，样本量为400的正态分布
service_time = np.random.normal(1,0.2,400)

def waiting_mean(arrival_time, service_time):
    waiting_time=[]
    leaving_time=[]
    
    waiting_time.append(0) #第一个客户的等待时间为0
    leaving_time.append(arrival_time[0]+service_time[0]+waiting_time[0]) #第一个客户离开时间
    
    for i in range(1,len(arrival_time)):
        waiting_time.append(max(0,leaving_time[i-1]-arrival_time[i]))
        leaving_time.append(arrival_time[i]+service_time[i]+waiting_time[i])
        
    mean_waiting = np.mean(waiting_time)
    return mean_waiting

waiting_mean(arrival_time, service_time)
    
average_Sim = []
for i in range(0,1000):
    # 设400名顾客的随机到达时间
    arrival_time = np.random.exponential(1, 400).cumsum()
    # 设服务时间是平均值为1，标准差为0.2，样本量为400的正态分布
    service_time = np.random.normal(1,0.2,400)
    waiting_time = waiting_mean(arrival_time, service_time)
    average_Sim.append(waiting_time)

np.mean(average_Sim)
np.median(average_Sim)
import matplotlib.pyplot as plt
plt.hist(average_Sim)

# 调用R语言
from rpy2.robjects import r ,pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects import FloatVector
import numpy as np
pandas2ri.activate()
importr('queuecomputer')

## queue_step(arrival_time, service_time, number_of_servers)

# 设400名顾客的随机到达时间
arrival_time = np.random.exponential(1, 400).cumsum()
# 设服务时间是平均值为1，标准差为0.2，样本量为400的正态分布
service_time = np.random.normal(1,0.2,400)
r_arrival = FloatVector(arrival_time)
r_service_time = FloatVector(service_time)

simulation = r['queue_step'](r_arrival, r_service_time, 1)

simulation[0]
simulation[1]
simulation[2]  # 总表arrivals   service  departures   waiting  system_time  server
simulation[3] # queuelength

mean_waiting_time = simulation[2]['waiting'].mean() # 6.1659260439566355

average_sim_r=[]
for i in range(0, 1000):
    # 设400名顾客的随机到达时间
    arrival_time = np.random.exponential(1, 400).cumsum()
    # 设服务时间是平均值为1，标准差为0.2，样本量为400的正态分布
    service_time = np.random.normal(1,0.2,400)
    r_arrival = FloatVector(arrival_time)
    r_service_time = FloatVector(service_time)
    simulation = r['queue_step'](r_arrival, r_service_time, 1)
    average_sim_r.append(simulation[2]['waiting'].mean())

import seaborn as sns
sns.distplot(average_sim_r)

#——————211.Multiple resources——————
'''
Case 2 案例描述:
You are the operation manager at a call center, you have been assigned the task of determing
how many call center rep you will need on an hourly basis, you checked the incoming call
of customers one day and you have determined that you receive around 40 calls per hour,
and a call takes around 7 minuts.
 - How many call center reps you shouls have to have a waiting time no more than 5 minutes?
 - that the arrival is exponential so as the service time.   
    
'''
import os
os.environ['R_HOME'] = '/Library/Frameworks/R.framework/Resources' #配置r_home环境变量
import numpy as np
import random
import seaborn as sns
from rpy2.robjects import R ,pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects import FloatVector
pandas2ri.activate()
importr('queuecomputer')


#电话的平均到达量mean arrival rate
rate = 40/60
arrival_time = np.cumsum([random.expovariate(rate) for x in range(1000)]) #1000个顾客的累加随机到达时间
inter_arrival_time = [random.expovariate(rate) for x in range(1000)] # 每顾客自己随机到达时间
sns.distplot(inter_arrival_time)

service_time = np.random.exponential(7, 1000) #随机生成1000次的服务时间
sns.distplot(service_time)

r_arrival = FloatVector(arrival_time)
r_service = FloatVector(service_time)

simulation = r['queue_step'](r_arrival, r_service, 5) # 模拟有5个servers的排队论结论
simulation[2]['waiting'].mean()

#——————Getting the optimum number of servers————
n_servers = range(1,9)
waiting_list=[]
for k in n_servers:
    simulation = r['queue_step'](r_arrival, r_service, k) # 模拟有i个servers的排队论结论
    waiting_time = simulation[2]['waiting'].mean()
    waiting_list.append(waiting_time)

import matplotlib.pyplot as plt
plt.plot(n_servers, waiting_list)
list(zip(n_servers, waiting_list))
'''
[(1, 2783.474310232838),
 (2, 1028.2855178965167),
 (3, 444.9739667142448),
 (4, 155.09774590493234),
 (5, 26.075738438112733),
 (6, 2.563681971728802),  #当6名servers时，waiitng_time小于5分钟
 (7, 0.8055791600115858),
 (8, 0.2519701163165346)]
所以，雇佣 6名servers
'''
#————213.Capacity constrains————
'''
As bank operation manager, you would like to know how many tellers you need if your bank
is visited by around 150 customers per hour and the average serving time is exponentially
distributed we a Mu of 15 minutes. The capacity of the bank is only 55 customers inside 
the bank. M,M,K,55,inf, you want the maximum waiting time to be 10 min per customer.
'''
import numpy as np
import random
import seaborn as sns
from rpy2.robjects import R ,pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects import FloatVector
pandas2ri.activate()
importr('queuecomputer')

arrival_Rate = 150/60
service_mean = 15

arrival_time = np.cumsum([random.expovariate(arrival_Rate) for x in range(2000)])
service_time = np.random.exponential(15, 2000)
r_arrival = FloatVector(arrival_time)
r_service_time = FloatVector(service_time)

simulation = r['queue_step'](r_arrival, r_service_time, 39) # 39名服务员
simulation[2]['waiting'].mean() # 5.369086306125274
simulation[3]['queuelength'].max() # 59

#———— 215. Multiple service with queue computer————
'''
At the same bank, the bank has two services, the teller service and the customer service.
Customers come the bank to register for either a teller or a customer service support. You
have found out a customer takes around 30 seconds to register and 65% of them go to the 
tellers while 35% of them go to customer service support. Customers still arrive at an
exponential rate of 150 per hour, the teller service takes 10 min with a stadard devistion 
of 2 while the customer service takes an exponential rate of 13 minutes. What is the mean
waiting time of the system if you have 20 tellers and 25 customer service specialists.
'''
arrival_registration = np.cumsum([random.expovariate(150/60) for x in range(5000)])
service_registration = np.random.exponential(0.5, 5000)

sns.distplot(service_registration)
# 转换数据格式
rarrival_reg = FloatVector(arrival_registration)
rservice_reg = FloatVector(service_registration)
simulation_reg = r['queue_step'](rarrival_reg, rservice_reg, 2) #2 registrations
simulation_reg[2]['waiting'].mean() # 0.2817220053870326
# 随机生成65%和35%的departure
randomization = np.random.random(5000)
departures = simulation_reg[2]['departures']
# 设置2种departure客流量比例
teller_arrival = departures[randomization <= 0.65] #65%客户会到teller柜台
cs_arrival = departures[randomization > 0.35] #35%客户回到customer service support柜台
#teller柜台正态分布，平均服务10分钟，标准差2，客户量为teller_arrival到达的数量（长度）
teller_service = np.random.normal(10, 2, len(teller_arrival)) 
#customer service support 柜台指数平滑分布，平均服务13分钟，客户量为cs_arrival到达的数量（长度）
cs_service = np.random.exponential(13, len(cs_arrival))
# 转换数据类型为R可用的
rteller_arrival = FloatVector(teller_arrival)
rcs_arrival = FloatVector(cs_arrival)
rteller_service = FloatVector(teller_service)
rcs_service = FloatVector(cs_service)
# ✨构建模拟
sim_teller = r['queue_step'](rteller_arrival, rteller_service, 20) #20名teller柜台专员
sim_cs = r['queue_step'](rcs_arrival, rcs_service, 25) #25名customer support柜台专员
# 得出总 mean waiting time
waiting_reg = simulation_reg[2]['waiting'].mean()
waiting_teller = sim_teller[2]['waiting'].mean()
waiting_cs = sim_cs[2]['waiting'].mean()
# 最后得出总平均等待时长，为registration柜台平均时长+ teller和cs柜台的平均时长
total_waiting_mean = waiting_reg + ((waiting_teller + waiting_cs)/2)
# 1.117932610926708，这种waiting mean需要在✨构建模拟时，不断调试分配的专员数量。



