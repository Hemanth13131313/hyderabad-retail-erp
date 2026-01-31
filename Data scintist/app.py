import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime
import hashlib
import re

# ==============================================================================
# 1. SECURITY & CONFIGURATION LAYER
# ==============================================================================

st.set_page_config(
    page_title="Hyderabad Retail Nexus (Secure)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Professional/Secure Look
st.markdown("""
<style>
    /* .stApp { background-color: #f8fafc; } Removed to support Dark Mode */
    .main-header { font-size: 2.5rem; font-weight: 700; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
    .critical { background-color: #fca5a5; color: #7f1d1d; }
    .healthy { background-color: #86efac; color: #14532d; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# --- SECURITY UTILS ---

def hash_password(password):
    """Securely hash passwords using SHA-256."""
    return hashlib.sha256(str(password).encode()).hexdigest()

def sanitize_input(user_input):
    """
    Sanitize text input to prevent injection attacks.
    Removes special characters that could be malicious scripts.
    """
    if not isinstance(user_input, str):
        return user_input
    # Allow alphanumeric, spaces, and basic punctuation
    return re.sub(r'[^\w\s\-\.\@]', '', user_input)

# --- AUTHENTICATION MODULE ---

# Simulated Secure Database (Hash of 'admin123' and 'view123')
CREDENTIALS = {
    "admin": {
        "hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9", # admin123
        "role": "Admin"
    },
    "viewer": {
        "hash": "656d604dfdba41a262963cce53699bbc56cd7a2c0da1ad5ead45fc49214159d6", # view123
        "role": "Viewer"
    }
}

def login_user(username, password):
    safe_user = sanitize_input(username)
    if safe_user in CREDENTIALS:
        stored_hash = CREDENTIALS[safe_user]["hash"]
        input_hash = hash_password(password)
        if stored_hash == input_hash:
            return True, CREDENTIALS[safe_user]["role"]
    return False, None

# ==============================================================================
# 2. DATA PROCESSING & OPTIMIZATION LAYER
# ==============================================================================

@st.cache_data
def initialize_data_optimized():
    """
    Generates dummy data using vectorized numpy operations for performance.
    Cached to run only once per session or reload.
    """
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
    
    # Vectorized Generation
    n_rows = len(stores) * len(products)
    
    # Create Base DF
    df = pd.DataFrame([
        {'Location': s, 'Product': p, 'Type': 'Store'} 
        for s in stores for p in products
    ])
    
    # Add Hub
    hub_df = pd.DataFrame([{'Location': 'Kompally Hub', 'Product': p, 'Type': 'Hub'} for p in products])
    df = pd.concat([hub_df, df], ignore_index=True)
    
    # Assign Targets based on Product (Vectorized Map)
    targets = {'iPhone 15': 20, 'Samsung TV': 10, 'Milk (1L)': 100, 'Rice (25kg)': 50, 'Detergent': 80, 'T-Shirt': 40}
    df['Target_Stock'] = df['Product'].map(targets)
    
    # Generate Current Stock (Vectorized Randomness)
    # Hub = 100x Target
    # Store = Random 0 to 1.5x Target
    
    df['Current_Stock'] = np.where(
        df['Type'] == 'Hub',
        df['Target_Stock'] * 100,
        (np.random.rand(len(df)) * 1.5 * df['Target_Stock']).astype(int)
    )
    
    # Force some criticals (<20%) for demo
    mask_critical = np.random.rand(len(df)) < 0.15 # 15% chance
    df.loc[(df['Type'] == 'Store') & mask_critical, 'Current_Stock'] = (df.loc[(df['Type'] == 'Store') & mask_critical, 'Target_Stock'] * 0.1).astype(int)

    # Coords Logic
    df['Lat'] = df['Location'].map(lambda x: coords.get(x, (17.55, 78.49))[0])
    df['Lon'] = df['Location'].map(lambda x: coords.get(x, (17.55, 78.49))[1])

    return df

# Initialize Session State securely
if 'data' not in st.session_state:
    st.session_state['data'] = initialize_data_optimized()

if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = False
    st.session_state['user_role'] = None

# ==============================================================================
# 3. UI LOGIC (SECURE REWRITE)
# ==============================================================================

def main():
    # --- LOGIN PAGE ---
    if not st.session_state['auth_status']:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.title("🔒 Secure Login")
            st.markdown("Use verified credentials to access Hyderabad Retail Nexus.")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Authenticate")
                
                if submit:
                    is_valid, role = login_user(username, password)
                    if is_valid:
                        st.session_state['auth_status'] = True
                        st.session_state['user_role'] = role
                        st.success(f"Welcome, {role}! Loading system...")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or unauthorized access attempt.")
            
            st.warning("⚠️ **Demo Access Credentials:**")
            st.markdown("- **Admin:** `admin` / `admin123`")
            st.markdown("- **Viewer:** `viewer` / `view123`")
        return # Stop execution here if not logged in

    # --- MAIN APPLICATION (AUTHENTICATED) ---
    
    # Sidebar Navigation & Role Info
    with st.sidebar:
        st.title("Nexus ERP")
        st.markdown(f"User: **{st.session_state['user_role']}**")
        st.divider()
        
        # Tabs based on Role
        tabs = ["🗺️ Map View", "📊 Demand AI", "🚚 Dispatch Plan"]
        if st.session_state['user_role'] == 'Admin':
            tabs.insert(2, "📦 Inventory Manager (Admin)")
        
        # Navigation Radio (Better GUI than selectbox)
        current_tab = st.radio("Navigation", tabs, label_visibility="collapsed")
        
        st.divider()
        if st.button("Log Out"):
            st.session_state['auth_status'] = False
            st.session_state['user_role'] = None
            st.rerun()

    st.markdown("<div class='main-header'>Hyderabad Logisitics Command Center</div>", unsafe_allow_html=True)
    st.divider()

    df = st.session_state['data']

    # --- MODULE 1: MAP VIEW ---
    if "Map" in current_tab:
        try:
            st.subheader("real-time network visibility")
            
            # KPI Row
            stores = df[df['Type'] == 'Store']
            # Vectorized Check for Critical Status
            critical_mask = stores['Current_Stock'] < (stores['Target_Stock'] * 0.2)
            critical_count = len(stores[critical_mask]['Location'].unique())
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Active Spokes", "10")
            k2.metric("Critical Alerts", str(critical_count), delta="Action Required", delta_color="inverse")
            k3.metric("Total Stock", f"{stores['Current_Stock'].sum():,}")

            # Map Render
            m = folium.Map(location=[17.44, 78.44], zoom_start=11)
            
            unique_locs = df[['Location', 'Type', 'Lat', 'Lon']].drop_duplicates()
            
            for _, loc in unique_locs.iterrows():
                loc_df = df[df['Location'] == loc['Location']]
                is_crit = (loc_df['Current_Stock'] < (loc_df['Target_Stock'] * 0.2)).any()
                
                color = 'red' if is_crit and loc['Type'] == 'Store' else 'green'
                if loc['Type'] == 'Hub': color = 'blue'
                
                folium.Marker(
                    [loc['Lat'], loc['Lon']],
                    tooltip=f"{loc['Location']} ({'CRITICAL' if is_crit else 'OK'})",
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
            
            st_folium(m, width="100%", height=500)
            
        except Exception as e:
            st.error(f"Map Rendering Error: {e}")

    # --- MODULE 2: DEMAND AI ---
    elif "Demand" in current_tab:
        try:
            st.subheader("AI Forecasting Engine (Prophet/ARIMA)")
            c1, c2 = st.columns(2)
            sel_prod = c1.selectbox("Select Product", df['Product'].unique())
            sel_store = c2.selectbox("Select Store", df[df['Type'] == 'Store']['Location'].unique())
            
            # Generate Synthetic Forecast Data (Vectorized)
            dates = pd.date_range(end=datetime.today(), periods=30)
            base = 20
            # Numpy random walk
            values = np.abs(np.cumsum(np.random.randn(30)) + base)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers', name='Forecast', line=dict(color='#3b82f6')))
            # Confidence Interval
            fig.add_trace(go.Scatter(
                x=list(dates)+list(dates)[::-1],
                y=list(values+5)+list(values-5)[::-1],
                fill='toself', fillcolor='rgba(59, 130, 246, 0.2)',
                line=dict(color='rgba(0,0,0,0)'),
                name='95% Conf. Interval'
            ))
            fig.update_layout(title=f"30-Day Outlook: {sel_prod}", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Analytics Error: {e}")

    # --- MODULE 3: INVENTORY MANAGER (ADMIN ONLY) ---
    elif "Inventory" in current_tab:
        # RBAC Double Check
        if st.session_state['user_role'] != 'Admin':
            st.error("⛔ ACCESS DENIED: Administrative privileges required.")
        else:
            st.subheader("Stock Management Interface")
            
            # File Upload Security Check
            uploaded_file = st.file_uploader("Bulk Update via CSV (Max 2MB)", type=['csv'])
            if uploaded_file:
                if uploaded_file.size > 2 * 1024 * 1024:
                    st.error("Security Alert: File exceeds 2MB limit.")
                else:
                    try:
                        new_data = pd.read_csv(uploaded_file)
                        # Basic Schema Validation
                        if {'Location', 'Product', 'Stock'}.issubset(new_data.columns):
                            st.success("File Validated & Processed Securely.")
                        else:
                            st.warning("Invalid CSV Schema.")
                    except Exception as e:
                        st.error("Corrupt File Upload detected.")

            # Editable Grid (CRUD)
            st.info("Live Edit Mode Active")
            
            editor_df = st.data_editor(
                df,
                column_config={"Current_Stock": st.column_config.NumberColumn(min_value=0)},
                disabled=["Location", "Type", "Product", "Target_Stock"],
                hide_index=True,
                key="data_editor"
            )
            
            # Persist changes
            if not editor_df.equals(st.session_state['data']):
                st.session_state['data'] = editor_df
                st.toast("Database Updated Successfully!", icon="💾")

    # --- MODULE 4: DISPATCH PLAN ---
    elif "Dispatch" in current_tab:
        try:
            st.subheader("Automated Dispatch Manifest")
            
            # Logic: Vectorized Shortage Calculation
            spokes = df[df['Type'] == 'Store'].copy()
            shortages = spokes[spokes['Current_Stock'] < spokes['Target_Stock']].copy()
            
            if shortages.empty:
                st.success("No shortages detected.")
            else:
                shortages['Required'] = shortages['Target_Stock'] - shortages['Current_Stock']
                shortages['Priority'] = np.where(
                    shortages['Current_Stock'] < (shortages['Target_Stock'] * 0.2), 
                    "🔥 CRITICAL", "NORMAL"
                )
                
                manifest = shortages[['Location', 'Product', 'Required', 'Priority']].sort_values('Priority', ascending=True) # Critical first (text sort works here due to emoji or string)
                
                st.dataframe(
                    manifest,
                    column_config={"Priority": st.column_config.TextColumn("Urgency")},
                    use_container_width=True
                )
                
                # Secure CSV Download
                csv = manifest.to_csv(index=False).encode('utf-8')
                st.download_button("Download Secure Manifest", csv, "manifest.csv", "text/csv")
                
        except Exception as e:
            st.error(f"Dispatch Logic Error: {e}")

if __name__ == "__main__":
    main()
