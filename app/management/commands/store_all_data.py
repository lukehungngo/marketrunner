import traceback

from django.core.management import BaseCommand

from app import services
from app.adapters import yahoo_finance_adapter
from app.models import Char1DMarketData
from app.services import market_data_service


class Command(BaseCommand):
    help = "Store all btc data"

    def handle(self, *args, **kwargs):
        try:
            # result = market_data_service.get_1d_market_data()
            result = yahoo_finance_adapter.get_all_raw_data()
            print("result", result.tail())
            print("result", result.head())
        except Exception as e:
            print(str(e), traceback.format_exc())
