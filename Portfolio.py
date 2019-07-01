from registerUniverse import register_universe_main
# global variable
global universe
universe = register_universe_main()

class Portfolio:
    """ the portfolio with with weights and assets with other operations
    """

    def __init__(self, instrumentsNWeights, totalInvest):
        """
        Initialize the portfolio with tuple of instruments and the corresponding
        weights.

        public attribute
        :param instrumentsNWeights: dict[str] -> float
        :param totalInvest: float
        total amount of USD used in this portfolio investment
        """
        # add all necessary attributes here which link to portfolio and
        # will be tracked.
        self.portfolio = instrumentsNWeights
        self.totalInvest = totalInvest

    def getPortfolioValue(self, t):
        """
        Return the portfolio value at time t
        :return: float
        """
        pass


    def addPortfolio(self, other):
        """
        Add two portfolios.
        :param other: Portofolio
        :return: Portfolio
        """
        pass

    # we may also need some methods to do portfolio level risk analysis