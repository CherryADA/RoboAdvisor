import pandas as pd
import numpy as np
from scipy.optimize import fmin
from scipy.stats import norm
from dateutil.relativedelta import relativedelta


def get_implied_vol(optionPrice, S0, r, K, T, isCall):
    """
    Get the implied vol
    :param optionPrice:
    :param S0:
    :param r:
    :param K:
    :param T:
    :param isCall:
    :return:
    """
    def price_discrepancy(sigma):
        def d1(sigma):
            return (np.log(S0 / K) + (sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))

        def d2(sigma):
            return (d1(sigma) - sigma * np.sqrt(T))

        def black_scholes(sigma):
            if isCall:
                return S0 * norm.cdf(d1(sigma)) - K * norm.cdf(d2(sigma))
            else:
                return -S0 * norm.cdf(-d1(sigma)) + K * norm.cdf(-d2(sigma))

        return (black_scholes(sigma) - optionPrice) ** 2

    vol = fmin(price_discrepancy, np.array([0.1]))
    return vol


def get_time_to_maturity(t, T):
    diff = relativedelta(T, t)
    result = diff.years + diff.months / 12 + diff.days / 252
    return result

def get_implied_vol_series(optionPrice_series, underlyingAsset_series, interest_rate, K, T, date_series, isCall):
    if None in [underlyingAsset_series, interest_rate, K, T, isCall]:
        print("option information is not completed")
        return None
    if (len(optionPrice_series) != len(underlyingAsset_series)):
        # we must have the same length of these provided series
        print("Input size of option price, underlying asset price and interest rate should be the same")
        return None
    results = [get_implied_vol(optionPrice_series[i], underlyingAsset_series[i],
                               interest_rate, K, get_time_to_maturity(date_series[i], T), isCall)[0] for i in
               range(len(optionPrice_series))]
    return pd.Series(results)
