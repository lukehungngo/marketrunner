import traceback

from pandas import DataFrame
import pandas as pd

from app import constants
from app.adapters import yahoo_finance_adapter
from app.models import Char1DMarketData
from typing import TypedDict, Optional


# Define the structure of the DataFrame
class MarketDataRow(TypedDict):
    date: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float]  # Volume can be None, so we use Optional
    count: Optional[int]  # Count can also be None


# @dev Get 1D market data from the database
# @return DataFrame: 1D market data from lowest date to current date
def get_1d_market_data() -> DataFrame:
    query = (
        Char1DMarketData.objects.all()
        .order_by("date")
        .values("date", "open", "high", "low", "close", "volume", "count")
    )
    current_date = constants.current_date_without_time()
    if not query.exists():
        result = yahoo_finance_adapter.get_all_raw_data()
        # process and store all data
        data = []
        for index, row in result.iterrows():
            data.append(
                Char1DMarketData(
                    date=row["Date"].strftime("%Y-%m-%d %H:%M:%S"),
                    open=row["Open"],
                    high=row["High"],
                    low=row["Low"],
                    close=row["Close"],
                    volume=row["Volume"],
                )
            )
        if len(data) > 0:
            try:
                Char1DMarketData.objects.bulk_create(data)
                print(
                    "Insert new chart 1d market data, {} days from {}, to {}".format(
                        len(data), data[0].date, data[-1].date
                    )
                )
            except Exception as e:
                print(
                    "get_1d_market_data|init|bulk_create|error={}|trace_back={}".format(
                        str(e),
                        traceback.format_exc(),
                    )
                )
                raise e
        result.rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            },
            inplace=True,
        )
        print("No data in database, store all data", result.head(), "\n", result.tail())
        return result

    last_date = list(query)[-1]["date"]
    if last_date == current_date:
        df = pd.DataFrame(list(query))
        df["date"] = pd.to_datetime(
            df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        )
        print("No new data to store", df.head(), "\n", df.tail())
        return df

    # find and import new data from the last date to the current date
    result = yahoo_finance_adapter.get_all_raw_data()
    new_data = []
    new_data_df = []
    for index, row in result.iterrows():
        if row["Date"].strftime("%Y-%m-%d %H:%M:%S") < last_date:
            continue
        if row["Date"].strftime("%Y-%m-%d %H:%M:%S") == last_date:
            Char1DMarketData.objects.filter(date=last_date).update(
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
            )
        new_data.append(
            Char1DMarketData(
                date=row["Date"].strftime("%Y-%m-%d %H:%M:%S"),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
            )
        )
        new_data_df.append(
            {
                "date": row["Date"],
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"],
            }
        )
    if len(new_data) > 0:
        try:
            Char1DMarketData.objects.bulk_create(new_data)
            print(
                "Insert new chart 1d market data, {} days from {}, to {}".format(
                    len(new_data), new_data[0].date, new_data[-1].date
                )
            )
        except Exception as e:
            print(
                "get_1d_market_data|insert_new|bulk_create|error={}|trace_back={}".format(
                    str(e),
                    traceback.format_exc(),
                )
            )
            raise e
    # assembly return data using query and new_data
    df = pd.DataFrame(list(query) + new_data_df)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    return df
