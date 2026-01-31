import pytest
import pandas as pd
import sys
import os

# Add src to path to import backend functions if needed
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mocking or extracting the logic to test
# Since we want to test independent logic chunks:

# ----------------- TEST 1: Data Validation -----------------
def validate_csv_columns(df):
    required_columns = {'Date', 'Product_ID', 'Sales_Qty'}
    return required_columns.issubset(df.columns)

def test_csv_upload_validation():
    """
    Test Case 1: Data Validation
    Checks if a dummy uploaded CSV has the required columns.
    """
    # Simulate a loaded CSV
    data = {
        'Date': ['2024-01-01'],
        'Product_ID': ['P01'],
        'Sales_Qty': [100],
        'Extra_Col': ['Ignore']
    }
    df = pd.DataFrame(data)
    
    # Assert validation passes
    assert validate_csv_columns(df) == True
    
    # Negative Test
    bad_data = {'Date': ['2024-01-01'], 'Sales_Qty': [100]} # Missing Product_ID
    bad_df = pd.DataFrame(bad_data)
    assert validate_csv_columns(bad_df) == False

# ----------------- TEST 2: Logic Check (Forecast) -----------------
def forecast_sales_safe(predicted_value):
    """
    Simulated wrapper for the forecasting function logic
    that ensures non-negative returns.
    """
    return max(0, predicted_value)

def test_forecast_non_negative():
    """
    Test Case 2: Logic Check
    Ensures that the forecasting function never returns a negative number.
    """
    # Scenario A: Positive prediction
    assert forecast_sales_safe(50) == 50
    
    # Scenario B: Negative prediction (Model output anomaly)
    assert forecast_sales_safe(-5) == 0
    
    # Scenario C: Zero
    assert forecast_sales_safe(0) == 0

# ----------------- TEST 3: Stock Alert Check -----------------
def check_stock_status(current_stock, safety_stock):
    """
    Simulates the status determination logic.
    """
    if current_stock < safety_stock:
        return "CRITICAL"
    else:
        return "OK"

def test_stock_alert_trigger():
    """
    Test Case 3: Stock Alert Check
    Asserts True if Current_Stock < Safety_Stock triggers "CRITICAL".
    """
    # Case 1: Crisis
    current = 10
    safety = 20
    assert check_stock_status(current, safety) == "CRITICAL"
    
    # Case 2: Healthy
    current = 50
    safety = 20
    assert check_stock_status(current, safety) == "OK"
    
    # Case 3: Edge Case (Equal) - usually OK
    assert check_stock_status(20, 20) == "OK"

if __name__ == "__main__":
    print("Run this file using 'pytest test_app.py'")
