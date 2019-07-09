
# coding: utf-8

from Portfolio import Portfolio, universe # universe is a global variable
# and each portfolio can access to the universe
from Admin import Admin, MeanReturn, MoneyWeightedReturn,SimpleReturn,TimeWeightedReturn,Volatility,ReturnAttribCurrency
import pandas as pd
# In[5]:

test_admin=Admin()
test_admin.suggestPortfolio('1','2014-04-01')


# In[6]:

test_admin.acceptPortfolio(0)


# In[7]:


test_admin.getAccountValue('2014-04-01')


# In[8]:


test_admin.trackPortfolio(rebalance_flag=True,rebalance_freq='3MS',rebal_start_date='2014-09-01')


# In[24]:


test_admin.portfolio


# In[13]:
last_report = '2019-02-28'
from datetime import datetime,timedelta
date_format='%Y-%m-%d'
last_quarter = [datetime.strftime(item,date_format) for item in pd.date_range(last_report,test_admin.today,freq='B')]


# In[73]:
last_quarter

# In[75]:
#port_values=[]
#for item in last_quarter:
#    port_values.append(test_admin.getAccountValue(item))
#   
#from matplotlib import pyplot as plt
#plt.figure(figsize=(100,15))
#plt.plot(last_quarter,port_values)


report_date = [datetime.strftime(item,date_format) for item in pd.date_range(end=test_admin.today,periods=21,freq='3MS')]
#pandas.date_range(end='2/08/2014', periods=104, freq='W-Sat')[::-1]

today_date = test_admin.today
# In[20]:
pnl_period = [datetime.strftime(item,date_format) for item in pd.date_range('2014-04-02','2019-06-01',freq='B')]
import numpy as np
import pandas as pd
port_val=[]
for item in pnl_period:
    port_val.append(test_admin.getAccountValue(item))
y = np.diff(port_val, n=1, axis=0)
x = pnl_period[1:]
y = pd.DataFrame(data=y,index=pnl_period[1:],columns=['pnl'])

# In[21]:
test_dates = [datetime.strftime(item,date_format) for item in pd.date_range('2009-06-02',today_date,freq='B')]
# In[22]:
test_dates

def PortfolioVaR(account,fit_start_date,fit_end_date,annualize):
    import numpy as np
    import scipy as sp
    model1={}
    for item in account.PortfolioWeights.keys():
        model1[item]=universe.fitFactorModel(item,fit_start_date,252*5).params
    
    factor_cov=universe.get_risk_factors_cov(fit_start_date,252*5,freq='B',annualize=False)
    betas=pd.DataFrame(index=list(model1.keys()),columns=factor_cov.index)
    for item in model1.keys():
        betas.loc[item,:]=model1[item].reindex(factor_cov.index,fill_value=0)
    sec_cov=pd.DataFrame(np.dot(betas,np.dot(factor_cov,betas.transpose())),index=list(model1.keys()),columns=list(model1.keys()))
    weights=[np.float(item) for item in list(account.PortfolioWeights.values())]
#     factors_mean=universe.get_risk_factors_mean(start_date,252*5,freq='B')
    portf_vol=np.sqrt(np.dot(weights,np.dot(sec_cov,weights)))
#     portf_mean=np.dot(weights,np.dot(betas,factors_mean))
    portf_VaR=np.float(sp.stats.norm.ppf(0.95)*portf_vol*account.getAccountValue(fit_end_date))
    return betas,portf_VaR

def backtest_Var(account,test_dates):
    Var = pd.DataFrame(columns=['VaR'],index=test_dates)
    for i in range(1, len(test_dates)-5*252):
        fit_begin = test_dates[-i-5*252] # -len(test_dates) 
        fit_end = test_dates[-i]
        beta, Var.loc[fit_end] = PortfolioVaR(account,fit_begin,fit_end,False)
        #print("fit begins at:" + fit_begin + fit_end + "is" + str(Var.loc[fit_end]))
    return Var
