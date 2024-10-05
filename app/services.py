from datetime import datetime
import pandas as pd
from django.apps import apps

from . import constants
from .adapter import nixtla_adapter


def forecast_btc_from_to(from_date=None, to_date=None):
    data = apps.get_app_config('app').get_btc_all_data()
    if not from_date:
        from_date = constants.DEFAULT_BTC_FROM_DATE
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")

    # Convert 'from_date' and 'to_date' strings to pd.Timestamp for comparison
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)

    range_data = data[(data['Date'] >= from_date) & (data['Date'] <= to_date)]

    result = nixtla_adapter.forecast(apps.get_app_config('app').get_nixtla_client(), range_data)
    dates = []
    for date in result['Date']:
        dates.append(date)
    values = []
    for value in result['TimeGPT']:
        values.append(value)

    return dates, values
