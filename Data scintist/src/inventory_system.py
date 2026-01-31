import pandas as pd
from prophet import Prophet
import os
import logging
from datetime import timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def train_predict_product(df_product, months_to_predict=1):
    """
    Trains a Prophet model for a single product and forecasts sales.
    """
    # Prepare dataframe for Prophet (ds, y)
    df_prophet = df_product[['Date', 'Sales_Quantity']].rename(columns={'Date': 'ds', 'Sales_Quantity': 'y'})
    
    # Initialize and train model
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df_prophet)
    
    # Create future dataframe
    future_days = 30 * months_to_predict
    future = model.make_future_dataframe(periods=future_days)
    
    # Forecast
    forecast = model.predict(future)
    
    # Get the sum of predicted sales for the *next* 30 days
    # We filter for dates > last date in historical data
    last_date = df_prophet['ds'].max()
    next_30_days = forecast[forecast['ds'] > last_date].head(30)
    
    total_predicted_sales = next_30_days['yhat'].sum()
    
    # Avoid negative predictions
    return max(0, total_predicted_sales)

def calculate_reorder_point(df_product, lead_time_days):
    """
    Calculates Reorder Point = (Avg Daily Usage * Lead Time) + Safety Stock
    Safety Stock = (Max Daily Usage * Max Lead Time) - (Avg Daily Usage * Avg Lead Time)
    For simplicity here, we assume Lead Time is constant, so:
    Safety Stock = (Max Daily Usage * Lead Time) - (Avg Daily Usage * Lead Time) 
                 = (Max Daily Usage - Avg Daily Usage) * Lead Time
    """
    avg_daily_usage = df_product['Sales_Quantity'].mean()
    max_daily_usage = df_product['Sales_Quantity'].max()
    
    # Safety Stock Formula (simplified for constant lead time)
    safety_stock = (max_daily_usage - avg_daily_usage) * lead_time_days
    
    reorder_point = (avg_daily_usage * lead_time_days) + safety_stock
    
    return reorder_point

def run_inventory_system():
    # Load Data
    data_path = os.path.join(os.getcwd(), 'data', 'raw', 'walmart_store_data.csv')
    if not os.path.exists(data_path):
        logging.error(f"Data file not found at {data_path}. Please run generate_data.py first.")
        return

    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    products = df['Product_ID'].unique()
    
    report_data = []
    
    logging.info("Starting analysis for all products...")
    
    for product_id in products:
        logging.info(f"Processing {product_id}...")
        
        # Filter for current product
        df_product = df[df['Product_ID'] == product_id].sort_values('Date')
        
        # Get latest stock info (assuming the last row has the most current stock info)
        current_stock = df_product.iloc[-1]['Current_Stock']
        lead_time = df_product.iloc[-1]['Lead_Time_Days']
        
        # 1. Forecast Demand (Next 30 Days)
        predicted_demand = train_predict_product(df_product)
        
        # 2. Calculate Reorder Point
        reorder_point = calculate_reorder_point(df_product, lead_time)
        
        # 3. Decision Engine
        status = "OK"
        quantity_to_order = 0
        
        # Logic: If (Current Stock - Predicted Sales) < Reorder Point, then REFILL
        # Note: The prompt formula was slightly ambiguous ("Current Stock - Predicted Sales"). 
        # Usually it's if Current Stock < Reorder Point. 
        # But if we follow "If (Current Stock - Predicted Sales) < Reorder Point":
        # This implies we are looking at the projected stock after 30 days.
        # Let's check the prompt precisely: "If (Current Stock - Predicted Sales) < Reorder Point"
        
        projected_stock = current_stock - predicted_demand
        
        if projected_stock < reorder_point:
            status = "CRITICAL"
            # How much to order? Let's aim to be back above Reorder Point + some buffer (e.g., forecasted demand)
            # Or just order enough to cover the deficit + safety stock?
            # A simple Economic Order Quantity (EOQ) or target level is better, but let's stick to filling up to a target.
            
            # Let's say we want to end up with stock = reorder_point + predicted_demand (to cover next cycle)
            # Quantity = (Reorder Point + Predicted Demand) - Current Stock
            # OR simpler: Quantity = Reorder Point - Projected Stock (to get back to Reorder Point)
            # Let's use: Order enough to cover demand + safety buffer.
            quantity_to_order = round(reorder_point - projected_stock + (predicted_demand * 0.1)) # +10% buffer
        
        report_data.append({
            'Product_ID': product_id,
            'Forecasted_Demand_30_Days': round(predicted_demand, 2),
            'Current_Stock': current_stock,
            'Reorder_Point': round(reorder_point, 2),
            'Status': status,
            'Quantity_To_Order': max(0, quantity_to_order)
        })

    # Create Report
    restock_report = pd.DataFrame(report_data)
    
    # Save Report
    output_dir = os.path.join(os.getcwd(), 'reports')
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, 'restock_report.csv')
    restock_report.to_csv(report_path, index=False)
    
    print("\n=== RESTOCK REPORT ===")
    print(restock_report)
    print(f"\nReport saved to: {report_path}")


