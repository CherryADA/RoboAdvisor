class InstrumentUniverse:
    """ A factory which collects all possible assets in our universe
    It should consist equities, bonds, options and ETFs. It should be a collection of Asset.
    """

    def __init__(self):
        """
        Initialize the AssetsUniverse with all possible assets filled in.

        private attribute
        :param _universe: the list of assets
        """
        self._universe = [] # we need to fill up this universe when we get data

    def getAssetClass(self, className):
        """
        Get the collection of existing assets in class as indicated in className.
        :param className: string which in one of the {"equity","bond", "option", "ETF"}
        :return: list of Asset
        """
        return []