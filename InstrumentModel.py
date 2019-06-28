class InstrumentModel:
    """ for individual instrument, we can build pricing model/risk model here and do scenario
    analysis.
    """

    def __init__(self, instrument, riskFactorDict):
        """
        Initialize the instrumentModel
        :param instrument:
        :param riskFactorLists: Dictionary of list risk factors
        """
        self.instrument = instrument
        self.riskFactors = riskFactorDict
        self._linearModelCoeffs = [];


# Testing
# Testing_Cherry