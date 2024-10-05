import time
from datetime import datetime, timedelta

import yfinance as yf
from django.conf import settings
from django.core.management.base import BaseCommand
from nixtla import NixtlaClient
import pandas as pd
import matplotlib.pyplot as plt


class Command(BaseCommand):
    help = 'Runs Nixtla Time GPT for stock data'

    def handle(self, *args, **kwargs):
        # Get the API key from settings
        nixtla_client = NixtlaClient(api_key=settings.NIXTLA_API_KEY)

        # Define the stock ticker and download the data
        ticker = 'BTC-USD'
        all_meta_stock_data = yf.download(ticker)
        all_meta_stock_data = all_meta_stock_data.reset_index()
        num_of_date_before = 30 * 80
        meta_stock_data = all_meta_stock_data.tail(num_of_date_before)
        last_date = meta_stock_data.tail(1)['Date'].values[0]
        first_date = meta_stock_data.head(1)['Date'].values[0]
        print(f'Last date: {last_date}')
        print(f'First date: {first_date}')
        # Plot the data
        # nixtla_client.plot(meta_stock_data, time_col='Date', target_col='Adj Close')
        meta_stock_forecast = nixtla_client.forecast(
            df=meta_stock_data,
            model="timegpt-1",
            h=12,
            level=[90],  # Generate a 90% confidence interval
            finetune_steps=120,  # Specify the number of steps for fine-tuning
            finetune_loss="mae",  # Specify the loss function for fine-tuning
            freq="B",
            time_col="Date",
            target_col="Adj Close",
        )

        self.stdout.write(str(meta_stock_forecast.head(20)))
        nixtla_client.plot(
            meta_stock_data.tail(30),
            meta_stock_forecast.tail(40),
            models=["TimeGPT"],
            level=[90],
            time_col="Date",
            target_col="Adj Close",
        )
        # Assuming meta_stock_forecast is a pandas DataFrame with 'Date' and 'TimeGPT' columns
        meta_stock_forecast['Date'] = pd.to_datetime(
            meta_stock_forecast['Date'])  # Ensure 'Date' is in datetime format
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(meta_stock_forecast['Date'], meta_stock_forecast['TimeGPT'], marker='o', linestyle='-', color='b',
                 label='TimeGPT Forecast')
        # Customizing the plot
        plt.xlabel('Date')
        plt.ylabel('TimeGPT Forecast Value')

        plt.title('{} Price Forecast Using data from {}'.format(ticker,
                                                                (datetime.now() - timedelta(
                                                                    days=num_of_date_before)).strftime("%Y-%m-%d")))
        plt.grid(True)
        plt.legend()
        # Improve readability of the date labels
        plt.xticks(rotation=45)
        plt.tight_layout()
        # Show the plot
        plt.show()
