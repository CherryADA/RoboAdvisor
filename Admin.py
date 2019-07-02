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
        print(self.portfolio[date_setup].portfolio)
        portf_val=self.portfolio[date_setup].getPortfolioValue(t)
   
            
        return portf_val


    # other methods