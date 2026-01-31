import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
import pandas as pd

def calculate_metrics(y_true, y_pred):
    """
    Calculate RMSE and MAE.
    """
    if len(y_true) != len(y_pred):
        # Align lengths if necessary (e.g., if forecast is longer/shorter)
        min_len = min(len(y_true), len(y_pred))
        y_true = y_true[:min_len]
        y_pred = y_pred[:min_len]
    
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    return {'RMSE': rmse, 'MAE': mae}

def plot_forecast(train, test, forecast, title="Forecast vs Actual"):
    """
    Plot training data, actual test data, and forecast.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(train.index, train, label='Train')
    plt.plot(test.index, test, label='Actual Test')
    
    # Forecast might be a Index or just values depending on model
    if hasattr(forecast, 'index'):
        plt.plot(forecast.index, forecast, label='Forecast')
    else:
        # Assuming forecast aligns with test index start
        # If forecast is just an array, we need to generate an index or use test index if lengths match
        if len(forecast) == len(test):
             plt.plot(test.index, forecast, label='Forecast')
        else:
             # Fallback
             plt.plot(np.arange(len(train), len(train)+len(forecast)), forecast, label='Forecast')
             
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # Save plot can be added here or in main
    return plt

def plot_decomposition(decomposition):
    """
    Plot seasonal decomposition.
    """
    fig = decomposition.plot()
    fig.set_size_inches(12, 8)
    return fig
