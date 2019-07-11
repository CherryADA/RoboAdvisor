# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 23:06:38 2019

@author: jkhai
"""
from Portfolio import Portfolio, universe
import pandas as pd
import numpy as np
import numpy.linalg as la
from Admin import PortfolioVaR,PortfolioVaRV2
from matplotlib import pyplot as plt
from datetime import datetime

def get_scenario_defining_returns(crisis_mid_point):
    markets=['Mkt-RF_log','Mkt-RF_log_global','Mkt-RF_log_EUR','Mkt-RF_log_JPY']
    markets_in_crisis=pd.DataFrame(index=list(universe.get_risk_factors()['Mkt-RF_log'].price.loc[:crisis_mid_point].iloc[-250:].index)+list(universe.get_risk_factors()['Mkt-RF_log'].price.loc[crisis_mid_point:].iloc[1:251].index),columns=markets)
    for item in markets_in_crisis.columns:
        markets_in_crisis.loc[:,item]=universe.get_risk_factors()[item].price.reindex(list(markets_in_crisis.index.values),method='ffill')
    markets_in_crisis=markets_in_crisis.dropna(axis=1)
    markets_in_crisis_monthly=markets_in_crisis.cumsum().iloc[::20,:]
    markets_in_crisis_monthly=markets_in_crisis_monthly.diff().dropna()
    return markets_in_crisis_monthly

def cond_means_of_factors(cond_values_df,factor_cov):
    #split factor cov in two, X_cov=all non-cond, Y_cov=all cond
    #assume factors all have mean return of 0
    Y_names=list(cond_values_df.columns)
    X_names=list(set(factor_cov.columns)-set(Y_names))
    factor_cov=factor_cov.reindex(index=X_names+Y_names,columns=X_names+Y_names)
    X_cov=factor_cov.loc[X_names,X_names]
    Y_cov=factor_cov.loc[Y_names,Y_names]
    XY_cov=factor_cov.loc[X_names,Y_names]
    YX_cov=factor_cov.loc[Y_names,X_names]
    Y_cov_inv=la.inv(Y_cov)
    cond_means_x=np.dot(np.matmul(XY_cov,Y_cov_inv),cond_values_df.transpose()).transpose()
    cond_means=pd.DataFrame(np.concatenate((cond_means_x,np.array(cond_values_df)),axis=1), index=list(range(0,24)),columns=X_names+Y_names)
    return cond_means

def run_scenario(account,scenario_num,today_date='2019-06-01'):
    financial_crisis_midpoint=np.cumsum(universe.get_risk_factors()['Mkt-RF_log'].price['2007-06-01':'2010-01-01'])[np.cumsum(universe.get_risk_factors()['Mkt-RF_log'].price['2007-06-01':'2010-01-01'])==np.cumsum(universe.get_risk_factors()['Mkt-RF_log'].price['2007-06-01':'2010-01-01']).min()].index[0]
    asian_crisis_midpoint=np.cumsum(universe.get_risk_factors()['Mkt-RF_log'].price['2000-06-01':'2004-01-01'])[np.cumsum(universe.get_risk_factors()['Mkt-RF_log'].price['2000-06-01':'2004-01-01'])==np.cumsum(universe.get_risk_factors()['Mkt-RF_log'].price['2000-06-01':'2004-01-01']).min()].index[0]
    if scenario_num==0:
        crisis_midpoint=asian_crisis_midpoint
    elif scenario_num==1:
        crisis_midpoint=financial_crisis_midpoint
    else:
        print("ERROR: No scenario found. Please choose one of: 0, 1")
        return
    factors_cov=universe.get_risk_factors_cov('2014-04-01',252*5,annualize=False)
    scenario_def=get_scenario_defining_returns(crisis_midpoint)
    cond_means=cond_means_of_factors(scenario_def,factors_cov)
    betas,var_tmp=PortfolioVaRV2(account,'2014-04-01',today_date,False)
    reinexed_betas=betas.reindex(columns=cond_means.columns,fill_value=0)
    sec_returns_in_crisis=pd.DataFrame(np.matmul(np.array(reinexed_betas).astype(float),np.array(cond_means).transpose().astype(float)),
                                  index=reinexed_betas.index,columns=cond_means.index)
    prices_today=[]
    for item in sec_returns_in_crisis.index:
        prices_today.append(universe.get_security(item).price[datetime.strftime(pd.date_range(end=today_date,periods=1,freq='B')[0],'%Y-%m-%d')])
    # prices_today
    amounts_today=[np.float(list(account.portfolio[today_date].portfolio.values())[i]) for i in range(0,len(prices_today))]
    cum_returns_in_crisis=sec_returns_in_crisis.add(1).cumprod(axis=1).subtract(1)
    cum_pnl_in_crisis=cum_returns_in_crisis.multiply(prices_today,axis=0).multiply(amounts_today,axis=0)
    port_cum_pnl_if_crisis_repeats_now=cum_pnl_in_crisis.sum().add(np.float(account.getAccountValue(today_date)))
    #plt.figure()
    #plt.plot(cum_pnl_in_crisis.sum().add(np.float(account.getAccountValue(today_date))))
    #plt.figure()
    #for item in cum_pnl_in_crisis.index:
    #    plt.plot(cum_pnl_in_crisis.loc[item])
    #plt.legend(cum_pnl_in_crisis.index)
    return cum_pnl_in_crisis, port_cum_pnl_if_crisis_repeats_now
