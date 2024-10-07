from nixtla.nixtla_client import AnyDFType
from pandas import DataFrame


def forecast(client, data: DataFrame) -> AnyDFType:
    print("Forecasting data with Nixtla")
    print("Data:", data.tail())
    print("Data:", data.head())
    print("Data shape:", data.shape)
    return client.forecast(
        df=data,
        model="timegpt-1",
        freq="D",  # Daily frequency
        h=7,  # Forecast X days ahead
        level=[90],  # Generate a 90% confidence interval
        time_col="date",
        target_col="close",
    )
