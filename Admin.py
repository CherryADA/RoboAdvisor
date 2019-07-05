import InstrumentUniverse
import pandas as pd
import numpy as np
from Portfolio import Portfolio, universe
from datetime import datetime
from Optimization import find_weights

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
        self.users = {"1": {'initial_wealth':200000, 'target_wealth':300000, 'threshold_wealth':100000, 'target_prob':0.75, 'threshold_prob':0.95, 'tenure':5,'secs':['MRD.TO','CIM.AX','GAPSX','LNC','KNEBV.HE']},
                        "2": {'initial_wealth':200000, 'target_wealth':300000, 'threshold_wealth':100000, 'target_prob':0.75, 'threshold_prob':0.95, 'tenure':5,'secs':['HBD.TO','HGU.TO','OIH','RIT.TO','EMB']},
                            "3": {'initial_wealth':200000, 'target_wealth':300000, 'threshold_wealth':100000, 'target_prob':0.75, 'threshold_prob':0.95, 'tenure':5}
                    }
        
        self.today='2019-06-01'
        
        cash_start_date='2014-09-01'
        cash_amount=20000
        cash_dates=[datetime.strftime(item,'%Y-%m-%d') for item in pd.date_range(cash_start_date,self.today,freq='6MS')]
        cash_transacs=pd.DataFrame(cash_amount,index=cash_dates,columns=['Deposit-CAD'])
        all_dates=[datetime.strftime(item,'%Y-%m-%d') for item in pd.date_range('2000-01-01',self.today,freq='D')]
        
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
        initial_wealth=parameters['initial_wealth']
        target_wealth=parameters['target_wealth']
        threshold_wealth=parameters['threshold_wealth']
        target_prob=parameters['target_prob']
        threshold_prob=parameters['threshold_prob']
        tenure=parameters['tenure']
        
        #pretend we run an optimization here to get the weights (done outside, outputs are in dict below)
        #weights=[-0.00539872, -0.02485202,  0.72246993, -0.24030242,  0.54808322]
        secs=parameters['secs']

        #test_portf_dict=dict(zip(secs,weights))
        
        #portfolios_to_select_from={'1':test_portf_dict}
        #,'2':{'ticker':weight},'3':{'ticker':weight}}
        self.possible_portf_mean_and_vol, possible_weights = find_weights(initial_wealth,target_wealth,threshold_wealth,target_prob,threshold_prob,tenure,secs,t,60)
        self.possible_weights=[]
        self.suggest_date=t
        for i in range(0,len(possible_weights)):
            self.possible_weights.append(dict(zip(secs,possible_weights[i])))
        return self.possible_portf_mean_and_vol, self.possible_weights
    
    def acceptPortfolio(self,mean_and_vol_id):
        
        try:
            keys_to_remove=list(self.portfolio.keys())
            keys_to_remove=[item for item in keys_to_remove if item<=self.suggest_date]
        except:
            keys_to_remove=[]
            
        if len(keys_to_remove)>0:
            for item in keys_to_remove:
                self.portfolio.pop(item)
            
        self.PortfolioWeights=self.possible_weights[mean_and_vol_id]
        #self.t0=t
        
        #compute amounts based on weights and setup time
        instrumentsNAmounts={}
        t=self.suggest_date
        for item in self.PortfolioWeights.keys():
            price=universe.get_price_in_currency(item,t,'CAD')   #change to get price in CAD
            weight=self.PortfolioWeights[item]
            amount=(self.initialInvest*weight)/(price*(1+self.tr_cost))
            instrumentsNAmounts[item]=amount
           
        
        self.portfolio[t]=Portfolio(instrumentsNAmounts, self.initialInvest)
        return instrumentsNAmounts
    
    def trackPortfolio(self, rebalance_flag=True,rebal_start_date='2014-09-01',rebalance_freq='3MS'):
        '''
        creates and stores multiple portfolios on rebalancing dates        
        
        '''
        keys_to_remove=list(self.portfolio.keys())
        if len(keys_to_remove)>1:
            for item in keys_to_remove[1:]:
                self.portfolio.pop(item)
                
        self.rebalance_flag=rebalance_flag
        
        if rebalance_flag:
            rebalance_dates=[datetime.strftime(item,'%Y-%m-%d') for item in pd.date_range(rebal_start_date,self.today,freq=rebalance_freq)]
            
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

