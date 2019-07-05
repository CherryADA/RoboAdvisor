import numpy as np
import pandas as pd
from datetime import datetime
import math
from HelperFunctions import fill_missing_data_business
from volModelHelperFunc import bs_formula
class Instrument:
    """ A Instrument is an abstract class, it's a parent class of
    Equity, Option, Future, ETF and risk factors so on.
    This should contain general parameters and methods among any asset classes.
    """

    def __init__(self, ticker, price):
        """
        Initialize the Instrument
        """
        self.ticker = ticker
        self.price = price

    # ===== then we could add any useful methods which can apply to all types of Instrument here ========
    def get_correlation(self, other, startDate, endDate):
        """
        Return the pearson correlation between self and other between start date and end date.
        :param other: Instrument
        :param startDate: Date
        :param endDate: Date
        :return:float
        """
        pass
    
    def compute_distance(self, dtw=False):
        """
        - computes the distance between two securities (Euclidean or DTW)
        """
        pass

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        return "Unknown"


    def compute_ret(self, log=False):
        """
        - calculates (log) returns of the stock
        - returns a list of a dataframe of returns and the CAGR
        """
        if not log:
            return (self.price.pct_change().dropna())
        else:
            return np.log(self.price.divide(self.price.shift(1))).dropna()

    def get_last_available_date(self):
        """

        :return: str
        string of the date which is the last available data point
        """
        return self.price.index.tolist()[-1]

    def get_the_price(self, t):
        """
        Return the price at time t in it's original currency.
        :param t: str
        :return: float
        """
        try:
            return float(self.price.loc[t])
        except:
            print("couldn't find the price at time of " + self.ticker + " " + t)
            return

    def get_slice_prices(self, start_date, end_date):
        """
        Get the slice of prices from start_date and end_date. All the missing value will be
        filled by forward fill method.
        :param start_date: str
        :param end_date: str/int
        if input end_date is int, it indicates the window_size. Otherwise, it indicates
        the end_date of the index
        :return: pd.Series
        """
        return fill_missing_data_business(self.price, start_date, end_date)
        # result = np.nan
        # if isinstance(end_date, int):
        #     inter_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
        #               pd.date_range(start=start_date, freq='B', periods=end_date)]
        #     result = pd.DataFrame(self.price.reindex(inter_dates, method='ffill').loc[:].astype(float))
        # elif isinstance(end_date, str):
        #     inter_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
        #               pd.date_range(start=start_date, freq='B', end=end_date)]
        #     result = pd.DataFrame(self.price.reindex(inter_dates, method='ffill').loc[:].astype(float))
        # else:
        #     print("input end_date as string or window size as int")
        #     return
        #
        # return result
## define all the child class here.
#class Bond(Instrument):
#    """
#
#    """
#
#    def __init__(self, couponRate, couponType, maturityDate, paymentFrequency, currency, type):
#        """
#        Initialize the Instrument
#        """
#        pass
 
    
class Stock(Instrument):
    """
    Global Equities 
    """
    
    def __init__(self, ticker, country, currency, sector, exchange, priceSeries):
        
        """
        priceSeries: A dataframe with dates as index 
        """
        self.ticker = ticker
        self.country = country
        self.currency = currency 
        self.sector = sector
        self.exchange = exchange 
        self.price = priceSeries 
        
        
    # def compute_ret(self, log=False):
    #     """
    #     - calculates (log) returns of the stock
    #     - returns a list of a dataframe of returns and the CAGR
    #     """
    #     if not log:
    #         return (self.price.pct_change().dropna())
    #     else:
    #         # ret = pd.DataFrame(index = self.price.index.copy())
    #         # for i in range(1, self.price.shape[0]):
    #         #     ret.iloc[i-1] = self.price.iloc[i]/self.price.iloc[i-1]
    #         # return ret
    #         return np.log(self.price.divide(self.price.shift(1))).dropna()
    
    
    def compute_vol(self, window):
        """
        - window: int (in month)
        - returns a list of a dataframe of rolling volatilities and an annualized vol 
        """
        pass
    
    def SMA(self, window=26):
        """
        -calculate simple moving averages with 
        """

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        # rmType = ""
        # if self.currency == "USD":
        #     rmType = "Equity:US"
        # else:
        #     rmType = "Equity:global"

        return "Equity:" + self.currency
    
    
class ETF(Instrument):
    
    def __init__(self, ticker, region, currency, stockPosition, bondPosition, holdings, rating, expenseRatio, assetClass,
                 priceSeries):
        """
        region: US or CANADA
        holdings: a dictionary of the etf's positions in basic_materials, communication_services, consumer_cyclical, 
                  consumer_defensive, energy, financial_services, healthcare, industrials, realestate, technology,
                  utilities
        rating: nan if no rating, otherwise, dict of rating with percentage
        assetClass: Equity, Fixed Income or Multi-Asset
        """
        self.ticker = ticker
        self.region = region
        self.currency = currency
        self.stock_pos = stockPosition 
        self.bond_pos = bondPosition
        self.holdings = holdings
        n = 0
        for rate in rating:
            n += rating[rate]
        if n == 0:
            self.rating = np.nan
        else:
            self.rating = rating
        self.expense_ratio = expenseRatio
        self.asset_class = assetClass
        self.price = priceSeries

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        rmType = ""
        if self.asset_class == "Fixed Income":
            rmType = "ETF:FixedIncome"
        elif self.asset_class == "Equity":
            rmType = "Equity:" + self.currency
        else:
            rmType = "ETF:Multi-asset"

        return rmType

    # def compute_ret(self, log=False):
    #     """
    #     - calculates (log) returns of the stock
    #     - returns a list of a dataframe of returns and the CAGR
    #     """
    #     if not log:
    #         return (self.price.pct_change().dropna())
    #     else:
    #         return np.log(self.price.divide(self.price.shift(1))).dropna()

