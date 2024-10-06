import krakenex
from django.apps import apps
from django.core.management import BaseCommand
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Command(BaseCommand):
    help = "Runs Kraken Crawler"

    def handle(self, *args, **kwargs):
        pair = "XXBTZUSD"
        interval = 240
        # Get the API key from settings
        kraken = krakenex.API()
        response = kraken.query_public(
            "OHLC",
            {
                "pair": pair,
                "interval": interval,
                "since": 0,
            },
        )

        # Extract the relevant data from the response
        data = response["result"][pair]
        # Convert to DataFrame for easy handling
        df = pd.DataFrame(
            data,
            columns=[
                "Datetime",
                "Open",
                "High",
                "Low",
                "Close",
                "Vwap",
                "Volume",
                "Count",
            ],
        )

        # Convert Datetime to human-readable date format
        df["Datetime"] = pd.to_datetime(df["Datetime"], unit="s")
        print(df)
        # # Convert price data to numeric
        df[["Open", "High", "Low", "Close", "Volume"]] = df[
            ["Open", "High", "Low", "Close", "Volume"]
        ].astype(float)
        #
        # # Display the first few rows
        print(df.head(1)["Datetime"])
        print(df.tail(1))
        print(len(df))
        #
        nixtla_client = apps.get_app_config("app").get_nixtla_client()
        forecast_result = nixtla_client.forecast(
            df=df,
            model="timegpt-1",
            h=6,
            level=[90],  # Generate a 90% confidence interval
            finetune_steps=120,  # Specify the number of steps for fine-tuning
            finetune_loss="smape",  # Specify the loss function for fine-tuning
            freq="B",
            time_col="Datetime",
            target_col="Close",
        )

        plt.figure(figsize=(10, 6))
        plt.plot(
            forecast_result["Datetime"],
            forecast_result["TimeGPT"],
            marker="o",
            linestyle="-",
            color="b",
            label="TimeGPT Forecast",
        )
        # Customizing the plot
        plt.xlabel("Datetime")
        plt.ylabel("TimeGPT Forecast Value")
        # Formatting the x-axis to show both date and time
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=12))

        plt.title(
            "{} Price Forecast Using data from {} to {}".format(
                "BTC-USD",
                df["Datetime"].iloc[0].strftime("%Y-%m-%d %H:%M:%S"),
                df["Datetime"].iloc[-1].strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        plt.grid(True)
        plt.legend()
        # Improve readability of the date labels
        plt.xticks(rotation=45)
        plt.tight_layout()
        # Show the plot
        plt.show()
