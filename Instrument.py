class Instrument:
    """ A Instrument is an abstract class, it's a parent class of
    Bond, Equity, Option, Future, ETF and risk factors so on.
    This should contain general parameters and methods among any asset classes.
    """

    def __init__(self):
        """
        Initialize the Instrument
        """
        pass

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
    
    def __init__(self, country, currency, sector, exchange, priceSeries):
        
        """
        priceSeries: A dataframe with dates as index 
        """
        self.country = country
        self.currency = currency 
        self.sector = sector
        self.exchange = exchange 
        self.price = priceSeries 
        
        
    def compute_ret(self, log=False):
        """
        - calculates (log) returns of the stock 
        - returns a list of a dataframe of returns and the CAGR
        """
        pass
    
    
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
    
    
    
class ETF(Instrument):
    
    def __init__(self, region, currency, stockPosition, bondPosition, holdings, rating, expenseRatio, assetClass):
        """
        region: US or CANADA
        holdings: a dictionary of the etf's positions in basic_materials, communication_services, consumer_cyclical, 
                  consumer_defensive, energy, financial_services, healthcare, industrials, realestate, technology,
                  utilities
        rating: nan if no rating
        assetClass: Equity, Fixed Income or Multi-Asset
        """
        
        self.region = region
        self.currency = currency
        self.stock_pos = stockPosition 
        self.bond_pos = bondPosition
        self.holdings = holdings 
        self.rating = rating 
        self.expense_ratio = expenseRatio
        self.asset_class = assetClass
        
    
        
        
        
        
        
        
        
        
        
        