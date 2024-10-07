from datetime import datetime

from django.apps import AppConfig
from django.conf import settings
from nixtla import NixtlaClient

from . import constants
from .adapters import nixtla_adapter, yahoo_finance_adapter


class ForecastappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    BTC_ALL_DATA_1D = []
    LAST_BTC_UPDATE_DATE = None
    NIXTLA_CLIENT = None

    def ready(self):
        # Custom initialization code here
        current_date = constants.datetime_to_string()
        nixtlatl_api_key = getattr(settings, "NIXTLA_API_KEY", None)
        if nixtlatl_api_key is None:
            raise ValueError("NIXTLATL_API_KEY is not set in settings.py")
        self.NIXTLA_CLIENT = NixtlaClient(api_key=settings.NIXTLA_API_KEY)
        self.BTC_ALL_DATA_1D = yahoo_finance_adapter.get_all_raw_data("BTC-USD")
        self.LAST_BTC_UPDATE_DATE = current_date
        print(
            "Date {}, BTC_ALL_DATA_1D initialized!, loaded data of {} dates from {} to {}".format(
                current_date,
                len(self.BTC_ALL_DATA_1D),
                self.BTC_ALL_DATA_1D["Date"].min(),
                self.BTC_ALL_DATA_1D["Date"].max(),
            )
        )

    def get_nixtla_client(self):
        """
        Getter for accessing the initialized NIXTLA_CLIENT.
        """
        if self.NIXTLA_CLIENT is None:
            raise ValueError("Nixtla client is not initialized!")
        return self.NIXTLA_CLIENT

    def get_btc_all_data_1d(self):
        """
        Getter for accessing the initialized BTC_ALL_DATA_1D.
        """
        current_date = constants.datetime_to_string()
        if current_date != self.LAST_BTC_UPDATE_DATE:
            self.BTC_ALL_DATA_1D = yahoo_finance_adapter.get_all_raw_data("BTC-USD")
            self.LAST_BTC_UPDATE_DATE = current_date
            print(
                "Date {}, BTC_ALL_DATA_1D updated!, loaded data of {} dates from {} to {}".format(
                    current_date,
                    len(self.BTC_ALL_DATA_1D),
                    self.BTC_ALL_DATA_1D["Date"].min(),
                    self.BTC_ALL_DATA_1D["Date"].max(),
                )
            )
        return self.BTC_ALL_DATA_1D
