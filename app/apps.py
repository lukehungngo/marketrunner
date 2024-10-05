from django.apps import AppConfig
from django.conf import settings
from nixtla import NixtlaClient

from .adapter import nixtla_adapter


class ForecastappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    BTC_ALL_DATA = []
    NIXTLA_CLIENT = None

    def ready(self):
        # Custom initialization code here
        nixtlatl_api_key = getattr(settings, 'NIXTLA_API_KEY', None)
        if nixtlatl_api_key is None:
            raise ValueError("NIXTLATL_API_KEY is not set in settings.py")
        self.NIXTLA_CLIENT = NixtlaClient(api_key=settings.NIXTLA_API_KEY)
        self.BTC_ALL_DATA = nixtla_adapter.get_all_raw_data("BTC-USD")
        print("BTC_ALL_DATA initialized!, loaded data of {} dates from {} to {}".format(len(self.BTC_ALL_DATA),
                                                                                        self.BTC_ALL_DATA['Date'].min(),
                                                                                        self.BTC_ALL_DATA[
                                                                                            'Date'].max()))

    def get_nixtla_client(self):
        """
        Getter for accessing the initialized NIXTLA_CLIENT.
        """
        if self.NIXTLA_CLIENT is None:
            raise ValueError("Nixtla client is not initialized!")
        return self.NIXTLA_CLIENT

    def get_btc_all_data(self):
        """
        Getter for accessing the initialized BTC_ALL_DATA.
        """
        return self.BTC_ALL_DATA
