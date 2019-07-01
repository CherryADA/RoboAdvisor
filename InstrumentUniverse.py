import pandas as pd
import numpy as np
from datetime import datetime
import statsmodels.api as sm
from statsmodels.api import OLS

class InstrumentUniverse:
    """ A factory which collects all possible assets in our universe
    It should consist equities, bonds, options and ETFs. It should be a collection of Asset.
    """

    def __init__(self):
        """
        Initialize the AssetsUniverse with all possible assets filled in.

        private attribute
        :param _universe: the dictionary of assets
        :param _riskFactors: the dictionary of pd.dataFrame
        :param _fx: pd.dataFrame
        """
        self._universe = {} # we need to fill up this universe when we get data
        self._riskFactors = {}
        self._fx = 0 # will fill the fx dataframe

    def addInstrument(self, newInstrument):
        """
        Add new instrument into instument universe
        :param newInstrument: Instument
        :nreturn
        """
        self._universe[newInstrument.ticker] = newInstrument

    def add_riskFactor_dataFrame(self, riskFactor_dataFrame, target):
        """

        :param riskFactor_dataFrame:
        :return:
        """
        self._riskFactors[target] = riskFactor_dataFrame


    def add_fx(self, fx_df):
        """
        Add new instrument into instument universe
        :param newInstrument: Instument
        :nreturn
        """
        self._fx = fx_df

    def show_registered_securities(self, assetCurrency="all"):
        """
        :nreturn:
        """
        r_string = "Securities:\n"
        if assetCurrency == "all":
            for inst_ticker in self._universe:
                r_string = r_string + inst_ticker + "\n"

            print("Total registered " + str(len(self._universe)) + " securities\n")
            print(r_string)
        else:
            n = 0
            for inst_ticker in self._universe:
                if self._universe[inst_ticker].get_type_RM() == assetCurrency:
                    r_string = r_string + inst_ticker + "\n"
                    n += 1

            print("Total registered " + str(n) + " " + assetCurrency + " securities\n")
            print(r_string)


    def show_registered_riskFactors(self):
        """
        :nreturn:
        """
        print("riskFactors for asset class: \n")
        for target in self._riskFactors:
            print(target)
        print("has been registered!")
        # n = 0
        # for inst_ticker in self._riskFactors:
        #     print("for " + inst_ticker)
        #     for item in self._riskFactors[inst_ticker]:
        #         n += 1
        #         print(item.ticker)
        #
        # print("Total registered " + str(n) + " risk factors")

    def get_fx_file(self):
        """
        Return the fx dataFrame.

        :return pd.DataFrame
        """
        return self._fx

    def get_security_universe(self):
        """
        Return all registered securities' dictionary
        :return: dict[str] -> Instrument
        """
        return self._universe

    def get_riskFactor_universe(self):
        """
        Return all registered risk fator's dictionary
        :return:  dict[str] -> Instrument
        """
        return self._riskFactors

    def get_security(self, ticker):
        """

        :param ticker:
        :return:
        """
        try:
            return self._universe[ticker]
        except KeyError as error:
            print(ticker + "doesn't exist")
            return np.nan

    def get_riskFactor(self, target):
        """

        :param ticker:
        :return:
        """
        try:
            return self._riskFactors[target]
        except KeyError as error:
            print(error)
            return np.nan

    def get_asset_class(self, className):
        """
        Get the collection of existing assets in class as indicated in className.
        :param className: string which in one of the {"equity","bond", "option", "ETF"}
        :return: list of Asset
        """
        return []

    def get_price_in_currency(self, ticker, t, target_currency):
        """
        Get the price of the security ticker in currency target_currency at date t.
        :param ticker: str
        :param date: str
        :param target_currency: str
        :return: float
        """
        from_currency = self.get_security(ticker).currency
        if from_currency == target_currency:
            return self.get_security(ticker).get_the_price(t)
        elif target_currency == "USD":
            # straight converting
            fx_rate_t = self._fx[[from_currency + "USD=X"]].loc[t]
            # try:
            #     fx_rate_t = self._fx[[from_currency+"USD=X"]].iloc[t]
            # except:
            #     print("couldn't find the exchange rate from " + from_currency + " to " + target_currency + " at time " +
            #           t)
            #     return

            return self.get_security(ticker).get_the_price(t) * float(fx_rate_t)
        else:
            # triangle converting
            try:
                fx_rate_t1 = self._fx[[from_currency + "USD=X"]].loc[t]
                fx_rate_t2 = 1/float(self._fx[[target_currency + "USD=X"]].loc[t])
            except:
                print("couldn't find the exchange rate from " + from_currency + " to " + target_currency + " at time " +
                      t)
                return

            return self.get_security(ticker).get_the_price(t) * float(fx_rate_t1) * fx_rate_t2

    # fit factor model and perform tests.
    def fitFactorModel(self, ticker, start_date, window_size):
        """ Fit the factor model with factors indicated by certain factor list in list_of_factor_set determined by item's
        decription on start_date - window_size to start_date. Test is also performed from start_date to start_date +
        test_window_size.

        :param item: str
               ticker of ETFs, Equities or volatility
        :param sec_returns_historical: DataFrame
        :param is_vol: Bool
               True if the input item is a volatility not return
        :param description_df: DataFrame of the description table
        :param list_of_factor_set: list of dataFrame
               must follow the order, [US, Global, Vols]
        :param start_date: string of the date form "%Y-%m-%d"
               the date that we will train model back with window_size and test forward with test_window_size
        :param window_size: int
        :param test_window_size: int
        :return: [OLS result, series, series, str]
        """
        if ticker not in self._universe:
            print(ticker + " cannot find in the universe")
            return
        else:
            instru = self._universe[ticker]
            Instru_type = instru.get_type_RM()
            if Instru_type not in self._riskFactors:
                print("risk factor for " + Instru_type + " hasn't been resisted yet!")
                return
            FF_rf_dec = self._riskFactors[Instru_type]

        # determine the period of training set and testing set
        regr_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
                      pd.date_range(end=start_date, freq='B', periods=window_size)]
        # test_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
        #               pd.date_range(start=start_date, freq='B', periods=test_window_size)]


        # select columns here
        if "Equity" in Instru_type:
            factor_names = FF_rf_dec.columns[6:len(FF_rf_dec.columns)]
        elif Instru_type == "ETF:FixedIncome":
            factor_names = FF_rf_dec.columns[0:len(FF_rf_dec.columns)-1]
        else:
            print("not implemented yet!!")
            return

        Y_train = pd.DataFrame(
            instru.compute_ret(True).reindex(
                regr_dates, method='ffill'
            ).loc[:].astype(float) - FF_rf_dec.reindex(
                regr_dates, method='ffill').loc[:, 'RF'].astype(float)
        )
        X_train = FF_rf_dec.reindex(regr_dates, method='ffill').loc[:, factor_names].astype(float)
        X2_train = sm.add_constant(X_train).astype(float)
        regr = OLS(Y_train, X2_train, missing='drop')
        results = regr.fit()
        #
        # Y_test = pd.DataFrame(
        #     sec_returns_historical.reindex(
        #         test_dates, method='ffill'
        #     ).loc[:, item].astype(float) - FF_rf_dec.reindex(
        #         test_dates, method='ffill').loc[:, 'RF'].astype(float)
        # )
        # X_test = FF_rf_dec.reindex(test_dates, method='ffill').loc[:, factor_names].astype(float)
        # X2_test = sm.add_constant(X_test).astype(float)
        # # Make predictions using the testing set
        # Y_pred = results.predict(X2_test)

        return results
