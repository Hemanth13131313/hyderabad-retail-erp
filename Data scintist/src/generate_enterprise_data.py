import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

def generate_enterprise_data():
    print("Initializing Enterprise Data Generation...")
    
    # 1. Define Network
    locations = {
        'W_001': {'Name': 'Shamirpet Central Warehouse', 'Type': 'Warehouse'},
        'S_001': {'Name': 'Gachibowli', 'Type': 'Store'},
        'S_002': {'Name': 'Jubilee Hills', 'Type': 'Store'},
        'S_003': {'Name': 'Madhapur', 'Type': 'Store'},
        'S_004': {'Name': 'Kukatpally', 'Type': 'Store'},
        'S_005': {'Name': 'Banjara Hills', 'Type': 'Store'},
        'S_006': {'Name': 'Kondapur', 'Type': 'Store'},
        'S_007': {'Name': 'Begumpet', 'Type': 'Store'},
        'S_008': {'Name': 'Uppal', 'Type': 'Store'},
        'S_009': {'Name': 'Dilsukhnagar', 'Type': 'Store'},
        'S_010': {'Name': 'Charminar', 'Type': 'Store'},
    }
    
    # 2. Define Product Hierarchy
    # Category -> Sub-Category -> SKUs
    # Including Price and Sales Velocity Flag (Fast/Slow)
    products = [
        # Electronics (High Value, Slow/Medium Moving)
        {'ID': 'E_001', 'Name': 'iPhone 15', 'Cat': 'Electronics', 'Sub': 'Mobile', 'Price': 80000, 'Velocity': 'Medium', 'Base': 5},
        {'ID': 'E_002', 'Name': 'Samsung S24', 'Cat': 'Electronics', 'Sub': 'Mobile', 'Price': 75000, 'Velocity': 'Medium', 'Base': 5},
        {'ID': 'E_003', 'Name': 'MacBook Air', 'Cat': 'Electronics', 'Sub': 'Laptop', 'Price': 100000, 'Velocity': 'Slow', 'Base': 2},
        {'ID': 'E_004', 'Name': 'Sony Headphones', 'Cat': 'Electronics', 'Sub': 'Audio', 'Price': 20000, 'Velocity': 'Medium', 'Base': 8},
        
        # Daily Needs (Low Value, Fast Moving)
        {'ID': 'D_001', 'Name': 'Fresh Milk 1L', 'Cat': 'Daily Needs', 'Sub': 'Dairy', 'Price': 60, 'Velocity': 'Fast', 'Base': 200},
        {'ID': 'D_002', 'Name': 'Whole Wheat Bread', 'Cat': 'Daily Needs', 'Sub': 'Bakery', 'Price': 50, 'Velocity': 'Fast', 'Base': 150},
        {'ID': 'D_003', 'Name': 'Farm Eggs (12)', 'Cat': 'Daily Needs', 'Sub': 'Dairy', 'Price': 90, 'Velocity': 'Fast', 'Base': 100},
        {'ID': 'D_004', 'Name': 'Tomatoes (1kg)', 'Cat': 'Daily Needs', 'Sub': 'Vegetables', 'Price': 40, 'Velocity': 'Fast', 'Base': 180},
        
        # Home Essentials (Medium Value, Medium Moving)
        {'ID': 'H_001', 'Name': 'Detergent 2kg', 'Cat': 'Home Essentials', 'Sub': 'Cleaning', 'Price': 350, 'Velocity': 'Medium', 'Base': 40},
        {'ID': 'H_002', 'Name': 'Toilet Paper Pack', 'Cat': 'Home Essentials', 'Sub': 'Cleaning', 'Price': 200, 'Velocity': 'Medium', 'Base': 60},
        {'ID': 'H_003', 'Name': 'Study Table', 'Cat': 'Home Essentials', 'Sub': 'Furniture', 'Price': 4000, 'Velocity': 'Slow', 'Base': 1},
        
        # Fashion (Medium Value, Seasonal)
        {'ID': 'F_001', 'Name': 'Mens T-Shirt', 'Cat': 'Fashion', 'Sub': 'Menswear', 'Price': 800, 'Velocity': 'Medium', 'Base': 25},
        {'ID': 'F_002', 'Name': 'Womans Jeans', 'Cat': 'Fashion', 'Sub': 'Womenswear', 'Price': 2500, 'Velocity': 'Medium', 'Base': 15},
    ]

    # Generate Data for last 180 days
    start_date = datetime.now() - timedelta(days=180)
    dates = [start_date + timedelta(days=x) for x in range(180)]
    
    records = []
    
    print("Processing dates...")
    for date in dates:
        month = date.month
        is_weekend = date.weekday() >= 5
        
        # Events
        is_diwali = (month == 11 and 10 <= date.day <= 15) # Mock Diwali
        is_sale = (date.day == 1) # First of month sale
        
        for loc_id, loc_info in locations.items():
            for p in products:
                # 3. Sales Generation Logic
                if loc_info['Type'] == 'Warehouse':
                    sales = 0
                else:
                    base_sales = p['Base']
                    
                    # Store Multiplier (Jubilee Hills sells more than Uppal mock logic)
                    store_mult = 1.0
                    if loc_id == 'S_002': store_mult = 1.5 # Wealthy area
                    if loc_id == 'S_001': store_mult = 1.3
                    
                    # Seasonality / Spike Logic
                    spike_mult = 1.0
                    if is_weekend: spike_mult *= 1.4
                    if is_sale: spike_mult *= 1.2
                    if is_diwali:
                        if p['Cat'] in ['Electronics', 'Fashion', 'Home Essentials']:
                            spike_mult *= 3.0 # Huge spike
                        else:
                            spike_mult *= 1.5
                            
                    final_mean = base_sales * store_mult * spike_mult
                    sales = max(0, int(np.random.normal(final_mean, final_mean * 0.2)))
                
                # 4. Inventory Logic
                # Simulate stock levels fluctuating. 
                # Warehouse has massive stock. Stores have limited stock.
                
                if loc_info['Type'] == 'Warehouse':
                    stock = p['Base'] * 500 # Huge buffer
                else:
                    target = p['Base'] * 7 # 1 week cover
                    # Randomize stock to create "Critical" situations for the heatmap
                    # Random walkish but simplified:
                    stock_level_factor = np.random.triangular(0.1, 0.8, 1.5) # Tend towards healthy but occasional dips
                    stock = max(0, int(target * stock_level_factor))
                    
                    # Force some critical stockouts for demo visualization
                    if random.random() < 0.05: # 5% chance of crisis
                        stock = int(p['Base'] * 0.5) # critical
                        
                records.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Location_ID': loc_id,
                    'Location_Name': loc_info['Name'],
                    'Location_Type': loc_info['Type'],
                    'Product_ID': p['ID'],
                    'Product_Name': p['Name'],
                    'Category': p['Cat'],
                    'Sub_Category': p['Sub'],
                    'Price': p['Price'],
                    'Sales_Qty': sales,
                    'Revenue': sales * p['Price'],
                    'Current_Stock': stock,
                    'Target_Stock': p['Base'] * 7 if loc_info['Type'] == 'Store' else 0
                })

    df = pd.DataFrame(records)
    
    output_dir = os.path.join(os.getcwd(), 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'walmart_enterprise_data.csv')
    
    df.to_csv(output_path, index=False)
    print(f"Enterprise Data Generated: {len(df)} rows.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    generate_enterprise_data()
