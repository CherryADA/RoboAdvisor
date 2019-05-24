import InstrumentUniverse
class Admin:
    """ Admin should be our main robo advisor.
    Admin is responsible for manage instrument universe, users, and suggest portfolio to each users

    """

    def __init__(self):
        """
        Initialize the Admin.
        """
        self.intrumentUniverse = InstrumentUniverse()
        # use dictionary of userID and User in to admin manged user list
        # in real world, one admin will manage many users
        # although in our project, we may only have one user but we can
        # still make it generic
        self.users = {}

    def addUser(self, user):
        """
        Add user into admin management user pool
        :param user: User
        :return:
        """
    def suggestPortfolio(self, userID):
        """
        suggest portfolio based on the user (indentify by userID)'s information
        and risk appetite, etc. Note that this userID must exist as a key in
        self.users

        :param userID: int
        :return: Portfolio
        """

    # other methods