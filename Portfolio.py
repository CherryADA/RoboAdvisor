from registerUniverse import register_universe_main
# global variable
global universe
universe = register_universe_main()

class Portfolio:
    """ the portfolio with with weights and assets with other operations
    """

    def __init__(self, instrumentsNAmounts, totalInvest):
        """
        Initialize the portfolio with tuple of instruments and the corresponding
        amounts held.

        public attribute
        :param instrumentsNAmounts: dict[str] -> float
        :param totalInvest: float
        total amount of USD used in this portfolio investment
        """
        # add all necessary attributes here which link to portfolio and
        # will be tracked.
        self.portfolio = instrumentsNAmounts
        self.totalInvest = totalInvest

    def getPortfolioValue(self, t):
        """
        Return the portfolio value at time t
        :return: float
        """
        sum_tmp=0
        for item in self.portfolio.keys():
            price=universe.get_price_in_currency(item,t,'CAD')
            #price=universe.get_security(item).price[t]
            amount=self.portfolio[item]
            sum_tmp=sum_tmp+price*amount
        
        return sum_tmp

#    def addPortfolio(self, other):
#        """
#        Add two portfolios.
#        :param other: Portofolio
#        :return: Portfolio
#        """
#        self.portfolio=other.portfolio
#        print(list(other.all_portfolios.keys())[0])
#        self.all_portfolios[list(other.all_portfolios.keys())[0]]=other
#        print(self.all_portfolios['2014-04-01'].portfolio)
    # we may also need some methods to do portfolio level risk analysis