class Cash(Instrument):
    """ Here we treat cash as another instrument, which means if you are holding cash will growth with the interest
    rate.
    """

    def __init__(self, ticker, priceSeries, currency):
        """
        Initialize Cash instrument
        :param priceSeries: series
        the interest rate series
        :param currency: str
        """
        self.ticker = ticker
        self.price = priceSeries
        self.currency = currency

    def get_cc_return(self, start_date, end_date):
        """
        Return the continuously compounded return from start_date to end_date
        :param start_date: str
        string of the form %Y-%m-%d
        :param end_date: str
        string of the form %Y-%m-%d
        :return: float
        """
        return math.exp(float(self.get_slice_prices(start_date, end_date).sum()))

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        return "Cash"

class Index(Instrument):

    def __init__(self, ticker, price):
        """
        Initialize a index which will be used for .

        :param ticker: ticker for the option
        :param price: pd.series
        """
        self.ticker = ticker
        self.price = price

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        return "Index"

class Option(Instrument):

    def __init__(self, ticker, T, K, cp_flag, underlying, interest_rate, issue_date, multiplier,
                 vol=None, premium=None,delta=None,vega=None, value=None):
        """
        Initialize a European option.

        :param ticker: str
        ticker for the option
        :param T: deltatime
        maturity
        :param K: int
        strike price
        :param cp_flag: str
        whether this is call ("call") or put ("put") option
        :param underying: Index
        :param interest_rate: pd.Series
        :param issue_date: str
        the issue_date of the option (used for compute the time to marturity)
        """
        self.ticker = ticker
        self.T = T
        self.cp_flag = cp_flag
        underlying.price = fill_missing_data_business(underlying.price, "2012-09-04", "2019-06-02", "B")
        self.underlying = underlying
        # note for option the price refer to implied volatility
        self.price = vol
        self.premium = premium
        self.issue_date = issue_date
        self.K = K
        self.interest_rate = fill_missing_data_business(interest_rate, "1963-7-1", "2019-06-02", "B")
        self.multiplier = multiplier
        self.delta = delta
        self.vega = vega
        self.value = value

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        return "VOL:US"

    def add_series(self):
        """
        Update the self.price
        # this should be done in instrument universe
        :return: nan
        """
        date_lst = self.price.index.tolist()
        issue_date = datetime.strptime(self.issue_date, "%Y-%m-%d")
        exdate = issue_date + self.T  # exdate is datetime
        premiums = []
        deltas = []
        vegas = []
        values = []
        for t in date_lst:
            values.append(self.get_intrinsic_value(t))
            if datetime.strptime(t, "%Y-%m-%d") > exdate:
                exdate = exdate + self.T
            T = (exdate - datetime.strptime(t, "%Y-%m-%d")).days/365
            if T == 0 :
                premiums.append(self.get_intrinsic_value(t))
                deltas.append(None)
                vegas.append(None)
            else:
                bs_result = bs_formula(self.underlying.price.loc[t], self.K, T, self.price.loc[t], self.interest_rate.loc[t], self.cp_flag)
                premiums.append(bs_result["price"])
                deltas.append(bs_result["delta"])
                vegas.append(bs_result["vega"])

        self.premium = pd.Series(premiums, index=date_lst).fillna(method = 'ffill')
        self.vega = pd.Series(vegas, index=date_lst).fillna(method = 'ffill')
        self.delta = pd.Series(deltas, index=date_lst).fillna(method = 'ffill')
        self.value = pd.Series(values, index=date_lst).fillna(method='ffill')

    def get_intrinsic_value(self, t):
        """
        Return the intrinsic value of option at time t, if it is call option : max(S_t-K, 0)
        if it is put option: max(K - S_k, 0)
        :param t:
        :return:
        """
        underlying_prices = fill_missing_data_business(self.underlying.price, "2012-09-04", "2019-06-02", "B")
        if self.cp_flag == "call":
            return max(underlying_prices.loc[t] - self.K, 0)
        else:
            return max(self.K - underlying_prices.loc[t], 0)


    # def compute_ret(self, log=False):
    #     """
    #     - calculates (log) returns of the stock
    #     - returns a list of a dataframe of returns and the CAGR
    #     """
    #     if not log:
    #         return (self.price.pct_change().dropna())
    #     else:
    #         return np.log(self.price.divide(self.price.shift(1))).dropna()

class RiskFactor(Instrument):

    def __init__(self, ticker, priceSeries, currency):
        """

        :param ticker: ticker/name of the riskFactor
        :param priceSeries: series of prices/value of the risk factor
        :param target_instruments: string
        one of equity_US, equity_global, etf or vol
        list of target instruments that this risk factor will fit to
        """
        self.ticker = ticker
        self.price = priceSeries
        self.currency = currency

