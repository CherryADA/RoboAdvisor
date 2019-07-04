import numpy as np
import pandas as pd
from datetime import datetime
import math
from HelperFunctions import fill_missing_data_business

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
        else:
            rmType = "ETF:other"

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
        return "ETF:FixedIncome"

class Option(Instrument):

    def __init__(self, ticker, T, K, cp_flag, underlyingTicker, issue_date):
        """
        Initialize a European option.

        :param ticker: ticker for the option
        :param T: Time to maturity
        :param K: strike price
        :param cp_flag: whether this is call ("C") or put ("P") option
        :param underyingTicker: str
        :param issue_date: str
        the issue_date of the option (used for compute the time to marturity)
        """
        self.ticker = ticker
        self.T = T
        self.cp_flag = cp_flag
        self.underlyingTicker = underlyingTicker
        # note for option the price refer to implied volatility
        self.price = np.nan
        self._premium = np.nan
        self.issue_date = issue_date
        self.K = K

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        return "VOL:US"

    def add_premium_series(self, prices):
        """
        Update the self.price
        # this should be done in instrument universe
        :return: nan
        """
        self._premium = prices

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

