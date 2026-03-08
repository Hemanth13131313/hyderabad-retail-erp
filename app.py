import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime, timedelta
import hashlib
import re

# ==============================================================================
# 1. SECURITY & CONFIGURATION LAYER
# ==============================================================================

st.set_page_config(
    page_title="Hyderabad Retail Nexus",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1e293b; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
    .critical { background-color: #fca5a5; color: #7f1d1d; }
    .healthy { background-color: #86efac; color: #14532d; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# --- SECURITY UTILS ---
def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

def sanitize_input(user_input):
    if not isinstance(user_input, str): return user_input
    return re.sub(r'[^\w\s\-\.\@]', '', user_input)

# --- AUTHENTICATION MODULE ---
# CREDENTIALS dict removed, we now use the 'employees' table in session_state

def login_user(username, password):
    safe_user = sanitize_input(username)
    if 'db' in st.session_state and 'employees' in st.session_state['db']:
        employees_df = st.session_state['db']['employees']
        user_record = employees_df[(employees_df['Username'] == safe_user) & (employees_df['Status'] == 'Active')]
        if not user_record.empty:
            stored_hash = user_record.iloc[0]['PasswordHash']
            if stored_hash == hash_password(password):
                return True, user_record.iloc[0]['Role'], user_record.iloc[0]['Store']
    return False, None, None

# ==============================================================================
# 2. DATA PROCESSING & OPTIMIZATION LAYER
# ==============================================================================

def initialize_data_optimized():
    stores_info = {
        'Hitech City': 'HYDSTR001', 'Banjara Hills': 'HYDSTR002', 'Gachibowli': 'HYDSTR003',
        'Secunderabad': 'HYDSTR004', 'Uppal': 'HYDSTR005', 'Jubilee Hills': 'HYDSTR006',
        'Madhapur': 'HYDSTR007', 'Kukatpally': 'HYDSTR008', 'Begumpet': 'HYDSTR009', 'Charminar': 'HYDSTR010'
    }
    stores = list(stores_info.keys())
    
    products_info = {
        'iPhone 15': 75000.0, 'Samsung TV': 45000.0, 'Milk (1L)': 60.0, 
        'Rice (25kg)': 1200.0, 'Detergent': 250.0, 'T-Shirt': 500.0
    }
    products = list(products_info.keys())
    
    # Coordinates mapping
    coords = {
        'Hitech City': (17.44, 78.38), 'Banjara Hills': (17.41, 78.43),
        'Gachibowli': (17.44, 78.34), 'Secunderabad': (17.43, 78.50),
        'Uppal': (17.39, 78.56), 'Jubilee Hills': (17.42, 78.40),
        'Madhapur': (17.45, 78.39), 'Kukatpally': (17.48, 78.40),
        'Begumpet': (17.44, 78.46), 'Charminar': (17.36, 78.47)
    }
    
    df = pd.DataFrame([{'Location': s, 'StoreID': stores_info[s], 'Product': p, 'Type': 'Store'} for s in stores for p in products])
    hub_df = pd.DataFrame([{'Location': 'Kompally Hub', 'Product': p, 'Type': 'Hub'} for p in products])
    df = pd.concat([hub_df, df], ignore_index=True)
    
    targets = {'iPhone 15': 20, 'Samsung TV': 10, 'Milk (1L)': 100, 'Rice (25kg)': 50, 'Detergent': 80, 'T-Shirt': 40}
    df['Target_Stock'] = df['Product'].map(targets)
    df['Current_Stock'] = np.where(
        df['Type'] == 'Hub',
        df['Target_Stock'] * 100,
        (np.random.rand(len(df)) * 1.5 * df['Target_Stock']).astype(int)
    )
    df['Lat'] = df['Location'].map(lambda x: coords.get(x, (17.55, 78.49))[0])
    df['Lon'] = df['Location'].map(lambda x: coords.get(x, (17.55, 78.49))[1])
    
    # Generate Mock Sales
    sales_data = []
    # Make random seed for reproducibility in sales demo
    np.random.seed(42)
    for _ in range(250):
        sale_date = datetime.now() - timedelta(days=np.random.randint(0, 30))
        store = np.random.choice(stores)
        prod = np.random.choice(products)
        qty = np.random.randint(1, 4)
        sales_data.append({
            'Date': sale_date.strftime("%Y-%m-%d %H:%M"),
            'Location': store,
            'Product': prod,
            'Quantity': qty,
            'Revenue': qty * products_info[prod]
        })
    sales_df = pd.DataFrame(sales_data)
    # Sort by Date descending correctly
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    sales_df = sales_df.sort_values(by='Date', ascending=False)
    sales_df['Date'] = sales_df['Date'].dt.strftime('%Y-%m-%d %H:%M')

    # Dispatches (empty at start, will fill from actions)
    dispatches_df = pd.DataFrame(columns=['Date', 'Destination', 'Product', 'Quantity', 'Status'])

    # Requests
    requests_df = pd.DataFrame([
         {'Date': (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), 'Store': 'Gachibowli', 'Product': 'Milk (1L)', 'Quantity': 50, 'Status': 'Pending'},
         {'Date': (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"), 'Store': 'Charminar', 'Product': 'Rice (25kg)', 'Quantity': 20, 'Status': 'Approved'}
    ])

    # Employees
    employees_data = [
        {'EmpID': 'EMP-0001', 'Name': 'Super Admin', 'Username': 'admin', 'PasswordHash': hash_password('admin123'), 'Contact': 'admin@nexus.com', 'Role': 'Admin', 'Store': 'All', 'Wage': 50000, 'Status': 'Active'},
        {'EmpID': 'HYDSTR001-MGR', 'Name': 'Store Manager Hitech', 'Username': 'manager1', 'PasswordHash': hash_password('mgr123'), 'Contact': 'mgr.hitech@nexus.com', 'Role': 'Manager', 'Store': 'Hitech City', 'Wage': 35000, 'Status': 'Active'},
        {'EmpID': 'EMP-2051', 'Name': 'Cashier Hitech', 'Username': 'employee', 'PasswordHash': hash_password('emp123'), 'Contact': 'cashier.hitech@nexus.com', 'Role': 'Employee', 'Store': 'Hitech City', 'Wage': 20000, 'Status': 'Active'},
        {'EmpID': 'HYDCHAR001', 'Name': 'Rajesh', 'Username': 'rajesh', 'PasswordHash': hash_password('emp123'), 'Contact': 'rajesh@nexus.com', 'Role': 'Employee', 'Store': 'Charminar', 'Wage': 22000, 'Status': 'Active'},
        {'EmpID': 'HYDBAN001', 'Name': 'Suresh', 'Username': 'suresh', 'PasswordHash': hash_password('emp123'), 'Contact': 'suresh@nexus.com', 'Role': 'Employee', 'Store': 'Banjara Hills', 'Wage': 25000, 'Status': 'Active'},
        {'EmpID': 'HYDGAC001', 'Name': 'Ramesh', 'Username': 'ramesh', 'PasswordHash': hash_password('emp123'), 'Contact': 'ramesh@nexus.com', 'Role': 'Employee', 'Store': 'Gachibowli', 'Wage': 24000, 'Status': 'Active'}
    ]
    employees_df = pd.DataFrame(employees_data)

    # Attendance
    att_data = []
    for emp_id in [e['EmpID'] for e in employees_data if e['Role'] != 'Admin']:
        # Generate 15-25 random days of attendance in the last 30 days
        days_worked = np.random.randint(15, 26)
        for d in range(days_worked):
            date_str = (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime("%Y-%m-%d")
            att_data.append({
                'EmpID': emp_id,
                'Date': date_str,
                'CheckIn': '09:00:00',
                'CheckOut': '18:00:00'
            })
    attendance_df = pd.DataFrame(att_data).drop_duplicates(subset=['EmpID', 'Date'])
    if attendance_df.empty:
        attendance_df = pd.DataFrame(columns=['EmpID', 'Date', 'CheckIn', 'CheckOut'])

    # Audit Logs
    audit_logs_df = pd.DataFrame(columns=['Timestamp', 'User', 'Action', 'Details'])

    # Purchase Orders
    po_df = pd.DataFrame(columns=['PO_ID', 'Date', 'Supplier', 'Product', 'Quantity', 'TotalCost', 'Status'])

    # Shifts
    shifts_df = pd.DataFrame(columns=['ShiftID', 'EmpID', 'Store', 'Date', 'StartCash', 'EndCash', 'Status'])

    return {
        'inventory': df,
        'sales': sales_df,
        'dispatches': dispatches_df,
        'requests': requests_df,
        'stores': stores,
        'stores_info': stores_info,
        'products': products,
        'products_info': products_info,
        'employees': employees_df,
        'attendance': attendance_df,
        'audit_logs': audit_logs_df,
        'purchase_orders': po_df,
        'shifts': shifts_df
    }

if 'db' not in st.session_state:
    st.session_state['db'] = initialize_data_optimized()

if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = False
    st.session_state['user_role'] = None
    st.session_state['user_store'] = None

# ==============================================================================
# 3. UI LOGIC (SECURE REWRITE)
# ==============================================================================

def render_admin_dashboard():
    db = st.session_state['db']
    
    tabs = st.tabs(["📊 Sales Tracking", "🚚 Dispatch Monitoring", "🔮 AI Demand Forecasting", "📥 Store Requests Dashboard", "� Inter-Store Transfers", "📦 Supplier & POs", "�👥 HR Management", "💰 Payroll & Audit"])
    
    # TAB 1: Sales Tracking
    with tabs[0]:
        st.subheader("Network Sales Analytics")
        if not db['sales'].empty:
            sales_df = db['sales'].copy()
            sales_df['Date'] = pd.to_datetime(sales_df['Date'])
            
            # Sub-tabs for better organization
            s_tabs = st.tabs(["Overview & Trends", "Store Financial Monitor", "Peak Hour Heatmap", "Dead Stock Analysis"])
            
            with s_tabs[0]:
                colA, colB = st.columns([1, 3])
                with colA:
                    st.markdown("**Date Range Filter**")
                    min_date = sales_df['Date'].min().date()
                    max_date = sales_df['Date'].max().date()
                    start_d = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
                    end_d = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
                    
                # Filter data
                mask = (sales_df['Date'].dt.date >= start_d) & (sales_df['Date'].dt.date <= end_d)
                filtered_sales = sales_df.loc[mask]
                
                if not filtered_sales.empty:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Sales Events", len(filtered_sales))
                    c2.metric("Total Items Sold", filtered_sales['Quantity'].sum())
                    top_store = filtered_sales.groupby('Location')['Quantity'].sum().idxmax()
                    c3.metric("Top Performing Store", top_store)
                    
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Sales by Product**")
                        prod_sales = filtered_sales.groupby('Product')['Quantity'].sum().reset_index()
                        fig1 = px.pie(prod_sales, values='Quantity', names='Product', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                        st.plotly_chart(fig1, width='stretch')
                    with col2:
                        st.markdown("**Sales by Store**")
                        store_sales = filtered_sales.groupby('Location')['Quantity'].sum().reset_index()
                        fig2 = px.bar(store_sales, x='Location', y='Quantity', color='Location', color_discrete_sequence=px.colors.qualitative.Set2)
                        st.plotly_chart(fig2, width='stretch')
                        
                    st.markdown("**Recent Global Sales Logs**")
                    st.dataframe(filtered_sales.sort_values(by='Date', ascending=False).head(15), width='stretch', hide_index=True)
                else:
                    st.warning("No sales found in the selected date range.")
            
            with s_tabs[1]:
                st.markdown("### Store Financial & Revenue Monitor")
                st.markdown("Analyze revenue and specific metrics by store and product.")
                
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    mon_store = st.selectbox("Select Store", db['stores'], key="mon_store")
                    mon_prod = st.selectbox("Select Product", db['products'] + ["All Products"], key="mon_prod")
                with f_col2:
                    m_start_d = st.date_input("From Date", min_date, key="mon_start")
                    m_end_d = st.date_input("To Date", max_date, key="mon_end")
                
                # Filter sales
                s_mask = (sales_df['Date'].dt.date >= m_start_d) & (sales_df['Date'].dt.date <= m_end_d) & (sales_df['Location'] == mon_store)
                if mon_prod != "All Products":
                    s_mask = s_mask & (sales_df['Product'] == mon_prod)
                    
                mon_sales = sales_df.loc[s_mask]
                
                # Get store specific info
                store_employees = db['employees'][ (db['employees']['Store'] == mon_store) | (db['employees']['Store'] == 'All') ]
                num_staff = len(store_employees)
                store_id = db['stores_info'].get(mon_store, 'N/A')
                
                st.divider()
                st.markdown(f"#### Store Profile: {mon_store} (ID: {store_id})")
                m_c1, m_c2, m_c3 = st.columns(3)
                m_c1.metric("Current Staff Count", num_staff)
                
                total_qty = mon_sales['Quantity'].sum() if not mon_sales.empty else 0
                total_rev = mon_sales['Revenue'].sum() if not mon_sales.empty else 0
                
                m_c2.metric("Items Sold", total_qty)
                m_c3.metric("Total Revenue (₹)", f"₹{total_rev:,.2f}")
                
                if not mon_sales.empty:
                    st.dataframe(mon_sales[['Date', 'Product', 'Quantity', 'Revenue']].sort_values(by='Date', ascending=False), hide_index=True, width='stretch')
                else:
                    st.info("No sales data matches the criteria.")
                    
            with s_tabs[2]:
                st.markdown("### Peak Hour Sales Heatmap")
                st.markdown("Identify the busiest times across stores for optimized shift scheduling.")
                
                # Extract Hours
                hm_df = sales_df.copy()
                hm_df['Hour'] = hm_df['Date'].dt.hour
                
                # Count sales per store per hour
                heatmap_data = hm_df.groupby(['Location', 'Hour']).size().reset_index(name='Transactions')
                
                fig_hm = px.density_heatmap(
                    heatmap_data, x="Hour", y="Location", z="Transactions",
                    nbinsx=24, color_continuous_scale="Viridis",
                    title="Transaction Volume by Hour and Location"
                )
                fig_hm.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
                st.plotly_chart(fig_hm, width='stretch')

            with s_tabs[3]:
                st.markdown("### Dead Stock Analytics")
                
                ds_range = st.selectbox("Inactivity Threshold (Days)", [30, 60, 90], index=0)
                cutoff_date = datetime.now() - timedelta(days=ds_range)
                
                # Find all store-product combinations that have NO sales since cutoff
                recent_sales = sales_df[sales_df['Date'] >= cutoff_date]
                sold_items = recent_sales[['Location', 'Product']].drop_duplicates()
                sold_items['Sold_Recently'] = True
                
                inv = db['inventory']
                stores_only = inv[inv['Type'] == 'Store'].copy()
                
                # Merge to find Unsold items
                merged = pd.merge(stores_only, sold_items, on=['Location', 'Product'], how='left')
                dead_stock = merged[merged['Sold_Recently'].isna()]
                
                if not dead_stock.empty:
                    st.warning(f"Found {len(dead_stock)} product allocations with 0 sales in the last {ds_range} days.")
                    st.dataframe(dead_stock[['Location', 'Product', 'Current_Stock', 'Target_Stock']].sort_values(by='Current_Stock', ascending=False), hide_index=True, width='stretch')
                else:
                    st.success(f"Excellent! All inventory lines have seen movement in the last {ds_range} days.")
                    
        else:
            st.info("No sales records available.")

    # TAB 2: Dispatch Monitoring
    with tabs[1]:
        st.subheader("Dispatch Tracking & Verification")
        st.markdown("Monitor stock moving from the Hub to specific retail store locations.")
        dispatches = db['dispatches'].copy()
        
        if not dispatches.empty:
            st.dataframe(dispatches, width='stretch', hide_index=True)
            
            st.markdown("### Update Transfer Status")
            in_transit = dispatches[dispatches['Status'] == 'In-Transit']
            
            if not in_transit.empty:
                # Need to use the original index for update
                in_transit_copy = in_transit.copy()
                in_transit_copy['Display'] = in_transit_copy.apply(lambda row: f"To {row['Destination']} - {row['Quantity']}x {row['Product']}", axis=1)
                
                idx = st.selectbox("Select Dispatch arriving at Store", in_transit_copy.index, format_func=lambda i: in_transit_copy.loc[i, 'Display'])
                
                if st.button("Mark as Delivered & Update Inventory", type="primary"):
                    # Record the status change
                    st.session_state['db']['dispatches'].loc[idx, 'Status'] = 'Delivered'
                    
                    # Target info
                    dest = db['dispatches'].loc[idx, 'Destination']
                    prod = db['dispatches'].loc[idx, 'Product']
                    qty = db['dispatches'].loc[idx, 'Quantity']
                    
                    # Update Store's Current Stock
                    inv = st.session_state['db']['inventory']
                    inv_idx = inv[(inv['Location'] == dest) & (inv['Product'] == prod)].index[0]
                    st.session_state['db']['inventory'].at[inv_idx, 'Current_Stock'] += qty
                    
                    st.success(f"Successfully marked delivered. {dest} inventory updated via Hub dispatch!")
                    st.rerun()
            else:
                st.success("🎉 All dispatched goods have safely arrived at their destinations.")
        else:
            st.info("No dispatches on record yet. AI Forecasting or Store Requests will initialize a dispatch.")

    # TAB 3: AI Demand Forecasting
    with tabs[2]:
        st.subheader("AI Predictor: Urgent Stock Targets")
        st.markdown("This AI-driven module predicts urgent needs based on local deficits and minimum targets.")
        
        inv = db['inventory']
        spokes = inv[inv['Type'] == 'Store'].copy()
        
        # Determine Shortages based on a predictive threshold logic
        spokes['Required'] = np.maximum(0, spokes['Target_Stock'] - spokes['Current_Stock'])
        shortages = spokes[spokes['Required'] > 0].copy()
        
        if shortages.empty:
            st.success("All stores meet or exceed baseline prediction targets.")
        else:
            # Calculate urgency severity score (percentage missing)
            shortages['Deficit_Ratio'] = shortages['Required'] / shortages['Target_Stock']
            # Prioritize largest percentage deficits
            shortages = shortages.sort_values(by='Deficit_Ratio', ascending=False)
            
            shortages['Urgency'] = np.where(shortages['Deficit_Ratio'] > 0.8, "🚨 CRITICAL", 
                                   np.where(shortages['Deficit_Ratio'] > 0.4, "⚠️ HIGH", "NORMAL"))
            
            st.markdown("**AI Prioritized Dispatch Strategy**")
            display_shortages = shortages[['Location', 'Product', 'Current_Stock', 'Target_Stock', 'Required', 'Urgency']]
            st.dataframe(display_shortages, width='stretch', hide_index=True)
            
            st.markdown("### Rapid Dispatch Automation")
            with st.form("quick_dispatch"):
                # Pre-fill with the most critical shortage
                top_priority = shortages.iloc[0]
                q_loc = st.selectbox("Destination Location", db['stores'], index=db['stores'].index(top_priority['Location']))
                q_prod = st.selectbox("Product Target", db['products'], index=db['products'].index(top_priority['Product']))
                q_qty = st.number_input("Units to Dispatch", min_value=1, max_value=1000, value=int(top_priority['Required']))
                
                if st.form_submit_button("Initiate Warehouse Dispatch", type="primary"):
                    # Verify hub has the inventory
                    hub_stock = inv[(inv['Location'] == 'Kompally Hub') & (inv['Product'] == q_prod)]['Current_Stock'].values[0]
                    if hub_stock >= q_qty:
                        # Deduct from Hub
                        hub_idx = inv[(inv['Location'] == 'Kompally Hub') & (inv['Product'] == q_prod)].index[0]
                        st.session_state['db']['inventory'].at[hub_idx, 'Current_Stock'] -= q_qty
                        
                        # Apply to dispatch tracker
                        new_dispatch = pd.DataFrame([{
                            'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'Destination': q_loc,
                            'Product': q_prod,
                            'Quantity': q_qty,
                            'Status': 'In-Transit'
                        }])
                        st.session_state['db']['dispatches'] = pd.concat([db['dispatches'], new_dispatch], ignore_index=True)
                        st.session_state['db']['dispatches'] = st.session_state['db']['dispatches'].reset_index(drop=True)
                        
                        st.success(f"Dispatched {q_qty} units of {q_prod} to {q_loc}!")
                        st.rerun()
                    else:
                        st.error(f"Cannot dispatch! Kompally Hub only has {hub_stock} units of {q_prod}.")

    # TAB 4: Store Requests
    with tabs[3]:
        st.subheader("Store Supply Requests")
        st.markdown("Review and authorize explicit requests submitted by Store Employees.")
        
        reqs = db['requests']
        if not reqs.empty:
            st.dataframe(reqs.sort_values(by='Date', ascending=False), width='stretch', hide_index=True)
            
            pending = reqs[reqs['Status'] == 'Pending']
            if not pending.empty:
                st.markdown("### Action Required")
                
                pending_copy = pending.copy()
                pending_copy['Display'] = pending_copy.apply(lambda row: f"{row['Store']} requests {row['Quantity']}x {row['Product']}", axis=1)
                
                req_idx = st.selectbox("Select Pending Request", pending_copy.index, format_func=lambda i: pending_copy.loc[i, 'Display'])
                
                colA, colB = st.columns(2)
                with colA:
                    if st.button("Approve & Trigger Dispatch", type="primary"):
                        # Get details
                        dest = reqs.loc[req_idx, 'Store']
                        prod = reqs.loc[req_idx, 'Product']
                        qty = reqs.loc[req_idx, 'Quantity']
                        
                        # Verify Hub stock
                        inv = db['inventory']
                        hub_stock = inv[(inv['Location'] == 'Kompally Hub') & (inv['Product'] == prod)]['Current_Stock'].values[0]
                        
                        if hub_stock >= qty:
                            # Update statuses
                            st.session_state['db']['requests'].loc[req_idx, 'Status'] = 'Approved'
                            
                            # Deduct from Hub
                            hub_idx = inv[(inv['Location'] == 'Kompally Hub') & (inv['Product'] == prod)].index[0]
                            st.session_state['db']['inventory'].at[hub_idx, 'Current_Stock'] -= qty
                            
                            # Add to dispatches
                            new_dispatch = pd.DataFrame([{
                                'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                'Destination': dest,
                                'Product': prod,
                                'Quantity': qty,
                                'Status': 'In-Transit'
                            }])
                            st.session_state['db']['dispatches'] = pd.concat([db['dispatches'], new_dispatch], ignore_index=True)
                            
                            st.success(f"Request Approved. Goods have left the warehouse for {dest}.")
                            st.rerun()
                        else:
                            st.error(f"Cannot fulfill request. Hub shortage: Only {hub_stock} units available.")
                with colB:
                    if st.button("Reject Request"):
                        st.session_state['db']['requests'].loc[req_idx, 'Status'] = 'Rejected'
                        st.warning("Request has been denied.")
                        st.rerun()
            else:
                st.success("All employee requests have been handled.")
        else:
            st.info("No communications from the network.")

    # TAB 5: Inter-Store Transfers
    with tabs[4]:
        st.subheader("Direct Peer-to-Peer Store Transfers")
        st.markdown("Rebalance inventory directly between retail locations without routing through the central Hub.")
        
        with st.form("inter_store_transfer"):
            col1, col2, col3 = st.columns(3)
            with col1:
                source_store = st.selectbox("Source (Sending Store)", db['stores'])
            with col2:
                dest_store = st.selectbox("Destination (Receiving Store)", db['stores'], index=1)
            with col3:
                transfer_prod = st.selectbox("Product", db['products'])
                
            transfer_qty = st.number_input("Quantity to Move", min_value=1, max_value=500, value=10)
            
            if st.form_submit_button("Execute Direct Transfer", type="primary"):
                if source_store == dest_store:
                    st.error("Source and Destination cannot be the same.")
                else:
                    inv = st.session_state['db']['inventory']
                    src_idx = inv[(inv['Location'] == source_store) & (inv['Product'] == transfer_prod)].index[0]
                    src_stock = inv.at[src_idx, 'Current_Stock']
                    
                    if src_stock >= transfer_qty:
                        # Deduct from Source
                        st.session_state['db']['inventory'].at[src_idx, 'Current_Stock'] -= transfer_qty
                        
                        # Add to Destination
                        dest_idx = inv[(inv['Location'] == dest_store) & (inv['Product'] == transfer_prod)].index[0]
                        st.session_state['db']['inventory'].at[dest_idx, 'Current_Stock'] += transfer_qty
                        
                        # Add Audit Log
                        audit_log = pd.DataFrame([{
                            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'User': 'admin',
                            'Action': 'INTER_STORE_TRANSFER',
                            'Details': f"Moved {transfer_qty}x {transfer_prod} from {source_store} to {dest_store}"
                        }])
                        st.session_state['db']['audit_logs'] = pd.concat([st.session_state['db']['audit_logs'], audit_log], ignore_index=True)
                        
                        st.success(f"Transfer Complete! {transfer_qty} units of {transfer_prod} moved from {source_store} to {dest_store}.")
                        st.rerun()
                    else:
                        st.error(f"Transfer Failed. {source_store} only has {src_stock} units of {transfer_prod}.")
                        
    # TAB 6: Supplier & PO Management
    with tabs[5]:
        st.subheader("Procurement & Supplier Management")
        st.markdown("Manage Purchase Orders to restock the central Kompally Hub.")
        
        c_po1, c_po2 = st.columns([1, 2])
        
        with c_po1:
            st.markdown("### Create Purchase Order")
            with st.form("new_po_form"):
                supplier_name = st.text_input("Supplier/Vendor Name", value="Global Electronics Ltd.")
                po_prod = st.selectbox("Product Line", db['products'])
                po_qty = st.number_input("Order Quantity", min_value=50, max_value=10000, value=500, step=50)
                unit_cost = st.number_input("Wholesale Unit Cost (₹)", min_value=1.0, value=150.0)
                
                total_cost = po_qty * unit_cost
                st.markdown(f"**Estimated Total:** ₹{total_cost:,.2f}")
                
                if st.form_submit_button("Issue PO to Supplier", type="primary"):
                    new_po_id = f"PO-{np.random.randint(40000, 99999)}"
                    new_po = pd.DataFrame([{
                        'PO_ID': new_po_id,
                        'Date': datetime.now().strftime("%Y-%m-%d"),
                        'Supplier': supplier_name,
                        'Product': po_prod,
                        'Quantity': po_qty,
                        'TotalCost': total_cost,
                        'Status': 'Issued'
                    }])
                    st.session_state['db']['purchase_orders'] = pd.concat([db['purchase_orders'], new_po], ignore_index=True)
                    st.success(f"PO {new_po_id} successfully issued to {supplier_name}.")
                    st.rerun()
                    
        with c_po2:
            st.markdown("### Active Purchase Orders")
            pos = db['purchase_orders']
            
            if not pos.empty:
                st.dataframe(pos.sort_values(by='Date', ascending=False), hide_index=True, width='stretch')
                
                issued_pos = pos[pos['Status'] == 'Issued']
                if not issued_pos.empty:
                    st.markdown("**Receive Goods into Hub**")
                    recv_po = st.selectbox("Select PO to Receive", issued_pos['PO_ID'] + " - " + issued_pos['Product'])
                    
                    if st.button("Confirm Goods Received at Hub"):
                        po_id = recv_po.split(" - ")[0]
                        idx = pos[pos['PO_ID'] == po_id].index[0]
                        
                        # Update status
                        st.session_state['db']['purchase_orders'].at[idx, 'Status'] = 'Received'
                        
                        # Add to Hub Inventory
                        prod = pos.loc[idx, 'Product']
                        qty = pos.loc[idx, 'Quantity']
                        
                        inv = st.session_state['db']['inventory']
                        hub_idx = inv[(inv['Location'] == 'Kompally Hub') & (inv['Product'] == prod)].index[0]
                        st.session_state['db']['inventory'].at[hub_idx, 'Current_Stock'] += qty
                        
                        st.success(f"Goods received! {qty}x {prod} added to Kompally Hub inventory.")
                        st.rerun()
            else:
                st.info("No Purchase Orders currently active.")

    # TAB 7: HR Management (Adding Staff & Soft Delete)
    with tabs[6]:
        st.subheader("Employee Directory & Management")
        employees = db['employees']
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("**Active Workforce**")
            st.dataframe(employees[['EmpID', 'Name', 'Role', 'Store', 'Contact', 'Wage', 'Status']], hide_index=True, width='stretch')
        
        with c2:
            st.markdown("**Action Panel**")
            with st.expander("➕ Onboard New Employee"):
                with st.form("new_employee_form"):
                    n_name = st.text_input("Full Name")
                    n_user = st.text_input("Username")
                    n_pass = st.text_input("Password", type="password")
                    n_role = st.selectbox("Role", ["Employee", "Manager", "Admin"])
                    n_store = st.selectbox("Assigned Store", db['stores'] + ["All"])
                    n_wage = st.number_input("Base Monthly Wage (₹)", min_value=5000)
                    
                    if st.form_submit_button("Register Staff"):
                        if n_name and n_user and n_pass:
                            new_emp_id = f"EMP-{np.random.randint(3000, 9999)}"
                            new_emp = pd.DataFrame([{
                                'EmpID': new_emp_id, 'Name': n_name, 'Username': n_user, 'PasswordHash': hash_password(n_pass),
                                'Contact': f"{n_user}@nexus.com", 'Role': n_role, 'Store': n_store, 'Wage': n_wage, 'Status': 'Active'
                            }])
                            st.session_state['db']['employees'] = pd.concat([employees, new_emp], ignore_index=True)
                            st.success(f"Successfully onboarded {n_name} ({new_emp_id})")
                            st.rerun()
                            
            with st.expander("🛠️ Update / Soft Delete Staff"):
                u_emp = st.selectbox("Select Employee", employees['EmpID'] + " - " + employees['Name'])
                if u_emp:
                    sel_id = u_emp.split(" - ")[0]
                    emp_rec = employees[employees['EmpID'] == sel_id].iloc[0]
                    
                    new_status = st.radio("Account Status", ["Active", "Inactive"], index=0 if emp_rec['Status'] == 'Active' else 1)
                    if st.button("Update Status"):
                        idx = employees[employees['EmpID'] == sel_id].index[0]
                        st.session_state['db']['employees'].at[idx, 'Status'] = new_status
                        
                        # Add audit log
                        audit_log = pd.DataFrame([{
                            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'User': 'admin',
                            'Action': 'STATUS_CHANGE',
                            'Details': f"Changed status of {sel_id} to {new_status}"
                        }])
                        st.session_state['db']['audit_logs'] = pd.concat([st.session_state['db']['audit_logs'], audit_log], ignore_index=True)
                        
                        st.success(f"Status updated to {new_status}")
                        st.rerun()
                        
    # TAB 6: Payroll & Audit Tracking
    with tabs[5]:
        st.subheader("Salaries & Security Operations")
        
        p_c1, p_c2 = st.columns(2)
        with p_c1:
            st.markdown("### Automated Payroll Processing")
            st.markdown("Calculates total hours/days worked based on Check-In logs.")
            
            att = db['attendance']
            if not att.empty:
                # Merge attendance with employee DB to calculate wages
                valid_att = att.dropna(subset=['CheckOut']) # Only completed shifts
                if not valid_att.empty:
                    # Calculate dummy 'days worked' by group counting
                    days_worked = valid_att.groupby('EmpID').size().reset_index(name='Days_Worked')
                    emp_wage = employees[['EmpID', 'Name', 'Role', 'Store', 'Wage']]
                    
                    payroll = pd.merge(days_worked, emp_wage, on='EmpID')
                    # Assume base wage is for 30 days, calculate daily rate
                    payroll['Calculated_Payout'] = (payroll['Wage'] / 30 * payroll['Days_Worked']).astype(int)
                    
                    st.dataframe(payroll[['EmpID', 'Name', 'Role', 'Store', 'Wage', 'Days_Worked', 'Calculated_Payout']], hide_index=True, width='stretch')
                    
                    if st.button("Generate Selected Payslip (PDF Mock)"):
                        st.success("📄 Generating PDF... (Simulated download complete: 'payslip_EMP.pdf')")
                else:
                    st.info("No completed shifts found to calculate payroll.")
            else:
                st.info("No attendance records logged yet.")
                
        with p_c2:
            st.markdown("### Global System Audit Trail")
            st.markdown("Immutable record of manual overrides and sensitive actions.")
            audits = db['audit_logs']
            if not audits.empty:
                st.dataframe(audits.sort_values(by='Timestamp', ascending=False), hide_index=True, width='stretch')
            else:
                st.info("No audit logs recorded yet. Manual inventory changes will appear here.")


def render_employee_dashboard():
    db = st.session_state['db']
    my_store = st.session_state['user_store']
    
    st.markdown(f"### Regional Store Manager: 📍 **{my_store}**")
    
    tabs = st.tabs(["📦 Local Inventory Tracker", "🛒 Daily Sales Input", "📤 RequestHQ Supplies", "⏱️ Attendance & Shifts"])
    
    # TAB 1: Local Inventory
    with tabs[0]:
        st.subheader("Your Real-time Floor Inventory")
        inv = db['inventory']
        my_inv = inv[inv['Location'] == my_store][['Product', 'Current_Stock', 'Target_Stock']].copy()
        
        # Helper for UI
        my_inv['Health'] = np.where(my_inv['Current_Stock'] >= my_inv['Target_Stock'] * 0.8, "🟢 OK",
                           np.where(my_inv['Current_Stock'] >= my_inv['Target_Stock'] * 0.3, "🟡 Monitor", "🔴 Low"))
        
        st.dataframe(my_inv, width='stretch', hide_index=True)
        
        critical = my_inv[my_inv['Health'] == "🔴 Low"]
        if not critical.empty:
            st.warning("⚠️ High Deficit Found. Switch to the 'RequestHQ Supplies' tab to restock.")
                
    # TAB 2: Sales Updates & POS
    with tabs[1]:
        st.subheader("Point of Sale (POS) & Checkout")
        st.markdown("Process transactions, handle returns, and document damaged goods.")
        
        # Mock Barcode Scanner integration
        st.markdown("### 🛒 Rapid Checkout")
        mock_barcode = st.text_input("Scan Barcode (Enter Product Name to mock)", key="barcode_input")
        default_prod = db['products'].index(mock_barcode) if mock_barcode in db['products'] else 0
        
        with st.form("sales_entry"):
            col1, col2 = st.columns([2, 1])
            with col1:
                prod_sold = st.selectbox("Select or verify scanned product line", db['products'], index=default_prod)
            with col2:
                tx_type = st.selectbox("Transaction Type", ["Sale", "Return / Refund", "Damaged / Broken goods"])
                
            qty_sold = st.number_input("Units", min_value=1, max_value=500, value=1)
            
            # Offline Mode Mock
            offline_mode = st.checkbox("Simulate Offline Mode (Network Outage)")
            
            if st.form_submit_button("Submit Transaction", type="primary"):
                # Evaluate available local stock
                inv = st.session_state['db']['inventory']
                inv_idx = inv[(inv['Location'] == my_store) & (inv['Product'] == prod_sold)].index[0]
                current = inv.at[inv_idx, 'Current_Stock']
                
                # Handling Sales
                if tx_type == "Sale":
                    if current >= qty_sold:
                        # Deduct from local inventory
                        st.session_state['db']['inventory'].at[inv_idx, 'Current_Stock'] -= qty_sold
                        
                        tx_record = {
                            'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'Location': my_store,
                            'Product': prod_sold,
                            'Quantity': qty_sold,
                            'Revenue': qty_sold * db['products_info'].get(prod_sold, 0),
                            'Status': 'Cached' if offline_mode else 'Synced'
                        }
                        
                        if offline_mode:
                            if 'offline_cache' not in st.session_state:
                                st.session_state['offline_cache'] = []
                            st.session_state['offline_cache'].append(tx_record)
                            st.warning(f"Network Offline. Sale of {qty_sold}x {prod_sold} cached locally.")
                        else:
                            new_log = pd.DataFrame([tx_record])
                            st.session_state['db']['sales'] = pd.concat([new_log, st.session_state['db']['sales']], ignore_index=True)
                            st.success(f"Sale successful. {qty_sold}x {prod_sold} removed from local stock.")
                        st.rerun()
                    else:
                        st.error(f"Transaction Error: You only have {current} units of {prod_sold} on shelves.")
                
                # Handling Returns & Damages
                else:
                    if tx_type == "Return / Refund":
                        # Add back to inventory for a return
                        st.session_state['db']['inventory'].at[inv_idx, 'Current_Stock'] += qty_sold
                        st.success(f"Return Processed! {qty_sold}x {prod_sold} successfully restocked.")
                    elif tx_type == "Damaged / Broken goods":
                        # Deduct from inventory since it's un-sellable
                        if current >= qty_sold:
                            st.session_state['db']['inventory'].at[inv_idx, 'Current_Stock'] -= qty_sold
                            st.warning(f"Shrinkage logged. {qty_sold}x {prod_sold} removed due to damage.")
                        else:
                            st.error(f"Cannot log {qty_sold} damages, only {current} exist in system.")
                            st.stop()
                            
                    # Audit Trail for returns/damages
                    audit_log = pd.DataFrame([{
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'User': st.session_state.get('user_username', 'employee'),
                        'Action': 'POS_EXCEPTION',
                        'Details': f"{tx_type}: {qty_sold}x {prod_sold} at {my_store}"
                    }])
                    st.session_state['db']['audit_logs'] = pd.concat([st.session_state['db']['audit_logs'], audit_log], ignore_index=True)
                    st.rerun()
                    
        # Offline Cache Sync Interface
        if 'offline_cache' in st.session_state and len(st.session_state['offline_cache']) > 0:
            st.warning(f"🔌 Connection Restored? You have {len(st.session_state['offline_cache'])} unsynced transactions.")
            if st.button("Sync Cached Data to HQ"):
                cached_df = pd.DataFrame(st.session_state['offline_cache'])
                cached_df['Status'] = 'Synced'
                st.session_state['db']['sales'] = pd.concat([cached_df, st.session_state['db']['sales']], ignore_index=True)
                st.session_state['offline_cache'] = [] # Clear out cache
                st.success("All offline transactions successfully synced with HQ database!")
                st.rerun()
                
        st.markdown("**Your Recent Store Sales**")
        my_sales = db['sales'][db['sales']['Location'] == my_store]
        if not my_sales.empty:
            st.dataframe(my_sales.head(10), width='stretch', hide_index=True)
        else:
            st.info("No recorded sales for this shift yet.")

    # TAB 3: Request Supplies
    with tabs[2]:
        st.subheader("Internal Supply Chain Requisition")
        st.markdown("Notify the Admin Hub of critical stock shortages.")
        
        with st.form("supply_request"):
            req_prod = st.selectbox("Product Line", db['products'])
            req_qty = st.number_input("Requested Volume", min_value=1, max_value=2000, value=25)
            
            if st.form_submit_button("Submit Fulfillment Order"):
                new_req = pd.DataFrame([{
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Store': my_store,
                    'Product': req_prod,
                    'Quantity': req_qty,
                    'Status': 'Pending'
                }])
                st.session_state['db']['requests'] = pd.concat([new_req, st.session_state['db']['requests']], ignore_index=True)
                
                st.success(f"Digital requisition filed! Awaiting Hub approval for {req_qty} units.")
                st.rerun()
        
        st.markdown("**Your Pending and History Requests**")
        my_reqs = db['requests'][db['requests']['Store'] == my_store]
        if not my_reqs.empty:
            st.dataframe(my_reqs, width='stretch', hide_index=True)
        else:
            st.info("You haven't requested any items recently.")
            
    # TAB 4: Attendance & Shifts
    with tabs[3]:
        st.subheader("Shift Management & Time Tracking")
        
        # Determine Current Logged In Employee ID
        # (For demo purposes, we infer from their Username, since st.session_state doesn't have EmpID directly yet)
        # We should find EmpID by joining with Employees table based on Username.
        safe_user = sanitize_input(st.session_state.get('user_username', 'employee')) # Fallback for demo
        emp_match = db['employees'][db['employees']['Username'] == safe_user]
        
        if not emp_match.empty:
            my_emp_id = emp_match.iloc[0]['EmpID']
            my_name = emp_match.iloc[0]['Name']
            
            st.markdown(f"**Employee:** {my_name} ({my_emp_id})")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Daily Attendance")
                att = db['attendance']
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                # Check if already checked in today
                today_att = att[(att['EmpID'] == my_emp_id) & (att['Date'] == today_str)]
                
                if today_att.empty:
                    if st.button("⏰ Check In for the Day", type="primary"):
                        new_att = pd.DataFrame([{
                            'EmpID': my_emp_id, 'Date': today_str, 
                            'CheckIn': datetime.now().strftime("%H:%M:%S"), 'CheckOut': None
                        }])
                        st.session_state['db']['attendance'] = pd.concat([att, new_att], ignore_index=True)
                        st.success("Successfully Checked In! Have a great shift.")
                        st.rerun()
                elif pd.isna(today_att.iloc[0]['CheckOut']):
                    st.success(f"Checked In at {today_att.iloc[0]['CheckIn']}")
                    if st.button("🚪 Check Out"):
                        idx = att[(att['EmpID'] == my_emp_id) & (att['Date'] == today_str)].index[0]
                        st.session_state['db']['attendance'].at[idx, 'CheckOut'] = datetime.now().strftime("%H:%M:%S")
                        st.success("Successfully Checked Out. See you tomorrow!")
                        st.rerun()
                else:
                    st.info(f"Shift Completed. Checked In: {today_att.iloc[0]['CheckIn']} | Checked Out: {today_att.iloc[0]['CheckOut']}")
                    
            with c2:
                st.markdown("### Cash Drawer Tracking")
                shifts = db['shifts']
                
                # Find active shift
                active_shift = shifts[(shifts['EmpID'] == my_emp_id) & (shifts['Status'] == 'Active')]
                
                if active_shift.empty:
                    with st.form("start_shift"):
                        start_cash = st.number_input("Starting Register Cash (₹)", min_value=0.0, value=5000.0)
                        if st.form_submit_button("Start Register Shift"):
                            new_shift = pd.DataFrame([{
                                'ShiftID': f"SHF-{np.random.randint(1000,9999)}",
                                'EmpID': my_emp_id, 'Store': my_store, 
                                'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                'StartCash': start_cash, 'EndCash': None, 'Status': 'Active'
                            }])
                            st.session_state['db']['shifts'] = pd.concat([shifts, new_shift], ignore_index=True)
                            st.success("Cash Register Shift Started.")
                            st.rerun()
                else:
                    shift_id = active_shift.iloc[0]['ShiftID']
                    st.info(f"Active Shift: {shift_id} | Started with: ₹{active_shift.iloc[0]['StartCash']}")
                    
                    with st.form("end_shift"):
                        end_cash = st.number_input("Ending Register Cash (₹)", min_value=0.0, value=float(active_shift.iloc[0]['StartCash']))
                        if st.form_submit_button("End Register Shift"):
                            idx = shifts[shifts['ShiftID'] == shift_id].index[0]
                            st.session_state['db']['shifts'].at[idx, 'EndCash'] = end_cash
                            st.session_state['db']['shifts'].at[idx, 'Status'] = 'Completed'
                            st.success(f"Shift Ended. Cash differential recorded.")
                            st.rerun()
                            
            st.markdown("### Your Logged Records")
            st.dataframe(att[att['EmpID'] == my_emp_id].tail(5), hide_index=True, width='stretch')
        else:
            st.error("Employee Profile not found. Please contact Hub HR.")


def main():
    if not st.session_state['auth_status']:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.title("🔒 Nexus Corporate Secure Auth")
            st.markdown("Supply chain logistics portal. Authorized personnel only.")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    is_valid, role, store = login_user(username, password)
                    if is_valid:
                        st.session_state['auth_status'] = True
                        st.session_state['user_role'] = role
                        st.session_state['user_store'] = store
                        st.session_state['user_username'] = username
                        st.success(f"Access granted: {role}. Preparing dashboard...")
                        # Give the success message half a second to show up
                        time.sleep(0.5) 
                        st.rerun()
                    else:
                        st.error("Authentication rejected. Integrity check failed.")
            
            st.info("""
            **Demo Credentials:**
            - **Super Admin (Hub View & HR):** `admin` / `admin123`
            - **Store Manager (Manager View):** `manager1` / `mgr123`
            - **Cashier (POS View):** `employee` / `emp123`
            """)
        return

    # --- MAIN APPLICATION (AUTHENTICATED) ---
    with st.sidebar:
        st.title("Nexus ERP")
        st.markdown(f"**Clearance Level:** {st.session_state['user_role']}")
        st.markdown(f"**Assigned Sector:** {st.session_state['user_store']}")
        st.divider()
        if st.button("Log Off Securely"):
            # Instead of completely wiping dict (which resets the demo data), 
            # we just log the user out so data persists across log-ins during the session.
            st.session_state['auth_status'] = False
            st.session_state['user_role'] = None
            st.session_state['user_store'] = None
            st.rerun()

    st.markdown("<div class='main-header'>Hyderabad Logistics Operations Center</div>", unsafe_allow_html=True)
    st.divider()

    if st.session_state['user_role'] == 'Admin':
        render_admin_dashboard()
    elif st.session_state['user_role'] == 'Manager':
        # Temporarily use the same function until we build a manager specific view
        render_employee_dashboard()
    elif st.session_state['user_role'] == 'Employee':
        render_employee_dashboard()

if __name__ == "__main__":
    main()
