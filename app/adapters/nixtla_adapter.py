from nixtla.nixtla_client import AnyDFType
from pandas import DataFrame


def forecast(client, data: DataFrame) -> AnyDFType:
    return client.forecast(
        df=data,
        model="timegpt-1",
        h=7,  # Forecast X days ahead
        level=[90],  # Generate a 90% confidence interval
        time_col="Date",
        target_col="Adj Close",
    )
