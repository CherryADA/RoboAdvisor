import pandas as pd
import numpy as np
from datetime import datetime
import statsmodels.api as sm
from statsmodels.api import OLS
from HelperFunctions import fill_missing_data_business

class InstrumentUniverse:
    """ A factory which collects all possible assets in our universe
    It should consist equities, bonds, options and ETFs. It should be a collection of Asset.
    """

    def __init__(self):
        """
        Initialize the AssetsUniverse with all possible assets filled in.

        private attribute
        :param _universe: the dictionary of assets
        :param _riskFactors_files: the dictionary of pd.dataFrame
        :param _fx: pd.dataFrame
        :param _risk_factors_list
        """
        self._universe = {} # we need to fill up this universe when we get data
        self._riskFactors_files = {}
        self._riskFactors = {}
        self._fx = 0 # will fill the fx dataFrame

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
        self._riskFactors_files[target] = riskFactor_dataFrame

    def add_risk_factor(self, riskFactor):
        """
        Add instrument risk factor into universe, which stores in self._riskFactors
        :param riskFactor: RiskFactor
        :return: nan
        """
        self._riskFactors[riskFactor.ticker] = riskFactor

    def add_fx(self, fx_df):
        """
        Add new instrument into instument universe
        :param newInstrument: Instument
        :nreturn
        """
        self._fx = fx_df

    def get_risk_factors(self):
        return self._riskFactors

    def get_tickers_in_asset_class(self, assetCurrency):
        """
        Get the collection of existing assets in class as indicated in className.
        :param assetCurrency: string which in one of the {  Equity:CAD
                                                        Equity:AUD
                                                        Equity:EUR
                                                        Equity:JPY
                                                        Equity:USD
                                                        ETF:FixedIncome
                                                        VOL:US}
        :return: list of tikcker
        """
        result = []
        if assetCurrency == "all":
            for inst_ticker in self._universe:
                result.append(inst_ticker)
        else:
            for inst_ticker in self._universe:
                if self._universe[inst_ticker].get_type_RM() == assetCurrency:
                    result.append(inst_ticker)
        return result

    """The following two functions are for the purpose of testing -- no return value """
    def show_registered_securities(self, assetCurrency="all"):
        """
        :nreturn:
        """
        r_string = "Securities:\n"
        inst_l = self.get_tickers_in_asset_class(assetCurrency)
        for inst_ticker in inst_l:
            r_string = r_string + inst_ticker + "\n"

        print("Total registered " + str(len(inst_l)) + " securities\n")
        print(r_string)

    def show_registered_riskFactors_files(self):
        """
        :nreturn:
        """
        print("riskFactors for asset class: \n")
        for target in self._riskFactors_files:
            print(target)
        print("has been registered!")
        # n = 0
        # for inst_ticker in self._riskFactors_files:
        #     print("for " + inst_ticker)
        #     for item in self._riskFactors_files[inst_ticker]:
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
        return self._riskFactors_files

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

    def get_risk_factor_files(self, target):
        """

        :param ticker:
        :return:
        """
        try:
            return self._riskFactors_files[target]
        except KeyError as error:
            print(error)
            return np.nan

    def get_price_in_currency(self, ticker, t, target_currency):
        """
        Get the price of the security ticker in currency target_currency at date t.
        :param ticker: str
        :param date: str
        :param target_currency: str
        :return: float
        """
        instrument = self.get_security(ticker)
        from_currency = instrument.currency

        if from_currency == target_currency:
            return self.get_security(ticker).get_the_price(t)

        full_fx_rate_target = self._fx[[target_currency+"USD=X"]]
        fx_rate_target = pd.DataFrame(full_fx_rate_target.reindex(instrument.price.index.tolist(), method='ffill').loc[:].astype(float))
        if from_currency == "USD":
            try:
                fx_rate_t = 1/fx_rate_target.loc[t]
            except:
                print("couldn't find the exchange rate from " + from_currency + " to " + target_currency + " at time " +
                      t)
                return
            return self.get_security(ticker).get_the_price(t) * float(fx_rate_t)

        full_fx_rate_from = self._fx[[from_currency+"USD=X"]]
        fx_rate_from = pd.DataFrame(full_fx_rate_from.reindex(instrument.price.index.tolist(), method='ffill').loc[:].astype(float))
        if target_currency == "USD":
            # straight converting
            try:
                fx_rate_t = fx_rate_from.loc[t]
            except:
                print("couldn't find the exchange rate from " + from_currency + " to " + target_currency + " at time " +
                      t)
                return

            return self.get_security(ticker).get_the_price(t) * float(fx_rate_t)
        else:
            # triangle converting
            try:
                fx_rate_t1 = fx_rate_from.loc[t]
                fx_rate_t2 = 1/float(fx_rate_target.loc[t])
            except:
                print("couldn't find the exchange rate from " + from_currency + " to " + target_currency + " at time " +
                      t)
                return

            return self.get_security(ticker).get_the_price(t) * float(fx_rate_t1) * fx_rate_t2

    # fit factor model
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
            if Instru_type not in self._riskFactors_files:
                print("risk factor for " + Instru_type + " hasn't been resisted yet!")
                return
            FF_rf_dec = self._riskFactors_files[Instru_type]

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
        ) # change to False if we want to fit the simple return

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

    ## Get all risk factors' covariance and mean
    ## helper function

    def get_risk_factors_cov(self, start_date, end_date,freq='BM',annualize=True):
        """
        Return the covariance matrix of all risk factors between the time start_date and end_date.
        :param start_date: str
        :param end_date: str
        :param freq: str (only 'BM' or 'B')
        :return:
        """
        result_df = pd.DataFrame()
        factor_tickers = self._riskFactors.keys()
        #print(factor_tickers)
        for k in factor_tickers:
            result_df[k] = fill_missing_data_business(self._riskFactors[k].price, start_date, end_date,freq)
        #cov_df = pd.DataFrame(np.cov(result_df), index=factor_tickers, columns=factor_tickers)
        
        out=result_df.cov()
        if annualize:
            if freq=='BM':
                ann_fac=12
            elif freq=='B':
                ann_fac=252
            else:
                print('Frequency string should be only "BM" or "B"')
                return
            out=out.multiply(ann_fac)
        return out

    def get_risk_factors_mean(self, start_date, end_date,freq='BM',annualize=True):
        """
        Return the mean of all risk factors between the time start_date and end_date.
        :param start_date: str
        :param end_date: str
        :return:
        """
        result_df = pd.DataFrame()
        for k in self._riskFactors:
            result_df[k] = fill_missing_data_business(self._riskFactors[k].price, start_date, end_date,freq)
        
        out=result_df.mean()
        if annualize:
            if freq=='BM':
                ann_fac=12
            elif freq=='B':
                ann_fac=252
            else:
                print('Frequency string should be only "BM" or "B"')
                return
            out=out.multiply(ann_fac)
        return out