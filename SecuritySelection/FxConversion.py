#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 15:07:35 2019

@author: sylvieshi
"""

import pandas as pd 
import copy 

import warnings
warnings.filterwarnings("ignore")

from Cluster import *

curr_to_keep = ['CAD', 'USD', 'EUR', 'JPY', 'AUD']
years = ['2008', '2009', '2010', '2011', '2012', '2013', '2014']


'''
1. separate the foreign_mtx into several dataframes based on the currency we chose 
2. for each currency, separate the data by years (a dictionary of lists)
3. apply the yearly Fx rates to each small matrix
4. stack them up to get a big array for each currency 
5. recombine all the securities 
'''

def separate_by_currency(foreign_mtx, curr_set, tick_to_curr):
    '''
    foreign_mtx: dataframe of all the securities denominated in foreign currencies 
    curr_set: list of currencies we want to keep 
    tick_to_curr: dictionary of tickers to currencies 
    '''
    currency_vec = []
    curr_separated = {}
    new_idx = []
    
    mtx_copy = copy.deepcopy(foreign_mtx)
    
    for ii in range(foreign_mtx.shape[0]):
        new_idx.append(str(foreign_mtx.index[ii])[:4])
    mtx_copy['year'] = new_idx
    mtx_copy.set_index('year', inplace=True)
        
    foreign_mtx_transposed = mtx_copy.T
    for i in range(foreign_mtx_transposed.shape[0]):
        currency_vec.append(tick_to_curr[foreign_mtx_transposed.index[i]])
    foreign_mtx_transposed['curr'] = currency_vec
    
    for cur in curr_set: 
        curr_separated[cur] = foreign_mtx_transposed[foreign_mtx_transposed['curr'] == cur]
    
    return curr_separated
    


def separate_by_years(curr_separated, years, curr_set):
    '''
    curr_separated: dictionary of security prices separated by currencies (output from the function separate_by_currency)
    years: list of years as strings 
    '''
    separators = [0]
    yr_idx = list(curr_separated['AUD'].columns)
    yr_count = 0 
    for i in range(len(yr_idx)):
        if yr_idx[i] == years[yr_count]:
            pass
        else:
            separators.append(i)
            yr_count += 1 
    
    sep_by_yr = {}
    for curr in curr_set:
        df_current = curr_separated[curr].drop('curr', axis=1)
        sep_by_yr[curr] = [df_current.iloc[:, separators[n]:separators[n+1]] for n in range(len(separators)-1)]
    
    return sep_by_yr
    
# NOTE: resulting dfs from the function before have dtype = OBJECT! 
def convert_to_usd(sep_by_yr, fx_rates, years, curr_set):
    
    large_dict = {}
    for curr in curr_set:
        df1 = pd.DataFrame()
        for i in range(len(years)):
            df_cur = sep_by_yr[curr][i].astype(float)
            curr_vec = fx_rates.filter(like=curr, axis=1)
            rate = float(curr_vec.loc[int(years[i])])
            df2 = df_cur * rate
            df1 = pd.concat([df1, df2], axis=1)
        large_dict[curr] = df1 

    return large_dict 

def cleaning_up(large_dict, foreign_mtx):
    
    '''
    concatenate all securities, take transpose and re-index
    '''
    true_index = list(foreign_mtx.index)
    
    df2 = pd.DataFrame()
    for key, value in large_dict.items():
        df1 = value
        df2 = pd.concat([df1, df2], axis=0)
    final_df = df2.T
    final_df['date'] = true_index
    final_df.set_index('date', inplace=True)
    
    return final_df



if __name__ == '__main__':
    curr_separated = separate_by_currency(eq_cluster, curr_to_keep, tick_to_curr)
    sep_by_yr = separate_by_years(curr_separated, years, curr_to_keep)
    large_dict = convert_to_usd(sep_by_yr, fx_for_filtered_eq, years, curr_to_keep)
    
    final_df = cleaning_up(large_dict, eq_cluster)
    
    final_df.to_csv('filtered_eq.csv')
    
    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    