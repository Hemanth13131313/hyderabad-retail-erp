import os
import sys

# Add project root to sys.path to allow 'src' imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.preprocessing import load_data, decompose_series
from src.models import train_arima, forecast_arima, train_prophet, forecast_prophet
from src.evaluation import calculate_metrics, plot_forecast, plot_decomposition

# Configuration
DATA_DIR = 'data/raw'
PROCESSED_DIR = 'data/processed'
REPORTS_DIR = 'reports'
FILENAME = 'sales_data.csv' # Expecting this filename
DATE_COL = 'Date'
SALES_COL = 'Sales'

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_dummy_data(filepath):
    """Generates dummy monthly sales data."""
    print("Generating dummy data...")
    dates = pd.date_range(start='2020-01-01', end='2023-12-01', freq='MS')
    # Trend + Seasonality + Noise
    trend = np.linspace(100, 300, len(dates))
    seasonality = 50 * np.sin(np.linspace(0, 3.14 * 8, len(dates)))
    noise = np.random.normal(0, 20, len(dates))
    sales = trend + seasonality + noise
    
    df = pd.DataFrame({DATE_COL: dates, SALES_COL: sales})
    df.to_csv(filepath, index=False)
    print(f"Dummy data saved to {filepath}")

def main():
    filepath = os.path.join(DATA_DIR, FILENAME)
    
    # Check if data exists, else generate
    if not os.path.exists(filepath):
        print(f"File {FILENAME} not found in {DATA_DIR}. Creating dummy dataset.")
        generate_dummy_data(filepath)
    
    # 1. Load Data
    print("\n--- Loading Data ---")
    df = load_data(filepath, date_col=DATE_COL, target_col=SALES_COL)
    if df is None:
        return
    
    # Train/Test Split (Dynamic)
    # If data is small (< 50 points), take top 20% as test, otherwise 12 steps
    if len(df) < 50:
        test_size = int(len(df) * 0.2)
        if test_size < 1: test_size = 1
    else:
        test_size = 12
        
    train_size = len(df) - test_size
    train, test = df.iloc[:train_size], df.iloc[train_size:]
    print(f"Train size: {len(train)}, Test size: {len(test)}")
    
    # 2. Decomposition
    print("\n--- Performing Decomposition ---")
    # Determine period based on freq or size
    period = 12 # Default
    if df.index.freqstr:
        if 'D' in df.index.freqstr: period = 7
        elif 'M' in df.index.freqstr: period = 12
    elif len(df) < 24: # Fallback for very small data
        period = 2
        
    # Safety check: statsmodels needs 2*period observations
    if len(train) < 2 * period:
        print(f"Warning: Not enough data for decomposition with period={period}. Reducing period to 2.")
        period = 2
        
    decomposition = decompose_series(train, target_col=SALES_COL, period=period)
    if decomposition:
        fig_decomp = plot_decomposition(decomposition)
        fig_decomp.savefig(os.path.join(REPORTS_DIR, 'decomposition.png'))
        print("Decomposition plot saved.")

    # 3. ARIMA Model
    print("\n--- Training ARIMA ---")
    # Adjust order if data is small
    p = 5 if len(train) > 10 else 1
    arima_order = (p, 1, 0) 
    arima_model = train_arima(train[SALES_COL], order=arima_order)
    
    if arima_model:
        arima_forecast = forecast_arima(arima_model, steps=len(test))
        # Series to align with test index
        arima_forecast_series = pd.Series(arima_forecast, index=test.index)
        
        # Eval
        arima_metrics = calculate_metrics(test[SALES_COL], arima_forecast_series)
        print(f"ARIMA Metrics: {arima_metrics}")
        
        # Plot
        fig_arima = plot_forecast(train[SALES_COL], test[SALES_COL], arima_forecast_series, title="ARIMA Forecast")
        fig_arima.savefig(os.path.join(REPORTS_DIR, 'arima_forecast.png'))
        print("ARIMA forecast plot saved.")

    # 4. Prophet Model
    print("\n--- Training Prophet ---")
    # Prophet expects 'ds' and 'y'
    prophet_df = train.reset_index().rename(columns={DATE_COL: 'ds', SALES_COL: 'y'})
    prophet_model = train_prophet(prophet_df)
    
    if prophet_model:
        # Forecast
        # Determine freq for prophet
        freq = 'D'
        if df.index.freqstr:
            freq = df.index.freqstr
            
        prophet_forecast = forecast_prophet(prophet_model, periods=len(test), freq=freq)
        
        # Extract forecast for test period
        # The forecast df contains historical + future. We just want the tail.
        y_pred_prophet = prophet_forecast.tail(len(test))['yhat'].values
        y_pred_prophet_series = pd.Series(y_pred_prophet, index=test.index)

        # Eval
        prophet_metrics = calculate_metrics(test[SALES_COL], y_pred_prophet_series)
        print(f"Prophet Metrics: {prophet_metrics}")
        
        # Plot
        fig_prophet = plot_forecast(train[SALES_COL], test[SALES_COL], y_pred_prophet_series, title="Prophet Forecast")
        fig_prophet.savefig(os.path.join(REPORTS_DIR, 'prophet_forecast.png'))
        print("Prophet forecast plot saved.")

    print("\n--- Processing Complete. Check 'reports/' folder. ---")

if __name__ == "__main__":
    main()
