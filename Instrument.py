class Instrument:
    """ A Instrument is an abstract class, it's a parent class of
    Bond, Equity, Option, Future, ETF and risk factors so on.
    This should contains general parameters and methods among any asset classes.
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

# define all the child class here.
class Bond(Instrument):
    """

    """

    def __init__(self, couponRate, couponType, maturityDate, paymentFrequency, currency, type):
        """
        Initialize the Instrument
        """
        pass
