from Instrument import Instrument, Stock, ETF
from InstrumentUniverse import InstrumentUniverse
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta


def register_universe_main():
    """ register all instrument into our universe

    :return:
    """
    universe = InstrumentUniverse()
    # register all equities first
    dir_path = os.getcwd()
    data_path = dir_path + "/Data/"
    filtered_path = dir_path + "/SecuritySelection/"
    equity_prices = pd.read_csv(filtered_path + "final_eq.csv")
    equity_prices.set_index('date', inplace=True)

    # read Equities description
    equity_desc = pd.read_csv(data_path + "Instrument_description/"+"equity_desc.csv")
    col_name = [col_name.lower() for col_name in equity_desc.columns.tolist()]
    equity_desc.columns = col_name
    for ticker in equity_prices.columns.tolist():
        info = equity_desc[equity_desc.ticker == ticker].iloc[0]
        s = Stock(ticker, info['country'], info['currency'], info['sector'], info['exchange'], equity_prices[ticker])
        universe.addInstrument(s)

    # ETF
    etf_prices = pd.read_csv(filtered_path + "final_etf.csv")
    etf_prices.set_index('date', inplace=True)
    etf_prices.head()

    # read Equities description
    etf_desc = pd.read_csv(data_path + "Instrument_description/"+"etf_desc.csv")
    col_name = [col_name.lower() for col_name in etf_desc.columns.tolist()]
    col_name[0] = "ticker"
    etf_desc.columns = col_name

    holdings_col = ['basic_materials', 'communication_services',
                    'consumer_cyclical', 'consumer_defensive', 'energy',
                    'financial_services', 'healthcare', 'industrials', 'realestate',
                    'technology', 'utilities']
    rating_col = ['a', 'aa', 'aaa', 'b', 'bb', 'bbb', 'below_b', 'other', 'us_government']

    for ticker in etf_prices.columns.tolist():
        info = etf_desc[etf_desc.ticker == ticker].iloc[0]
        holdings = {}
        rating = {}
        for h in holdings_col:
            holdings[h] = info[h]
        for r in rating_col:
            rating[r] = float(info[r])

        s = ETF(ticker, info['region'], info['currency'], info['stock_position'], info['bond_position'], holdings, rating,
                info['expense_ratio'], info["asset_class"], etf_prices[ticker])
        universe.addInstrument(s)
    ## register all risk factor

    # load F-F files (both US F-F and International F-F)
    # US Fama-French
    FF_rf_us = pd.read_csv(data_path + 'RiskFactors/F-F_Research_Data_5_Factors_2x3_daily.CSV', skiprows=(0, 1))
    FF_rf_us['Unnamed: 0'] = [datetime.strftime(datetime.strptime(str(item), '%Y%m%d'), '%Y-%m-%d') for item in
                              FF_rf_us['Unnamed: 0']]
    FF_rf_us.set_index('Unnamed: 0', inplace=True)
    FF_rf_us_dec = FF_rf_us.divide(100)

    # # International Fama-French
    # FF_rf_global = pd.read_csv(data_path + 'RiskFactors/Global_5_Factors_Daily.csv', skiprows=(0, 1, 2, 3, 4, 5))
    # FF_rf_global['Unnamed: 0'] = [datetime.strftime(datetime.strptime(str(item), '%Y%m%d'), '%Y-%m-%d') for item in
    #                               FF_rf_global['Unnamed: 0']]
    # FF_rf_global.set_index('Unnamed: 0', inplace=True)
    # FF_rf_global_dec = FF_rf_global.divide(100)

    # Factors for International equities
    currencyList = ["CAD", "AUD", "EUR", "JPY"]
    for c in currencyList:
        filename = data_path + 'RiskFactors/' + 'equity_' +  c + '_factors.csv'
        df = pd.read_csv(filename)
        df.set_index('Unnamed: 0', inplace=True)
        df_des = df.divide(100)
        universe.add_riskFactor_dataFrame(df_des, "Equity:" + c)

    # load risk factors for Fixed income etfs
    # ETF_rf = pd.read_excel(data_path + 'RiskFactors/Risk_Factor_ETF.xlsx', sheet_name="Daily_data")
    # ETF_rf['Date'] = [datetime.strftime(item, '%Y-%m-%d') for item in ETF_rf['Date']]
    # ETF_rf.set_index('Date', inplace=True)
    ETF_rf = pd.read_csv(data_path + 'RiskFactors/etf_fixedIncome_factors.csv')
    ETF_rf.set_index('Date', inplace=True)

    # load risk factors for vol
    vol_rf = pd.read_csv(data_path + "RiskFactors/vol_factors.csv")
    vol_rf.set_index('Date', inplace=True)


    universe.add_riskFactor_dataFrame(FF_rf_us_dec, "Equity:USD")
    #universe.add_riskFactor_dataFrame(FF_rf_global_dec, "Equity:global")
    universe.add_riskFactor_dataFrame(ETF_rf, "ETF:FixedIncome")
    universe.add_riskFactor_dataFrame(vol_rf, "VOL:US")

    # register the FX exchange rate into the universe
    fx = pd.read_csv(data_path + "RiskFactors/fx_factors.csv")
    fx.set_index('Unnamed: 0', inplace=True)
    universe.add_fx(fx)

    # for ticker in FF_rf_us_dec.columns.tolist():
    #     rf = RiskFactor(ticker, FF_rf_us_dec[ticker], "equity_US")
    #     universe.addInstrument(rf)
    #
    # for ticker in FF_rf_global_dec.columns.tolist():
    #     rf = RiskFactor(ticker, FF_rf_global_dec[ticker], "equity_global")
    #     universe.addInstrument(rf)
    #
    # for ticker in ETF_rf.columns.tolist():
    #     rf = RiskFactor(ticker, ETF_rf[ticker], "ETF:FixedIncome")
    #     universe.addInstrument(rf)
    return universe