# In[ ]:
b_Var = backtest_Var(test_admin,test_dates)
#VaR = pd.DataFrame(columns='VaR', index = Var.keys())
#for key in Var.keys():
#    VaR.loc[key] = - Var[key]
#    print(VaR.loc[key])


# In[ ]:
if __name__ == '__main__': 
    import matplotlib.pyplot as plt
    #beta, VaR = PortfolioVaR(test_admin,all_dates[0],test_admin.today)
#    plt.figure(figsize=(45,25))
#    #VaR = pd.DataFrame(columns='VaR', index = Var.keys())
#    #for key in Var.keys():
#    #    VaR.loc[key] = - Var[key]
#    plt.plot(y.index,b_Var)
#    plt.plot(y.index, y)
#    plt.title("Backtesting VaR (95%) for the total investment horizon", fontsize=40)
#    plt.xlabel("Date for the total investment horizon", fontsize=20)
#    plt.ylabel("Portfolio daily P&L", fontsize=20)
#    plt.tick_params(labelsize=30)
#    plt.xticks(x, rotation='vertical')
#    plt.show()
    #%% 
    plt.figure(figsize=(45,25))
    VaR = pd.DataFrame(columns='VaR', index = Var.keys())
    for key in Var.keys():
        VaR.loc[key] = - Var[key]
        
    plt.plot(y.index,b_Var.loc['2019-02-28':'2019-05-31'])
    plt.plot(y.index, y.loc['2019-03-01':'2019-06-01'])
    plt.title("Backtesting VaR (95%) for the past quarter as of June 1st 2019", fontsize=40)
    plt.xlabel("Date for the Last Quarter", fontsize=20)
    plt.ylabel("Portfolio daily P&L", fontsize=20)
    plt.tick_params(labelsize=30)
    plt.xticks(x, rotation='vertical')
    plt.show()
    
    #%% 
    #VaR backtesting for the past one-year
    plt.figure(figsize=(45,25))
        
    plt.plot(y.index,b_Var.loc['2018-05-31':'2019-05-31'])
    plt.plot(y.index, y.loc['2018-06-01':'2019-06-01'])
    plt.title("Backtesting 1-year VaR (95%) as of June 1st 2019", fontsize=40)
    plt.xlabel("Date for the Last 1 year", fontsize=20)
    plt.ylabel("Portfolio daily P&L", fontsize=20)
    plt.tick_params(labelsize=30)
    plt.xticks(x, rotation='vertical')
    plt.show()
    
