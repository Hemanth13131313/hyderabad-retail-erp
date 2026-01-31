import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

# --- Configuration ---
DATA_FILE = 'data/raw/sales_data.csv'

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.index.freq = pd.infer_freq(df.index)
    return df

def check_stationarity(series):
    print("\n--- 1. Augmented Dickey-Fuller Test ---")
    result = adfuller(series)
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {result[1]}')
    print('Critical Values:')
    for key, value in result[4].items():
        print(f'\t{key}: {value}')
    
    if result[1] <= 0.05:
        print("Result: Series is Stationary")
    else:
        print("Result: Series is Non-Stationary")

def decompose_data(series):
    print("\n--- 2. Seasonal Decomposition ---")
    decomposition = seasonal_decompose(series, model='additive')
    
    # Plotting
    fig = decomposition.plot()
    fig.set_size_inches(12, 8)
    plt.suptitle('Seasonal Decomposition', fontsize=16)
    plt.tight_layout()
    plt.show()
    print("Decomposition plot generated.")

def run_arima(series):
    print("\n--- 3. ARIMA Modeling ---")
    # Split data
    train_size = int(len(series) * 0.8)
    train, test = series[0:train_size], series[train_size:len(series)]
    
    # Train Model (Generic order, can be tuned)
    model = ARIMA(train, order=(5,1,0))
    model_fit = model.fit()
    print(model_fit.summary())
    
    # Forecast
    forecast = model_fit.forecast(steps=len(test))
    
    # Visualization
    plt.figure(figsize=(12, 6))
    plt.plot(train.index, train, label='Train')
    plt.plot(test.index, test, label='Actual')
    plt.plot(test.index, forecast, label='Forecast', color='red')
    plt.title('ARIMA Forecast vs Actual')
    plt.xlabel('Date')
    plt.ylabel('Sales')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    rmse = np.sqrt(mean_squared_error(test, forecast))
    print(f"\nModel RMSE: {rmse}")

if __name__ == "__main__":
    try:
        # Load
        df = load_data(DATA_FILE)
        sales_series = df['Sales']
        
        # 1. Stationarity
        check_stationarity(sales_series)
        
        # 2. Decomposition
        decompose_data(sales_series)
        
        # 3. ARIMA & Plot
        run_arima(sales_series)
        
    except FileNotFoundError:
        print(f"Error: {DATA_FILE} not found. Please run src/main.py first to generate dummy data.")
