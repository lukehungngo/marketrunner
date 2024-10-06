from nixtla.nixtla_client import AnyDFType
from pandas import DataFrame


def forecast(client, data: DataFrame) -> AnyDFType:
    return client.forecast(
        df=data,
        model="timegpt-1",
        h=8,  # Forecast X days ahead
        level=[90],  # Generate a 90% confidence interval
        finetune_steps=120,  # Specify the number of steps for fine-tuning
        freq="B",
        time_col="Date",
        target_col="Adj Close",
    )
