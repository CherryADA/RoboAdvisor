#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 16:12:35 2019

@author: sylvieshi
"""

import numpy as np 

investment_date = '2014-04-01'

class Filters():
    
    def __init__(self, price_series, desc_series, initial_invest_date, fx_rates, log_ret=True):
        '''
        price_series: dataframe
        desc_series: dataframe
        '''
        
        self.price = price_series 
        self.desc = desc_series 
        self.fx = fx_rates 
        self.investment_dt = initial_invest_date
        
    def delete_curr(self, curr):
        '''
        countries: a list of currencies we want to delete from the pool of securities 
    
        '''
        for name in curr: 
            sec_names = []
            for i in range(self.desc.shape[0]):
                if self.desc.ix[i, 'Currency'] == name:
                    if self.desc.index[i] in self.price.columns:
                        sec_names.append(self.desc.index[i])
            
            self.price = self.price.drop(sec_names, axis=1)
        
        return self.price
    
    def delete_penny(self, tick_to_curr, upper_bound=1):
        
        '''
        - convert prices to usd first 
        - delete securities with price lower than upper_bound on the initial investment_date
        - tick_to_curr: a dictionary with ticker names as keys and 
        '''
        fx_rates = self.fx.loc[self.investment_dt, :]
        foreign_px = self.price.loc[self.investment_dt, :]
        usd_px = {}
        for i in range(len(foreign_px)):
            curr = tick_to_curr[foreign_px.index[0]]
            usd_px[foreign_px.index[i]] = float(foreign_px.iloc[i]) * float(fx_rates.filter(like=curr))
        
        penny = []
        for key in usd_px.keys():
            if usd_px[key] <= upper_bound:
                penny.append(key)
        
        self.price = self.price.drop(penny, axis=1)
        
        return self.price
        
    def delete_high_vol(self, percentage=2e-1):
        
        '''
        delete all securities with a daily vol in the top percentile (percentage)
        
        '''
        return_values = self.price.astype(float).pct_change(axis=0)
        stdev = np.nanstd(return_values, axis=0) * np.sqrt(252)
        ticks = self.price.columns 
        
        ticker_std = np.vstack((ticks, stdev))
        
        # sort the standard deviations 
        ticker_std.sort()
        num_to_drop = round(percentage * ticker_std.shape[1])
        tickers_to_drop = list(ticker_std[0, -num_to_drop:])
        
        self.price = self.price.drop(tickers_to_drop, axis=1)
        
        return self.price
    
    def trimmed_dict(self, tick_to_curr):
        '''
        Match the keys in tick_to_curr dictionary with securities 
        in the current price dataframe 
        '''
        tick_list = list(tick_to_curr.keys())
        for tick in tick_list:
            if tick not in list(self.price.columns):
                try:
                    del tick_to_curr[tick]
                except KeyError:
                    pass 
        return tick_to_curr 
    
    
        
        
        
        
        
            