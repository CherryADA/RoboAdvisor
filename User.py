class User:
    """ User contains all his/her information, risk appetite and other useful input.
    Also, this is the user end engine where can perform any desired action.

    User should have attribute to store the portfolio at discrete time
    """

    def __init__(self, userID, riskAppetite):
        """
        Initialize the user
        """
        self.userID = userID
        self.riskAppetite = riskAppetite
        self.accountAmount = 0 #initial amount should be zero
        self.portfolioOverTime = {} # use dictionary to record the portfolio hold at each time t
        # currentPortfolio store the current position the user current hold.
        self.currentPortfolio = None

    # ===== then we could add any useful methods here ========
    def changeRiskAppetite(self, newRiskAppeite):
        self.riskAppetite = newRiskAppeite

    