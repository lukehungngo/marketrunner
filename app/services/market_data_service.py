from pandas import DataFrame
import pandas as pd

from marketrunner.app import constants
from marketrunner.app.adapters import yahoo_finance_adapter
from marketrunner.app.models import Char1DMarketData


# ['Open', 'High', 'Low', 'Close', 'Volume']
def get_1d_market_data() -> DataFrame:
    query = Char1DMarketData.objects.filter().order_by("-date")
    current_date = constants.datetime_to_string()
    if not query.exists():
        result = yahoo_finance_adapter.get_all_raw_data()
        # process and store all data
        data = []
        for index, row in result.iterrows():
            data.append(
                Char1DMarketData(
                    date=row["Date"].dt.strftime("%Y-%m-%d %H:%M:%S"),
                    open=row["Open"],
                    high=row["High"],
                    low=row["Low"],
                    close=row["Close"],
                    volume=row["Volume"],
                )
            )
        Char1DMarketData.objects.bulk_create(data, ignore_conflicts=True)
        return result

    # only store updated data
    last_date = query[0].date
    if last_date == current_date:
        return query
