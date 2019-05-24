class Portfolio:
    """ the portfolio with with weights and assets with other operations
    """

    def __init__(self, instrumentsNWeights):
        """
        Initialize the portfolio with tuple of instruments and the corresponding
        weights.

        public attribute
        :param instrumentsNWeights: tuple (Instrument, weight)
        """
        # add all necessary attributes here which link to portfolio and
        # will be tracked.
        self.portfolio = instrumentsNWeights

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