import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

def load_data(filepath, date_col='Date', target_col='Sales'):
    """
    Load data from CSV, parse dates, and set index.
    """
    try:
        df = pd.read_csv(filepath)
        # Check if columns exist
        if date_col not in df.columns or target_col not in df.columns:
            raise ValueError(f"Columns {date_col} and {target_col} must exist in the dataset.")
        
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(by=date_col)
        df = df.set_index(date_col)
        
        # Handle missing values (simple forward fill for time series)
        if df[target_col].isnull().any():
            print("Missing values detected. Imputing with forward fill.")
            df[target_col] = df[target_col].fillna(method='ffill')
            
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def decompose_series(df, target_col='Sales', model='additive', period=None):
    """
    Perform seasonal decomposition on the time series.
    """
    try:
        # If period is not specified, statsmodels tries to infer, but for monthly/daily data 
        # explicit period is often safer. Let's rely on index frequency if possible.
        if df.index.freq is None:
            # Attempt to infer freq
            try:
                df.index.freq = pd.infer_freq(df.index)
            except:
                pass
        
        decomposition = seasonal_decompose(df[target_col], model=model, period=period)
        return decomposition
    except Exception as e:
        print(f"Error in decomposition: {e}")
        return None
