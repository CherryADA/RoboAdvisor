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
        self._riskFactors = []

    def addInstrument(self, newInstrument):
        """
        Add new instrument into instument universe
        :param newInstrument: Instument
        :nreturn
        """
        # append the risk factor into risk factor list
        if newInstrument.get_type_RM == "Unknown":
            self._riskFactors.append(newInstrument)
        # else, append to security list
        else:
            self._universe.append(newInstrument)

    def show_registered_securities(self):
        """
        :nreturn:
        """
        r_string = "Securities:\n"
        for inst in self._universe:
            r_string = r_string + inst.ticker + "\n"

        print("Total registered " + str(len(self._universe)) + " securities\n")
        print(r_string)

    def show_registered_riskFactors(self):
        """
        :nreturn:
        """
        r_string = "riskFactors:\n"
        for inst in self._riskFactors:
            r_string = r_string + inst.ticker + "\n"

        print("Total registered " + str(len(self._riskFactors)) + " risk factors\n")
        print(r_string)

    def getAssetClass(self, className):
        """
        Get the collection of existing assets in class as indicated in className.
        :param className: string which in one of the {"equity","bond", "option", "ETF"}
        :return: list of Asset
        """
        return []