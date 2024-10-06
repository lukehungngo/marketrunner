import yfinance as yf
from pandas import DataFrame


def get_all_raw_data(ticker=None) -> DataFrame:
    if not ticker:
        ticker = "BTC-USD"

    data = yf.download(ticker)
    data = data.reset_index()
    # data as list of ['Open', 'High', 'Low', 'Close', 'Volume']
    return data
