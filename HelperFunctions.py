import pandas as pd
from datetime import datetime
import numpy as np

""" Helper function"""


def fill_missing_data_business(data_series, start_date, end_date,freq='BM'):
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
    if start_date == end_date:
        if pd.date_range(start_date, end_date, freq=freq).shape[0] == 0:
            start_date = datetime.strftime(pd.date_range(end=start_date, freq='B', periods=1)[0], '%Y-%m-%d')

    if start_date=='2019-06-01':
        start_date='2019-05-31'
        end_date='2019-05-31'
        
    if isinstance(end_date, int):
        inter_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
                       pd.date_range(start=start_date, freq=freq, periods=end_date)]
        result = pd.Series(data_series.reindex(inter_dates, method='ffill').loc[:].astype(float))
    elif isinstance(end_date, str):
        inter_dates = [datetime.strftime(item, '%Y-%m-%d') for item in
                       pd.date_range(start=start_date, freq=freq, end=end_date)]
        result = pd.Series(data_series.reindex(inter_dates, method='ffill').loc[:].astype(float))
    else:
        print("input end_date as string or window size as int")
        return
    return result