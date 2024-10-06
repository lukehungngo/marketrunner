import traceback

from django.core.management import BaseCommand

from app.adapters import yahoo_finance_adapter
from app.models import Char1DMarketData


class Command(BaseCommand):
    help = "Store all btc data"

    def handle(self, *args, **kwargs):
        try:
            result = yahoo_finance_adapter.get_all_raw_data()
            # process and store all data
            data = []
            print(result.tail(1)["Date"].dt.strftime("%Y-%m-%d %H:%M:%S"))
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
            print("Data length: ", len(data))
            Char1DMarketData.objects.bulk_create(data)
        except Exception as e:
            print(str(e), traceback.format_exc())
