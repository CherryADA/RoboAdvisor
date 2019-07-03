import InstrumentUniverse
import pandas as pd
import numpy as np
from Portfolio import Portfolio, universe
from datetime import datetime

class Admin:
    """ Admin should be our main robo advisor.
    Admin is responsible for manage instrument universe, users, and suggest portfolio to each users

    """
    tr_cost=0.0001
    
    def __init__(self):
        """
        Initialize the Admin.
        """
        self.intrumentUniverse = universe
        # use dictionary of userID and User in to admin manged user list
        # in real world, one admin will manage many users
        # although in our project, we may only have one user but we can
        # still make it generic
        self.users = {"1": {'initial_wealth':200000, 'target_wealth':300000, 'threshold_wealth':100000, 'target_prob':0.75, 'threshold_prob':0.95, 'tenure':5},
                        "2": {'initial_wealth':200000, 'target_wealth':300000, 'threshold_wealth':100000, 'target_prob':0.75, 'threshold_prob':0.95, 'tenure':5},
                            "3": {'initial_wealth':200000, 'target_wealth':300000, 'threshold_wealth':100000, 'target_prob':0.75, 'threshold_prob':0.95, 'tenure':5}
                    }
        
        self.today='2019-06-01'
        
        cash_start_date='2014-09-01'
        cash_amount=20000
        cash_dates=[datetime.strftime(item,'%Y-%m-%d') for item in pd.date_range(cash_start_date,self.today,freq='6MS')]
        cash_transacs=pd.DataFrame(cash_amount,index=cash_dates,columns=['Deposit-CAD'])
        all_dates=[datetime.strftime(item,'%Y-%m-%d') for item in pd.date_range(cash_start_date,self.today,freq='D')]
        
        self.cash_transacs=cash_transacs.reindex(all_dates,fill_value=0)
        self.portfolio={}
    #def addUser(self, user):
        """
        Add user into admin management user pool
        :param user: User
        :return:
        """
        
    def suggestPortfolio(self, userID, t):
        """
        suggest portfolio based on the user (indentify by userID)'s information
        and risk appetite, etc. Note that this userID must exist as a key in
        self.users
        
        Run optimization outside of the class, based on the parameters specified by user
        return asset weights
        
        :param userID: int
        :      t:      datetime 
        :return: Portfolio
        """
        #get parameters
        parameters=self.users[userID]
        self.initialInvest=parameters['initial_wealth']
        #pretend we run an optimization here to get the weights (done outside, outputs are in dict below)
        weights=[-0.00539872, -0.02485202,  0.72246993, -0.24030242,  0.54808322]
        secs=['MRD.TO',	'CIM.AX',	'GAPSX',	'LNC',	'KNEBV.HE']
        test_portf_dict=dict(zip(secs,weights))
        
        portfolios_to_select_from={'1':test_portf_dict}
        #,'2':{'ticker':weight},'3':{'ticker':weight}}
        
        self.PortfolioWeights=portfolios_to_select_from[userID]
        #self.t0=t
        
        #compute amounts based on weights and setup time
        instrumentsNAmounts={}
        for item in self.PortfolioWeights.keys():
            price=universe.get_price_in_currency(item,t,'CAD')   #change to get price in CAD
            weight=self.PortfolioWeights[item]
            amount=(self.initialInvest*weight)/(price*(1+self.tr_cost))
            instrumentsNAmounts[item]=amount
           
        
        self.portfolio[t]=Portfolio(instrumentsNAmounts, self.initialInvest)
        return instrumentsNAmounts
    
    def trackPortfolio(self, rebalance_flag=True,rebalance_freq='3MS'):
        '''
        creates and stores multiple portfolios on rebalancing dates        
        
        '''
        self.rebalance_flag=rebalance_flag
        if rebalance_flag:
            rebalance_dates=[datetime.strftime(item,'%Y-%m-%d') for item in pd.date_range(self.cash_transacs.index[0],self.today,freq=rebalance_freq)]
            
            for date in rebalance_dates:
                #take portfolio setup at date prior to rebalance date and calculate its value on rebalance date
                keys_tmp=list(self.portfolio.keys())
                date_setup=[i for i in keys_tmp if i<=date][-1]
                portf_val_tmp=self.portfolio[date_setup].getPortfolioValue(date)+self.cash_transacs.loc[date]
                #print(portf_val_tmp)
                instrumentsNAmounts={}
                for item in self.PortfolioWeights.keys():
                    price=self.intrumentUniverse.get_price_in_currency(item,date,'CAD')        #change to get price in CAD
                    weight=self.PortfolioWeights[item]
                    amount=portf_val_tmp*weight/(price*(1+self.tr_cost))
                    instrumentsNAmounts[item]=amount
                portfolio_to_add=Portfolio(instrumentsNAmounts,portf_val_tmp)
                #note that the portfolio method of self.portfolio is now changed to the latest date
                self.portfolio[date]=portfolio_to_add
        

    def getAccountValue(self,t):
        '''
        grabs the collection of portfolios (if rebalanced) and returns the value of appropriate portfolio at t
        
        return: float
        '''
        
        keys_tmp=list(self.portfolio.keys())
        date_setup=[i for i in keys_tmp if i<=t][-1]
        portf_val=self.portfolio[date_setup].getPortfolioValue(t)
                    
        return portf_val
    

