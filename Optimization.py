# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 12:14:20 2019

@author: jkhai
"""


#def trace_efficient_frontier(mean,cov):
#    mean=np.array(mean*12)
#    cov=np.array(12*cov)
#    cov_inv=la.inv(cov)
#    
#    k=np.sum(np.matmul(mean.transpose(),cov_inv))
#    l=np.matmul(np.matmul(mean.transpose(),cov_inv),mean)
#    m=np.sum(cov_inv.sum())
#    g=(l*cov_inv.sum(axis=1)-k*np.matmul(cov_inv,mean))/(l*m-k**2)
#    h=(-k*cov_inv.sum(axis=1)+m*np.matmul(cov_inv,mean))/(l*m-k**2)
#    a=np.matmul(np.matmul(h.transpose(),cov),h)
#    b=2*np.matmul(np.matmul(g.transpose(),cov),h)
#    c=np.matmul(np.matmul(g.transpose(),cov),g)
#
#    mean_plot=np.array(range(0,1000))-500
#    mean_plot=mean_plot/1000
#    sigma_plot=[np.sqrt(a*item**2+b*item+c) for item in mean_plot]
#    plt.plot(sigma_plot,mean_plot)
#    return mean_plot, sigma_plot



def find_weights(initial_wealth,target_wealth,threshold_wealth,target_prob,threshold_prob,tenure,instr_names,est_date,num_per):
    import scipy as sp
    import numpy as np
    import pandas as pd
    import numpy.linalg as la
    from matplotlib import pyplot as plt
    from Portfolio import universe
    from datetime import datetime
    
    date_format='%Y-%m-%d'
    
    def trace_efficient_frontier(mean,cov,short_sell=True):
        mean=np.array(mean*12)
        cov=np.array(12*cov)
        mean_plot=np.arange(0,0.301,0.001)
        w0=np.ones(len(mean))/len(mean)
        def obj_fun(w):
            portf_var=np.dot(w,np.dot(cov,w))
            return 0.5*portf_var
        sigma_plot=[]
        weights=[]
        bounds=[(0,None)]*len(mean)
        if short_sell:
            bounds=[(None,None)]*len(mean)
        for item in mean_plot:
            res=sp.optimize.minimize(obj_fun,w0,constraints=[{'type':'eq','fun':lambda w: np.dot(w,mean)-item},{'type':'eq','fun':lambda w: np.sum(w)-1}],bounds=bounds)
            sigma_plot.append(np.sqrt(2*res.fun))
            weights.append(res.x)
    #         print(res.fun)
        plt.plot(sigma_plot,mean_plot)
        return mean_plot, sigma_plot, weights
        
    
    def trace_GPLC(initial_wealth,target_wealth,target_prob,tenure):
        sigma_plot=np.arange(0,1,0.001)
    #     sigma_plot=sigma_plot/1000
        z0=sp.stats.norm.ppf(target_prob)
        mean_plot=[0.5*item**2+z0*item/np.sqrt(tenure)+(1/tenure)*np.log(target_wealth/initial_wealth) for item in sigma_plot]
        plt.plot(sigma_plot,mean_plot)
        return mean_plot, sigma_plot
    
    def target_weights(GPLC_mean, GPLC_sigma, LT_mean, LT_sigma, EFC_mean, EFC_sigma, EFC_weights, EF_mean, EF_sigma, EF_weights):
        
        inters_with_EFC=[]
        n_EFC=[]
        for item in zip([np.round(item,3) for item in GPLC_mean],[np.round(item,3) for item in GPLC_sigma]):
            i_EFC=0
            for item2 in zip([np.round(item,3) for item in EFC_mean],[np.round(item,3) for item in EFC_sigma]):
                if np.logical_and(item[0]==item2[0],item[1]==item2[1]):
                    n_EFC.append(i_EFC)
                    inters_with_EFC.append(item2)
                i_EFC=i_EFC+1
                
        inters_with_EF=[]
        n_EF=[]
        for item in zip([np.round(item,3) for item in GPLC_mean],[np.round(item,3) for item in GPLC_sigma]):
            i_EF=0
            for item2 in zip([np.round(item,3) for item in EF_mean],[np.round(item,3) for item in EF_sigma]):
                if np.logical_and(item[0]==item2[0],item[1]==item2[1]):
                    n_EF.append(i_EF)
                    inters_with_EF.append(item2)
                i_EF=i_EF+1
                
        inters_with_EFC_LT=[]
        inters_with_EF_LT=[]
        n_EFC_LT=[]
        n_EF_LT=[]
        if np.logical_and(inters_with_EFC==[],inters_with_EF==[]):
            for item in zip([np.round(item,3) for item in LT_mean],[np.round(item,3) for item in LT_sigma]):
                i_EFC_LT=0
                for item2 in zip([np.round(item,3) for item in EFC_mean],[np.round(item,3) for item in EFC_sigma]):
                    if np.logical_and(item[0]==item2[0],item[1]==item2[1]):
                        n_EFC_LT.append(i_EFC_LT)
                        inters_with_EFC_LT.append(item2) 
                    i_EFC_LT=i_EFC_LT+1
            for item in zip([np.round(item,3) for item in LT_mean],[np.round(item,3) for item in LT_sigma]):
                i_EF_LT=0
                for item2 in zip([np.round(item,3) for item in EF_mean],[np.round(item,3) for item in EF_sigma]):
                    if np.logical_and(item[0]==item2[0],item[1]==item2[1]):
                        n_EF_LT.append(i_EF_LT)
                        inters_with_EF_LT.append(item2)
                    i_EF_LT=i_EF_LT+1
        
        weight_EF=[]
        if inters_with_EF!=[]:
            for item in range(0,len(inters_with_EF)):
                weight_EF.append(EF_weights[n_EF[item]])
        else:
            for item in range(0,len(inters_with_EF_LT)):
                weight_EF.append(EF_weights[n_EF_LT[item]])
        weight_EFC=[]
        
        if inters_with_EFC!=[]:
            for item in range(0,len(inters_with_EFC)):
                weight_EFC.append(EFC_weights[n_EFC[item]])
        else:
            for item in range(0,len(inters_with_EFC_LT)):
                weight_EFC.append(EFC_weights[n_EFC_LT[item]])
            
        return inters_with_EFC,inters_with_EF,inters_with_EFC_LT,inters_with_EF_LT,weight_EF,weight_EFC


    
    
    dates_monthly=[datetime.strftime(item,date_format) for item in pd.date_range(end=est_date,periods=num_per+1,freq='BM')]
    instruments_used=pd.DataFrame(index=dates_monthly,columns=instr_names)
    for item in instr_names:
        instruments_used[item]=universe.get_security(item).price[dates_monthly]
    instruments_log_monthly=np.log(instruments_used.divide(instruments_used.shift(1))).dropna()
    
    mean=instruments_log_monthly.mean()
    cov=instruments_log_monthly.cov()
    
    GPLC_mean, GPLC_sig = trace_GPLC(initial_wealth,target_wealth,target_prob,tenure)
    LT_mean, LT_sig = trace_GPLC(initial_wealth,threshold_wealth,threshold_prob,tenure)
    
    EF_mean, EF_sig, EF_weights = trace_efficient_frontier(mean,cov,short_sell=True)
    EFC_mean, EFC_sig, EFC_weights = trace_efficient_frontier(mean,cov,short_sell=False)
    
    inters_with_EFC,inters_with_EF,inters_with_EFC_LT,inters_with_EF_LT, weight_EF,weight_EFC = target_weights(GPLC_mean, 
                                GPLC_sig, 
                                LT_mean, 
                                LT_sig, 
                                EFC_mean, 
                                EFC_sig, 
                                EFC_weights, 
                                EF_mean, 
                                EF_sig, 
                                EF_weights)
    if inters_with_EF!=[]:
        print('We are in a good state, target weights with short selling returned')
        return inters_with_EF,weight_EF
    elif inters_with_EFC!=[]:
        print('We are in a good state, target weights without short selling returned')
        return inters_with_EFC,weight_EFC
    elif inters_with_EFC_LT!=[]:
        print('We are in a bad state, short selling not allowed, safest weights returned')
        return inters_with_EFC_LT,weight_EFC
    else:
        print('Please select another set of securities. No appropriate weights found')
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    