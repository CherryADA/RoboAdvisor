class InstrumentModel:
    """ for individual instrument, we can build pricing model/risk model here and do scenario
    analysis.
    """

    def __init__(self, instrument, linearModelCoeffs):
        """
        Initialize the instrumentModel
        :param instrument:
        :param linearModelCoeffs: fitted linear model coeffs
        """
        self.instrument = instrument

        self._linearModelCoeffs = linearModelCoeffs;


