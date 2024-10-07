from datetime import datetime, timedelta

from django.apps import AppConfig
from django.conf import settings
from nixtla import NixtlaClient

from . import constants
from .adapters import nixtla_adapter, yahoo_finance_adapter


class ForecastappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    BTC_ALL_DATA_1D = []
    LAST_BTC_UPDATE_DATETIME = None
    NIXTLA_CLIENT = None

    def ready(self):
        # Custom initialization code here
        current_date = constants.current_date_without_time()
        nixtlatl_api_key = getattr(settings, "NIXTLA_API_KEY", None)
        if nixtlatl_api_key is None:
            raise ValueError("NIXTLATL_API_KEY is not set in settings.py")
        self.NIXTLA_CLIENT = NixtlaClient(api_key=settings.NIXTLA_API_KEY)

    def get_nixtla_client(self):
        if self.NIXTLA_CLIENT is None:
            raise ValueError("Nixtla client is not initialized!")
        return self.NIXTLA_CLIENT

    def get_btc_all_data_1d(self):
        from .services import market_data_service

        current_datetime = constants.get_current_datetime()
        # if not update today yet or just start the server
        # or last update more than 10 minutes
        if self.LAST_BTC_UPDATE_DATETIME is None or (
                datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
                - datetime.strptime(self.LAST_BTC_UPDATE_DATETIME, "%Y-%m-%d %H:%M:%S")
                > timedelta(minutes=10)
        ):
            self.BTC_ALL_DATA_1D = (
                market_data_service.get_1d_market_data().reset_index()
            )
            self.LAST_BTC_UPDATE_DATETIME = current_datetime
            print(
                "Date {}, BTC_ALL_DATA_1D loaded!, loaded data of {} dates from {} to {}".format(
                    current_datetime,
                    len(self.BTC_ALL_DATA_1D),
                    self.BTC_ALL_DATA_1D["date"].min(),
                    self.BTC_ALL_DATA_1D["date"].max(),
                )
            )
        return self.BTC_ALL_DATA_1D
