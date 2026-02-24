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
CREDENTIALS = {
    "admin": {
        "hash": hash_password("admin123"),
        "role": "Admin",
        "store": "All"
    },
    "employee": {
        "hash": hash_password("emp123"),
        "role": "Employee",
        "store": "Hitech City"
    }
}

def login_user(username, password):
    safe_user = sanitize_input(username)
    if safe_user in CREDENTIALS:
        if CREDENTIALS[safe_user]["hash"] == hash_password(password):
            return True, CREDENTIALS[safe_user]["role"], CREDENTIALS[safe_user]["store"]
    return False, None, None

# ==============================================================================
# 2. DATA PROCESSING & OPTIMIZATION LAYER
# ==============================================================================

def initialize_data_optimized():
    stores = ['Hitech City', 'Banjara Hills', 'Gachibowli', 'Secunderabad', 'Uppal', 
              'Jubilee Hills', 'Madhapur', 'Kukatpally', 'Begumpet', 'Charminar']
    products = ['iPhone 15', 'Samsung TV', 'Milk (1L)', 'Rice (25kg)', 'Detergent', 'T-Shirt']
    
    # Coordinates mapping
    coords = {
        'Hitech City': (17.44, 78.38), 'Banjara Hills': (17.41, 78.43),
        'Gachibowli': (17.44, 78.34), 'Secunderabad': (17.43, 78.50),
        'Uppal': (17.39, 78.56), 'Jubilee Hills': (17.42, 78.40),
        'Madhapur': (17.45, 78.39), 'Kukatpally': (17.48, 78.40),
        'Begumpet': (17.44, 78.46), 'Charminar': (17.36, 78.47)
    }
    
    df = pd.DataFrame([{'Location': s, 'Product': p, 'Type': 'Store'} for s in stores for p in products])
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
            'Quantity': qty
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

    return {
        'inventory': df,
        'sales': sales_df,
        'dispatches': dispatches_df,
        'requests': requests_df,
        'stores': stores,
        'products': products
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
    
    tabs = st.tabs(["📊 Sales Tracking", "🚚 Dispatch Monitoring", "🔮 AI Demand Forecasting", "📥 Store Requests Dashboard"])
    
    # TAB 1: Sales Tracking
    with tabs[0]:
        st.subheader("Network Sales Analytics")
        if not db['sales'].empty:
            sales_df = db['sales'].copy()
            sales_df['Date'] = pd.to_datetime(sales_df['Date'])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales Events", len(sales_df))
            c2.metric("Total Items Sold", sales_df['Quantity'].sum())
            top_store = sales_df.groupby('Location')['Quantity'].sum().idxmax()
            c3.metric("Top Performing Store", top_store)
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Sales by Product**")
                prod_sales = sales_df.groupby('Product')['Quantity'].sum().reset_index()
                fig1 = px.pie(prod_sales, values='Quantity', names='Product', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig1, width='stretch')
            with col2:
                st.markdown("**Sales by Store**")
                store_sales = sales_df.groupby('Location')['Quantity'].sum().reset_index()
                fig2 = px.bar(store_sales, x='Location', y='Quantity', color='Location', color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig2, width='stretch')
                
            st.markdown("**Recent Global Sales Logs**")
            st.dataframe(sales_df.sort_values(by='Date', ascending=False).head(15), width='stretch', hide_index=True)
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


def render_employee_dashboard():
    db = st.session_state['db']
    my_store = st.session_state['user_store']
    
    st.markdown(f"### Regional Store Manager: 📍 **{my_store}**")
    
    tabs = st.tabs(["📦 Local Inventory Tracker", "🛒 Daily Sales Input", "📤 RequestHQ Supplies"])
    
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
                
    # TAB 2: Sales Updates
    with tabs[1]:
        st.subheader("Point of Sale (POS) Log")
        st.markdown("Record items purchased by customers to sync back with HQ.")
        
        with st.form("sales_entry"):
            prod_sold = st.selectbox("Product Profile", db['products'])
            qty_sold = st.number_input("Units Sold", min_value=1, max_value=500, value=1)
            
            if st.form_submit_button("Finalize Sale", type="primary"):
                # Evaluate available local stock
                inv = st.session_state['db']['inventory']
                inv_idx = inv[(inv['Location'] == my_store) & (inv['Product'] == prod_sold)].index[0]
                current = inv.at[inv_idx, 'Current_Stock']
                
                if current >= qty_sold:
                    # Deduct from local inventory
                    st.session_state['db']['inventory'].at[inv_idx, 'Current_Stock'] -= qty_sold
                    
                    # Store new sale log
                    new_log = pd.DataFrame([{
                        'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'Location': my_store,
                        'Product': prod_sold,
                        'Quantity': qty_sold
                    }])
                    st.session_state['db']['sales'] = pd.concat([new_log, st.session_state['db']['sales']], ignore_index=True)
                    
                    st.success(f"Sale successful. {qty_sold}x {prod_sold} removed from local stock.")
                    st.rerun()
                else:
                    st.error(f"Transaction Error: You only have {current} units of {prod_sold} on shelves.")
                    
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
                        st.success(f"Access granted: {role}. Preparing dashboard...")
                        # Give the success message half a second to show up
                        time.sleep(0.5) 
                        st.rerun()
                    else:
                        st.error("Authentication rejected. Integrity check failed.")
            
            # Simple demo helper
            st.info("""
            **Demo Credentials:**
            - **Admin (Hub View):** `admin` / `admin123`
            - **Employee (Store View):** `employee` / `emp123`
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
    elif st.session_state['user_role'] == 'Employee':
        render_employee_dashboard()

if __name__ == "__main__":
    main()