import scipy as sp
def MoneyWeightedReturn(portfolio,cash_transacs,d1,d2):
    #get money weighted (IRR) return during given date range d1 to d2
    #assuming all capital gains are reinvested at rebalancing
    
    #get portfolio values at the beginning and end
    date_format='%Y-%m-%d'
    keys_tmp=list(portfolio.keys())
    date_setup=[i for i in keys_tmp if i<=d1][-1]
    date_last_rebal=[i for i in keys_tmp if i<=d2][-1]
    port_d1=portfolio[date_setup].getPortfolioValue(d1)
    port_d2=portfolio[date_last_rebal].getPortfolioValue(d2)
    #cash flow from capital gains at the end of observ period
    time_delta=datetime.strptime(d2,date_format)-datetime.strptime(d1,date_format)

    #now cash inflows in between:
    # also drop all zeros
    CFs_bw=cash_transacs[cash_transacs.iloc[:,0]!=0].loc[d1:d2]
    CFs_bw.loc[d2]=port_d2
    CFs_bw['TimeDelta']=[datetime.strptime(item,date_format)-datetime.strptime(d1,date_format) for item in CFs_bw.index]
    CFs_bw['TimeYears']=[item.days/365 for item in CFs_bw['TimeDelta']]

    def optim_err_fun(IRR):
        timeYears=CFs_bw['TimeYears'].values
        divisers=(1+IRR)**timeYears
        cash_flows=CFs_bw['Deposit-CAD'].values
        PV_infl=np.sum(np.divide(cash_flows,divisers))        
        PV_outfl=np.float(port_d1)
        error=(PV_outfl-PV_infl)**2
        return error
    res=sp.optimize.minimize(optim_err_fun,0.5)
    return res.x[0]


def TimeWeightedReturn(portfolio,cash_transacs,d1,d2):
    #get time weighted return during given date range d1 to d2
    #assuming all capital gains are reinvested at rebalancing
    
    date_format='%Y-%m-%d'
    
    #now cash inflows in between d1 d2:
    # also drop all zeros
    CFs_bw=cash_transacs[cash_transacs.iloc[:,0]!=0].loc[d1:d2]
    #need to split time into holding periods based on CF dates
    #each holding period return: HPR=(value_end-value_beg-CF_beg)/(value_beg+CF_beg)
    unique_dates=list(set(list(CFs_bw.index)+[d1]+[d2]))
    unique_dates.sort()
    hp_dates=zip(unique_dates[:-1],unique_dates[1:])
    
    hpr=[]
    keys_tmp=portfolio.keys()
    
    for pair in hp_dates:
#         print(list(hp_dates))
        setup_beg_date=[i for i in keys_tmp if i<=pair[0]][-1]
        setup_end_date=[i for i in keys_tmp if i<=pair[1]][-1]
        value_end=portfolio[setup_end_date].getPortfolioValue(pair[1])
        value_beg=portfolio[setup_beg_date].getPortfolioValue(pair[0])
        try:
            CF=cash_transacs.loc[pair[0]]
        except:
            CF=0
        hpr_tmp=(value_end-value_beg-CF)/(value_beg+CF)
        hpr.append(np.float(hpr_tmp))
    tot_return=np.product(np.array(hpr)+1)-1
    #annualize
    time_del=datetime.strptime(d2,date_format)-datetime.strptime(d1,date_format)
    ann_return=(1+tot_return)**(1/(time_del.days/365))-1
    return ann_return

def SimpleReturn(portfolio,d1,d2, annualize=True):
    #get simple portfolio return based on value time series
    #optional annualization
    date_format='%Y-%m-%d'
    keys_tmp=portfolio.keys()
    
    setup_beg_date=[i for i in keys_tmp if i<=d1][-1]
    setup_end_date=[i for i in keys_tmp if i<=d2][-1]
    
    value_end=portfolio[setup_end_date].getPortfolioValue(d2)
    value_beg=portfolio[setup_beg_date].getPortfolioValue(d1)
    
    tot_return=np.float((value_end-value_beg)/value_beg)
    out=tot_return
    if annualize:
        #annualize
        time_del=datetime.strptime(d2,date_format)-datetime.strptime(d1,date_format)
        ann_return=(1+tot_return)**(1/(time_del.days/365))-1
        out=np.float(ann_return)
    return out

def Volatility(portfolio, d1, d2, annualize=True):
    #computes monthly portfolio volatility
    #optional annualization
    date_format='%Y-%m-%d'
    keys_tmp=portfolio.keys()
    
    all_dates=[datetime.strftime(item,date_format) for item in pd.date_range(d1,d2,freq='M')]
    time_ser=[]
    for t in all_dates:
        setup_date=[i for i in keys_tmp if i<=t][-1]
        time_ser.append(np.float(portfolio[setup_date].getPortfolioValue(t)))
    ret_ser=np.divide(np.diff(time_ser),time_ser[1:])
    vol=np.std(ret_ser)
    out=np.float(vol)
    if annualize:
        out=np.float(vol*np.sqrt(12))
    return out

def MeanReturn(portfolio, d1, d2, annualize=True):
    #computes monthly portfolio returns and estimates mean
    #optional annualization
    date_format='%Y-%m-%d'
    keys_tmp=portfolio.keys()
    
    all_dates=[datetime.strftime(item,date_format) for item in pd.date_range(d1,d2,freq='M')]
    time_ser=[]
    for t in all_dates:
        setup_date=[i for i in keys_tmp if i<=t][-1]
        time_ser.append(np.float(portfolio[setup_date].getPortfolioValue(t)))
    ret_ser=np.divide(np.diff(time_ser),time_ser[1:])
    mean=np.mean(ret_ser)
    out=np.float(mean)
    if annualize:
        out=np.float(mean*12)
    return out

    # other methods