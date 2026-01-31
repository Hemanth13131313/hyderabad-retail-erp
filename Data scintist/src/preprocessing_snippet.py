from statsmodels.tsa.stattools import adfuller

def check_stationarity(series):
    """
    Perform Augmented Dickey-Fuller test to check for stationarity.
    """
    print("Results of Dickey-Fuller Test:")
    try:
        dftest = adfuller(series, autolag='AIC')
        dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
        for key,value in dftest[4].items():
            dfoutput['Critical Value (%s)'%key] = value
        print(dfoutput)
        
        if dftest[1] <= 0.05:
            print("\nConclusion: The series is stationary (p-value <= 0.05).")
        else:
            print("\nConclusion: The series is NOT stationary (p-value > 0.05).")
        return dftest
    except Exception as e:
        print(f"Error in ADF test: {e}")
        return None
