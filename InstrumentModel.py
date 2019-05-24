class InstrumentModel:
    """ for individual instrument, we can build pricing model/risk model here and do scenario
    analysis.
    """

    def __init__(self, instrument, riskFactorLists):
        """
        Initialize the instrumentModel
        :param instrument:
        :param riskFactorLists: list of risk factors
        """
        self.instrument = instrument
        self.riskFactorLists = riskFactorLists
        self._linearModelCoeffs = [];
