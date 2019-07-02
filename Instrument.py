import numpy as np
import pandas as pd


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

    # ===== then we could add any useful methods which can apply to all types of Intrument here ========
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
    """

    """
class Option(Instrument):

    def __init__(self, ticker, T, isCall, underlyingTicker, priceSeries, impliedVol):
        """
        Initialize a European option.

        :param ticker: ticker for the option
        :param T: Time to maturity
        :param isCall: whether this is call or put option
        :param underyingTicker:
        :param priceSeries:
        """
        self.ticker = ticker
        self.T = T
        self.isCall = isCall
        self.underlyingTicker = underlyingTicker
        self.priceSeries = priceSeries
        self._impliedVol = impliedVol

    def get_type_RM(self):
        """
        :return: string
        return the type of the instrument
        """
        return "VOL:US"

    def calculate_implied_vol(self):
        """
        Return the series our implied volatility from price series
        :return:
        """
        pass

    # def compute_ret(self, log=False):
    #     """
    #     - calculates (log) returns of the stock
    #     - returns a list of a dataframe of returns and the CAGR
    #     """
    #     if not log:
    #         return (self.price.pct_change().dropna())
    #     else:
    #         return np.log(self.price.divide(self.price.shift(1))).dropna()
# class RiskFactor(Instrument):
#
#     def __init__(self, ticker, priceSeries, target_instruments):
#         """
#
#         :param ticker: ticker/name of the riskFactor
#         :param priceSeries: series of prices/value of the risk factor
#         :param target_instruments: string
#         one of equity_US, equity_global, etf or vol
#         list of target instruments that this risk factor will fit to
#         """
#         self.ticker = ticker
#         self.priceSeries = priceSeries
#         self.target_instruments = target_instruments

