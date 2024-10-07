import json

from django.conf import settings
from django.db import models


class Char1DMarketData(models.Model):
    class Meta:
        db_table = settings.DB_PREFIX + "_chart_1d_market_data"

    date = models.CharField(max_length=64, db_index=True)  # Date of the data
    open = models.FloatField()  # Open price
    high = models.FloatField()  # High price
    low = models.FloatField()  # Low price
    close = models.FloatField()  # Close price
    volume = models.FloatField(null=True, default=None)  # Volume
    count = models.IntegerField(null=True, default=None)  # Number of trades

    def __str__(self):
        return f"Market Data 1D on {self.date}"


class Chart1DForecastTimeGPT(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["from_date", "to_date"]),
        ]
        db_table = settings.DB_PREFIX + "_chart_1d_forecast_time_gpt"

    from_date = models.CharField(max_length=64)  # Date of the forecast
    to_date = models.CharField(max_length=64)  # Date of the forecast
    dates = models.TextField(null=True)  # Forecasted date
    values = models.TextField(null=True)  # Forecasted value
    high_90s = models.TextField(null=True)  # Upper confidence bound (hi-90)
    low_90s = models.TextField(null=True)  # Lower confidence bound (lo-90)

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Timestamp when data is cached

    def get_dates(self):
        return json.loads(self.dates) if self.dates else []

    def get_values(self):
        return json.loads(self.values) if self.values else []

    def get_high_90s(self):
        return json.loads(self.high_90s) if self.high_90s else []

    def get_low_90s(self):
        return json.loads(self.low_90s) if self.low_90s else []

    def __str__(self):
        return f"Forecast Char 1D from {self.from_date} to {self.to_date}"
