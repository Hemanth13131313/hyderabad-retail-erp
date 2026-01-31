import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

def train_arima(series, order=(1, 1, 1)):
    """
    Train an ARIMA model.
    series: A pandas Series with DatetimeIndex.
    order: Tuple (p, d, q).
    """
    try:
        # ARIMA requires a univariate series
        print(f"Training ARIMA with order {order}...")
        model = ARIMA(series, order=order)
        model_fit = model.fit()
        return model_fit
    except Exception as e:
        print(f"Error training ARIMA: {e}")
        return None

def forecast_arima(model_fit, steps):
    """
    Generate forecasts using a fitted ARIMA model.
    """
    try:
        forecast = model_fit.forecast(steps=steps)
        return forecast
    except Exception as e:
        print(f"Error forecasting ARIMA: {e}")
        return None

def train_prophet(df, date_col='ds', target_col='y'):
    """
    Train a Prophet model.
    df: Pandas DataFrame expecting columns 'ds' (date) and 'y' (value).
    """
    try:
        print("Training Prophet model...")
        model = Prophet()
        model.fit(df)
        return model
    except Exception as e:
        print(f"Error training Prophet: {e}")
        return None

def forecast_prophet(model, periods, freq='D'):
    """
    Generate forecasts using a fitted Prophet model.
    """
    try:
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)
        return forecast
    except Exception as e:
        print(f"Error forecasting Prophet: {e}")
        return None