def PortfolioVaR(account,fit_start_date,fit_end_date,annualize):
    import numpy as np
    import scipy as sp
    model1={}
    for item in account.PortfolioWeights.keys():
        model1[item]=universe.fitFactorModel(item,fit_start_date,252*5).params
    
    factor_cov=universe.get_risk_factors_cov(fit_start_date,252*5,freq='B',annualize)
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

def MarginalVaRs(account,fit_start_date,fit_end_date):
    #Think about currency
    #fit model in local currency, aggregate to potfolio level in CAD
    #when to do conversion for risk metrics???
    #Also think about marginal on security level not on RF level!!!
    from HelperFunctions import fill_missing_data_business
    result_df = pd.DataFrame()
    factor_tickers = universe._riskFactors.keys()
    #print(factor_tickers)
    for k in factor_tickers:
        result_df[k] = fill_missing_data_business(universe._riskFactors[k].price, fit_start_date, fit_end_date,freq='B')
    factor_cov=result_df.cov()*252
    model1 = {}
    for item in account.PortfolioWeights.keys():
        model1[item]=universe.fitFactorModel(item,fit_start_date,252*5).params
    betas=pd.DataFrame(index=list(model1.keys()),columns=factor_cov.index)
    for item in model1.keys():
        betas.loc[item,:]=model1[item].reindex(factor_cov.index,fill_value=0)
        
    sec_cov=pd.DataFrame(np.dot(betas,np.dot(factor_cov,betas.transpose())),index=list(model1.keys()),columns=list(model1.keys()))
    weights=[np.float(item) for item in list(account.PortfolioWeights.values())]
    portf_vol=np.sqrt(np.dot(weights,np.dot(sec_cov,weights)))
    
    
    result_df['Portfolio']=np.array(np.dot(np.dot(result_df,betas.transpose()),weights)).astype(np.float64)
    result_df_cov=252*result_df.cov()
    betas_new=result_df_cov.loc[:,'Portfolio'].divide(portf_vol**2)    
    MVaRs=betas_new*sp.stats.norm.ppf(0.95)*portf_vol
    #now to dollar value
#     for item in account.PortfolioWeights.keys():
        
    return MVaRs

#decomposing security return
def ReturnAttribCurrency(PortfolioWeights,d1,d2):
    df_tmp=pd.DataFrame(index=list(PortfolioWeights.keys()),columns=['Weights','Currency','LocalReturn','CADReturn','FX_appr'])
    for sec_name in PortfolioWeights.keys():
        local_ret=universe.get_security(sec_name).price.loc[today_date]/universe.get_security(sec_name).price.loc['2019-03-01']-1
        report_ret=universe.get_price_in_currency(sec_name,today_date,'CAD')/universe.get_price_in_currency(sec_name,'2019-03-01','CAD')-1
        FX_app=(report_ret-local_ret)/(local_ret+1)

        df_tmp.loc[sec_name,:]=[PortfolioWeights[sec_name],
                                universe.get_security(sec_name).currency,
                                local_ret,
                                report_ret,
                                FX_app]
    df_tmp['LocalReturnWeighted']=df_tmp['LocalReturn'].multiply(df_tmp['Weights'])
    df_tmp['CADReturnWeighted']=df_tmp['CADReturn'].multiply(df_tmp['Weights'])
    df_tmp['CurContrWeighted']=df_tmp['FX_appr'].multiply(df_tmp['Weights'])

    cur_contrib=df_tmp[['Currency','LocalReturnWeighted','CADReturnWeighted','CurContrWeighted']].groupby('Currency').sum()
    local_cur_return=cur_contrib.sum()['LocalReturnWeighted']
    report_cur_return=cur_contrib.sum()['CADReturnWeighted']
    cur_contrib.rename(columns={'CurContrWeighted':'Return Contribution'},inplace=True)
    return cur_contrib['Return Contribution'], local_cur_return, report_cur_return

    # other methods