# ... (Inside inventory_system.py - adding new functions)

def load_network_data():
    data_path = os.path.join(os.getcwd(), 'data', 'raw', 'walmart_network_data.csv')
    if not os.path.exists(data_path):
        return pd.DataFrame()
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def calculate_stock_transfer(df, forecast_days=7):
    """
    Calculates stock transfers from Hub to Spokes for the next 7 days.
    """
    latest_date = df['Date'].max()
    today_df = df[df['Date'] == latest_date]
    
    # Separate Hub and Spokes
    hub = today_df[today_df['Location_Type'] == 'Hub'].set_index('Product_ID')
    spokes = today_df[today_df['Location_Type'] == 'Spoke']
    
    transfer_plan = []
    
    products = df['Product_ID'].unique()
    
    for product in products:
        if product not in hub.index:
            continue
            
        hub_stock = hub.loc[product, 'Current_Stock']
        
        # Calculate Total Demand per Spoke for next 7 days
        spoke_demands = []
        total_demand_all_spokes = 0
        
        product_spokes = spokes[spokes['Product_ID'] == product]
        
        for _, spoke in product_spokes.iterrows():
            # Get historical data for this spoke/product to forecast
            spoke_hist = df[(df['Location_ID'] == spoke['Location_ID']) & 
                            (df['Product_ID'] == product)].sort_values('Date')
            
            # Simple forecast: Avg Sales last 30 days * forecast_days
            # (Using simple moving average for speed in this demo instead of Prophet for every single combo on the fly)
            avg_daily_sales = spoke_hist.tail(30)['Sales_Quantity'].mean()
            predicted_demand = avg_daily_sales * forecast_days
            
            # Net Need = Predicted Demand - Current Stock
            # If Current Stock > Predicted Demand, Need is 0
            net_need = max(0, predicted_demand - spoke['Current_Stock'])
            
            spoke_demands.append({
                'Location': spoke['Location_Name'],
                'Net_Need': net_need,
                'Current_Stock': spoke['Current_Stock']
            })
            total_demand_all_spokes += net_need
            
        # Allocation Logic
        # If Hub has enough, give everyone what they need.
        # If Hub has less, pro-rate.
        
        available_to_ship = hub_stock # Assuming we can ship everything if needed
        
        for demand in spoke_demands:
            qty_to_transfer = 0
            if total_demand_all_spokes > 0:
                if available_to_ship >= total_demand_all_spokes:
                    qty_to_transfer = demand['Net_Need']
                else:
                    # Pro-rate
                    share = demand['Net_Need'] / total_demand_all_spokes
                    qty_to_transfer = share * available_to_ship
            
            if qty_to_transfer > 0:
                transfer_plan.append({
                    'Product_ID': product,
                    'Product_Name': today_df[today_df['Product_ID'] == product].iloc[0]['Product_Name'],
                    'From_Hub': hub.iloc[0]['Location_Name'],
                    'To_Branch': demand['Location'],
                    'Qty_Requested': round(demand['Net_Need'], 2),
                    'Qty_Approved': int(qty_to_transfer),
                    'Hub_Status': 'Sufficient' if available_to_ship >= total_demand_all_spokes else 'Shortage',
                    'Hub_Stock': hub_stock # Snapshot
                })
                
    return pd.DataFrame(transfer_plan)

# ... (Original code below kept or adapted - we primarily focus on the new functions for app.py)