#
## In[255]:
#
#
##x = last_quarter[1:]
##y = port_ret
#plt.figure(figsize=(45,25))
##dailyPnL =
#
#ret = pd.DataFrame(columns=['PnL'],index=pnl_period)
#for i in range(0,len(pnl_period)):
#    curr = test_admin.getAccountValue(pnl_period[i])
#    print(curr)
#    prev = test_admin.getAccountValue(pnl_period[i-1])
#    print(prev)
#    ret.loc[pnl_period[i]] = curr - prev    
#    print(ret.loc[pnl_period[i]])
#    
##port_val=[]
##for item in pnl_period:
##    port_val.append(test_admin.getAccountValue(item))
##y = np.diff(port_val, n=1, axis=0)
#x = all_dates[1:]
#
#from Admin import PortfolioVaR
#beta, VaR = PortfolioVaR(test_admin,all_dates[0],test_admin.today)
#plt.plot(Var.keys(),Var.values())
#plt.plot(x,y)
#plt.title("Backtesting 3-month VaR (95%) as of June 1st, 2019", fontsize=40)
#plt.xlabel("Date for the Last Quarter", fontsize=20)
#plt.ylabel("Portfolio daily P&L", fontsize=20)
#plt.tick_params(labelsize=30)
#plt.xticks(x, rotation='vertical')
#plt.show()
#
#
## In[137]:
#
#
#def backtest_port(test_admin, time_period, alpha):
#    port_val=[]
#    for item in time_period:
#        port_val.append(test_admin.getAccountValue(item))
#    y = np.diff(port_val, n=1, axis=0)
#    x = time_period[1:]
#    beta, VaR = PortfolioVaR(test_admin,time_period[0],test_admin.today,alpha)
#    plt.figure(figsize=(45,25))
#    plt.plot(x,y)
#    plt.axhline(y=-VaR, color='r', linestyle='-')
#    plt.title("Backtesting 1 year VaR (95%) as of June 1st, 2019", fontsize=40)
#    plt.xlabel("Date for the Last Quarter", fontsize=20)
#    plt.ylabel("Portfolio daily P&L", fontsize=20)
#    plt.xticks(x, rotation='vertical')
#    plt.tick_params(labelsize=30)
#    plt.show()
#
#
## In[138]:
#
#
#backtest_port(test_admin,all_dates,0.95)
#
#
## In[ ]:
#
#
#x2 = all_dates
#y2 = port_ret
#plt.figure(figsize=(45,25))
#plt.plot(x,y)
#plt.axhline(y=-9578.478, color='r', linestyle='-')
#plt.title("Backtesting 3-month VaR (95%) as of June 1st, 2019", fontsize=40)
#plt.xlabel("Date for the Last Quarter", fontsize=20)
#plt.ylabel("Portfolio daily P&L", fontsize=20)
#plt.tick_params(labelsize=30)
#plt.xticks(x, rotation='vertical')
#plt.show()
#
#
## In[90]:
##PortfolioVaR(test_admin,start_date,today_date)
#from Admin import PortfolioVaR
#betas,VAR_test=PortfolioVaR(test_admin,start_date,test_admin.today)
#
## In[164]:
#
#def PortfolioVaR(account,fit_start_date,fit_end_date,annualize=False,alpha=0.95):
#    import numpy as np
#    import scipy as sp
#    model1={}
#    for item in account.PortfolioWeights.keys():
#        model1[item]=universe.fitFactorModel(item,fit_start_date,252*5).params
#    
#    factor_cov=universe.get_risk_factors_cov(fit_start_date,252*5,freq='B',annualize=False)
#    betas=pd.DataFrame(index=list(model1.keys()),columns=factor_cov.index)
#    for item in model1.keys():
#        betas.loc[item,:]=model1[item].reindex(factor_cov.index,fill_value=0)
#    sec_cov=pd.DataFrame(np.dot(betas,np.dot(factor_cov,betas.transpose())),index=list(model1.keys()),columns=list(model1.keys()))
#    weights=[np.float(item) for item in list(account.PortfolioWeights.values())]
##     factors_mean=universe.get_risk_factors_mean(start_date,252*5,freq='B')
#    portf_vol=np.sqrt(np.dot(weights,np.dot(sec_cov,weights)))
##     portf_mean=np.dot(weights,np.dot(betas,factors_mean))
#    portf_VaR=np.float(sp.stats.norm.ppf(alpha)*portf_vol*account.getAccountValue(fit_end_date))
#    return betas,portf_VaR
#
#
#
## In[1]:
#def SharpeRatio(portfolio,d1,d2,annualize=True):
#    """excess return over std
#       Think: the risk-free rate for the portfolio
#       CAD rf or the maximum of rf available?
#       assume portfolio return in CAD"""
#    rf = MeanReturn(universe.CAD_rf.loc[d1:d2],d1,d2)
#    return (MeanReturn(portfolio,d1,d2) - rf) / np.sqrt(Volatility(portfolio,d1,d2))
#    
#def Sortino(portfolio,d1,d2,annualize=True):
#    """dss: downside standard deviation
#    assume a target return at 5%"""
#    target_ret = 0.05
#    all_dates=[datetime.strftime(item,date_format) for item in pd.date_range(d1,d2,freq='D')]
#    dss = np.sqrt(min(0,))
#    (MeanReturn(portfolio,d1,d2) - target_ret) / dss
#    

