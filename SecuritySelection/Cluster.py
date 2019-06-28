#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 15:15:12 2019

@author: sylvieshi
"""

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.cluster.vq import kmeans,vq
from pylab import plot,show
from PreScreening import Filters 

################################### PRE-SCREENING ##################################################
investment_date = '2014-04-01'
lookback_start_date = '2008-04-01'
countries_to_keep = ['Canada', 'United States', 'Australia', 'Japan', 'China']
curr_to_keep = ['CAD', 'USD', 'EUR', 'JPY', 'AUD']


# don't run the code below if switch is off 
switch = 0
if switch == True: 
    EQUITIES = pd.read_csv(r"equity_all.csv", index_col=0, header=0,parse_dates=True, error_bad_lines=False, dtype='unicode')
    EQUITIES = EQUITIES.loc[:investment_date, :]
    eq_des = pd.read_csv(r"equity_description.csv", index_col=0, header=0, parse_dates=True)
    ETFS = pd.read_csv(r"etf_all.csv", index_col=0, header=0, parse_dates=True, error_bad_lines=False, dtype='float')
    ETFS = ETFS.loc[:investment_date, :]
    etf_des = pd.read_csv(r"etf_desc.csv", index_col=0, header=0, parse_dates=True)
    fx_rates = pd.read_csv(r"fx_factors.csv", index_col=0, header=0,parse_dates=True, error_bad_lines=False, dtype='float')
    fx_rates = fx_rates.loc[lookback_start_date:investment_date, :]
    fx_for_filtered_eq = pd.read_excel("fx_for_filtered_eq.xlsx", sheet_name='set1', index_col=0) # NEED TO MODIFY THIS FILE IF CHOOSE DIFFERENT COUNTRIES 
    
    # Get the full set of countries and a dictiionary of ticker to currency 
    curr_all = []
    tick_to_curr = {}
    
    country_data = eq_des['Country']
    tick_currency = eq_des['Currency']
    
    for i in range(len(tick_currency)):
        if tick_currency.iloc[i] not in curr_all:
            curr_all.append(tick_currency.iloc[i])
        tick_to_curr[tick_currency.index[i]] = tick_currency.iloc[i]
    
    equity_filter = Filters(EQUITIES, eq_des, investment_date, fx_rates)
    
    # filter the DataFrame 
    filtered_eq = equity_filter.delete_penny(tick_to_curr)
    filtered_eq = equity_filter.delete_high_vol() 
    
    curr_to_take_out = list(set(curr_all) - set(curr_to_keep))
    
    filtered_eq = equity_filter.delete_curr(curr_to_take_out)
    
    ############################ CLUSTERING ###################################################
    
    # Only use data back to 5 years for clustering due to the misssing data issue 
    eq_cluster = filtered_eq.loc[lookback_start_date:investment_date, :]
    
    # check missing data and separate the securities with missing data from the rest 
    eq_w_missing = []
    count_missing = eq_cluster.isna().sum()
    
    for j in range(len(count_missing)):
        if count_missing.iloc[j] != 0:
            eq_w_missing.append(count_missing.index[j])
    
    eq_cluster = eq_cluster.drop(eq_w_missing, axis=1)
    
    # Convert data to USD 
    tick_to_curr = equity_filter.trimmed_dict(tick_to_curr)

###########################################################################
#def Normalize(price_mtx):
#    '''
#    normalized the prices (in USD)
#    '''

final_df = pd.read_csv(r"filtered_eq.csv", index_col=0, header=0,parse_dates=True, error_bad_lines=False, dtype='float')
# Try naive K-means first (k = 10)
# Elbow Curve 
returns = final_df.pct_change().mean() * 252
returns = pd.DataFrame(returns)
returns.columns = ['Returns']
returns['Volatility'] = final_df.pct_change().std() * np.sqrt(252)
#format the data as a numpy array to feed into the K-Means algorithm
data = np.asarray([np.asarray(returns['Returns']),np.asarray(returns['Volatility'])]).T
X = data
distorsions = []
for k in range(2, 20):
    k_means = KMeans(n_clusters=k)
    k_means.fit(X)
    distorsions.append(k_means.inertia_)
fig = plt.figure(figsize=(15, 5))
plt.plot(range(2, 20), distorsions)
plt.grid(True)
plt.title('Elbow curve')

k = 10
centroids,_ = kmeans(data,k)
# assign each sample to a cluster
idx,_ = vq(data,centroids)
# some plotting using numpy's logical indexing
plot(data[idx==0,0],data[idx==0,1],'ob',
     data[idx==1,0],data[idx==1,1],'oy',
     data[idx==2,0],data[idx==2,1],'or',
     data[idx==3,0],data[idx==3,1],'og',
     data[idx==4,0],data[idx==4,1],'om')
plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
show()


### Check for outliers 
print(returns.idxmax())
returns.drop(['RTL', 'CEZ', 'AC', 'MGNK.DE', 'CRIN.F'], inplace=True)
data = np.asarray([np.asarray(returns['Returns']),np.asarray(returns['Volatility'])]).T
centroids,_ = kmeans(data,k)
# assign each sample to a cluster
idx,_ = vq(data,centroids)
# some plotting using numpy's logical indexing
plot(data[idx==0,0],data[idx==0,1],'ob',
     data[idx==1,0],data[idx==1,1],'oy',
     data[idx==2,0],data[idx==2,1],'or',
     data[idx==3,0],data[idx==3,1],'og',
     data[idx==4,0],data[idx==4,1],'om')
plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
show()

details = [(name,cluster) for name, cluster in zip(returns.index,idx)]
for detail in details:
    print(detail)

TEST_EQUITY = pd.concat([final_df['MRD.TO'], final_df['CIM.AX'], final_df['GAPSX'], final_df['LNC'], final_df['KNEBV.HE']], axis=1)
# correlation matrix 

plt.matshow(TEST_EQUITY.corr())
plt.show()






