import pandas as pd
from datetime import datetime
import numpy as np

""" Helper function"""


def fill_missing_data_business(data_series, start_date, end_date):
    """
    Get the slice of prices from start_date and end_date. All the missing value will be
    filled by forward fill method.
    :param start_date: str
    :param end_date: str/int
    if input end_date is int, it indicates the window_size. Otherwise, it indicates
    the end_date of the index

    :return: pd.DateFrame
    """
    result = np.nan
    if isinstance(end_date, int):
        inter_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
                       pd.date_range(start=start_date, freq='B', periods=end_date)]
        result = pd.Series(data_series.reindex(inter_dates, method='ffill').loc[:].astype(float))
    elif isinstance(end_date, str):
        inter_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
                       pd.date_range(start=start_date, freq='B', end=end_date)]
        result = pd.Series(data_series.reindex(inter_dates, method='ffill').loc[:].astype(float))
    else:
        print("input end_date as string or window size as int")
        return
    return result