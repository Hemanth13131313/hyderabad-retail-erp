import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_walmart_data():
    # Configuration
    products = {
        'SKU_001': {'Category': 'Dairy', 'Name': 'Milk', 'Base_Sales': 150, 'Price': 3.50},
        'SKU_002': {'Category': 'Bakery', 'Name': 'Bread', 'Base_Sales': 100, 'Price': 2.00},
        'SKU_003': {'Category': 'Electronics', 'Name': 'Smartphone', 'Base_Sales': 10, 'Price': 500.00},
        'SKU_004': {'Category': 'Clothing', 'Name': 'T-Shirt', 'Base_Sales': 50, 'Price': 15.00},
        'SKU_005': {'Category': 'Household', 'Name': 'Detergent', 'Base_Sales': 30, 'Price': 8.00}
    }

    # Location Network (Hub + Spokes)
    # Lat/Lon for Map Plotting
    locations = {
        'Warehouse': {'Type': 'Hub', 'Name': 'Kompally Central Warehouse', 'Coords': [17.55, 78.49], 'Stock_Multiplier': 50},
        'Branch_001': {'Type': 'Spoke', 'Name': 'Hitech City', 'Coords': [17.44, 78.38], 'Stock_Multiplier': 2, 'Sales_Multiplier': 1.5},
        'Branch_002': {'Type': 'Spoke', 'Name': 'Banjara Hills', 'Coords': [17.41, 78.43], 'Stock_Multiplier': 1.5, 'Sales_Multiplier': 1.2},
        'Branch_003': {'Type': 'Spoke', 'Name': 'Gachibowli', 'Coords': [17.44, 78.34], 'Stock_Multiplier': 1.8, 'Sales_Multiplier': 1.3},
        'Branch_004': {'Type': 'Spoke', 'Name': 'Secunderabad', 'Coords': [17.43, 78.50], 'Stock_Multiplier': 1.2, 'Sales_Multiplier': 1.0},
        'Branch_005': {'Type': 'Spoke', 'Name': 'Uppal', 'Coords': [17.39, 78.56], 'Stock_Multiplier': 1.0, 'Sales_Multiplier': 0.8}
    }

    start_date = datetime.now() - timedelta(days=365) # 1 year data
    dates = [start_date + timedelta(days=x) for x in range(365)]
    
    data = []

    print("Generating data for Network...")

    for date in dates:
        for loc_id, loc_info in locations.items():
            for pid, p_info in products.items():
                
                # Sales Logic
                if loc_info['Type'] == 'Hub':
                    sales = 0 # Warehouse doesn't sell directly
                else:
                    base = p_info['Base_Sales'] * loc_info['Sales_Multiplier']
                    # Seasonality & Randomness
                    month = date.month
                    dow = date.weekday()
                    
                    if month == 12: base *= 1.2
                    if dow >= 5: base *= 1.3
                    
                    sales = int(np.random.normal(base, base * 0.15))
                    if sales < 0: sales = 0

                # Stock Logic
                # Simulate stock levels
                target_stock = p_info['Base_Sales'] * loc_info['Stock_Multiplier'] 
                current_stock = int(np.random.normal(target_stock, target_stock * 0.1))
                if current_stock < 0: current_stock = 0
                
                # Lead Time (randomized slightly)
                lead_time = 2 if loc_info['Type'] == 'Spoke' else 14 # Hub takes longer to restock from supplier

                data.append([
                    date.strftime('%Y-%m-%d'),
                    loc_id,
                    loc_info['Name'],
                    loc_info['Type'],
                    loc_info['Coords'][0],
                    loc_info['Coords'][1],
                    pid,
                    p_info['Name'],
                    p_info['Category'],
                    sales,
                    current_stock,
                    lead_time,
                    p_info['Price']
                ])

    columns = ['Date', 'Location_ID', 'Location_Name', 'Location_Type', 'Lat', 'Lon', 
               'Product_ID', 'Product_Name', 'Category', 'Sales_Quantity', 'Current_Stock', 'Lead_Time_Days', 'Price']
    
    df = pd.DataFrame(data, columns=columns)
    
    # Ensure data directory exists
    output_dir = os.path.join(os.getcwd(), 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'walmart_network_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset generated at: {output_path}")
    print(df.head())

if __name__ == "__main__":
    generate_walmart_data()
