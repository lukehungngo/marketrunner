import json
from datetime import datetime
import pandas as pd
from django.apps import apps

from . import constants
from .adapter import nixtla_adapter
from .models import Chart1DForecastTimeGPT


def forecast_btc_from_to(from_date=None, to_date=None, force_update=False):
    if not from_date:
        from_date = constants.DEFAULT_BTC_FROM_DATE
    from_date = constants.check_and_convert_date_format(from_date)
    if not to_date:
        to_date = (
            datetime.now()
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
    to_date = constants.check_and_convert_date_format(to_date)

    if not force_update:
        cached_data = get_forecast_1d_from_db(from_date, to_date)
        if cached_data:
            return (
                cached_data.get_dates(),
                cached_data.get_values(),
                cached_data.get_high_90s(),
                cached_data.get_low_90s(),
            )

    data = apps.get_app_config("app").get_btc_all_data_1d()

    # Convert 'from_date' and 'to_date' strings to pd.Timestamp for comparison
    from_date_pd = pd.to_datetime(from_date)
    to_date_pd = pd.to_datetime(to_date)
    range_data = data[(data["Date"] >= from_date_pd) & (data["Date"] <= to_date_pd)]
    result = nixtla_adapter.forecast(
        apps.get_app_config("app").get_nixtla_client(),
        range_data,
    )
    print(result)
    dates = []
    for date in result["Date"]:
        dates.append(date.strftime("%Y-%m-%d %H:%M:%S"))
    values = []
    for value in result["TimeGPT"]:
        values.append(value)
    high_values = []
    for value in result["TimeGPT-hi-90"]:
        high_values.append(value)
    low_values = []
    for value in result["TimeGPT-lo-90"]:
        low_values.append(value)

    # store as cached
    store_forecast_1d_in_db(from_date, to_date, dates, values, high_values, low_values)

    return dates, values, high_values, low_values


def get_forecast_1d_from_db(from_date, to_date):
    return Chart1DForecastTimeGPT.objects.filter(
        from_date=from_date, to_date=to_date
    ).first()


def store_forecast_1d_in_db(from_date, to_date, dates, values, high_90s, low_90s):
    Chart1DForecastTimeGPT.objects.create(
        from_date=from_date,
        to_date=to_date,
        dates=json.dumps(dates),
        values=json.dumps(values),
        high_90s=json.dumps(high_90s),
        low_90s=json.dumps(low_90s),
    )
    print(f"Stored forecast 1d chart from {from_date} to {to_date} in DB")
