import json
from datetime import datetime
import pandas as pd
from django.apps import apps

from app import constants
from app.adapters import nixtla_adapter
from app.models import Chart1DForecastTimeGPT


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
    if to_date > constants.current_date_without_time():
        raise ValueError("Last date cannot be greater than current date")
    print(
        "Forecast 1d chart from {} to {}, current_date {}".format(
            from_date, to_date, constants.current_date_without_time()
        )
    )
    if to_date == constants.current_date_without_time():
        force_update = True
        print("Force update forecast 1d chart from {} to {}".format(from_date, to_date))

    data = apps.get_app_config("app").get_btc_all_data_1d()

    # Convert 'from_date' and 'to_date' strings to pd.Timestamp for comparison
    from_date_pd = pd.to_datetime(from_date)
    to_date_pd = pd.to_datetime(to_date)
    range_data = data[(data["date"] >= from_date_pd) & (data["date"] <= to_date_pd)]
    more_date = data[(data["date"] > to_date_pd)].head(7)
    range_data_for_ploting = range_data if len(range_data) < 30 else range_data.tail(30)
    range_data_for_ploting = pd.concat([range_data_for_ploting, more_date])
    
    plot_dates = range_data_for_ploting['date'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
    plot_close_values = range_data_for_ploting['close'].tolist()

    if not force_update:
        cached_data = get_forecast_1d_from_db(from_date, to_date)
        if cached_data:
            return (
                cached_data.get_dates(),
                cached_data.get_values(),
                cached_data.get_high_90s(),
                cached_data.get_low_90s(),
                plot_dates,
                plot_close_values,
            )

    
    result = nixtla_adapter.forecast(
        apps.get_app_config("app").get_nixtla_client(),
        range_data,
    )
    print(result)
    dates = []
    for date in result["date"]:
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
    upsert_forecast_1d_in_db(from_date, to_date, dates, values, high_values, low_values)


    return dates, values, high_values, low_values, plot_dates, plot_close_values


def get_forecast_1d_from_db(from_date, to_date):
    return Chart1DForecastTimeGPT.objects.filter(
        from_date=from_date, to_date=to_date
    ).first()


def upsert_forecast_1d_in_db(from_date, to_date, dates, values, high_90s, low_90s):
    if Chart1DForecastTimeGPT.objects.filter(
        from_date=from_date, to_date=to_date
    ).exists():
        Chart1DForecastTimeGPT.objects.filter(
            from_date=from_date, to_date=to_date
        ).update(
            dates=json.dumps(dates),
            values=json.dumps(values),
            high_90s=json.dumps(high_90s),
            low_90s=json.dumps(low_90s),
        )
        print(f"Updated forecast 1d chart from {from_date} to {to_date} in DB")
        return
    Chart1DForecastTimeGPT.objects.create(
        from_date=from_date,
        to_date=to_date,
        dates=json.dumps(dates),
        values=json.dumps(values),
        high_90s=json.dumps(high_90s),
        low_90s=json.dumps(low_90s),
    )
    print(f"Stored forecast 1d chart from {from_date} to {to_date} in DB")
