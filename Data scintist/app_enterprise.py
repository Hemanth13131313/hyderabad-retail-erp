import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Define layout first
st.set_page_config(page_title="Retail ERP - Executive Dashboard", page_icon="🏢", layout="wide")

# --- CUSTOM CSS FOR DARK/NEON/SAAS LOOK ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background-color: #1a1e25;
        border: 1px solid #2d333b;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="metric-container"] label {
        color: #9ca3af; /* muted text */
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-weight: 700;
        font-size: 24px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] svg {
        fill: #4ade80; /* green arrow */
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f3f4f6;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] {
        color: #9ca3af;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #2563eb;
        color: white;
    }
    
    /* Tables */
    div[data-testid="stDataFrame"] {
        background-color: #1a1e25;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_enterprise_data():
    path = os.path.join(os.getcwd(), 'data', 'raw', 'walmart_enterprise_data.csv')
    if not os.path.exists(path):
        st.error("Data not found. Please run src/generate_enterprise_data.py")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_enterprise_data()

# Header
col_logo, col_title = st.columns([1, 6])
with col_title:
    st.title("CITY-WIDE RETAIL ERP SYSTEM")
    st.markdown("**Executive Dashboard | Hyderabad Network**")

st.divider()

if not df.empty:
    latest_date = df['Date'].max()
    today_df = df[df['Date'] == latest_date]
    prev_date = latest_date - pd.Timedelta(days=1)
    prev_df = df[df['Date'] == prev_date]

    # --- 1. CEO's HEADER (KPIs) ---
    st.subheader("Start of Day Snapshot")
    
    # Calculate KPIs
    total_rev = today_df['Revenue'].sum()
    prev_rev = prev_df['Revenue'].sum()
    rev_delta = float(total_rev - prev_rev)
    
    active_inv = (today_df['Current_Stock'] * today_df['Price']).sum()
    prev_inv = (prev_df['Current_Stock'] * prev_df['Price']).sum()
    inv_delta = float(active_inv - prev_inv)

    # Critical Stockouts (Stock < Target * 0.2)
    critical_df = today_df[today_df['Current_Stock'] < (today_df['Target_Stock'] * 0.2)]
    # Filter out Warehouse from critical count as its target isn't same
    critical_stores = critical_df[critical_df['Location_Type'] == 'Store']
    stockouts = len(critical_stores)
    
    # Replenishment Cost (Cost to refill to target)
    # Assumption: Cost is 70% of Price
    replenish_cost = ((critical_stores['Target_Stock'] - critical_stores['Current_Stock']) * critical_stores['Price'] * 0.7).sum()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Daily Revenue", f"₹{total_rev:,.0f}", delta=f"{rev_delta:,.0f}")
    kpi2.metric("Inventory Asset Value", f"₹{active_inv:,.0f}", delta=f"{inv_delta:,.0f}")
    kpi3.metric("Critical SKU Alerts", f"{stockouts}", delta="Needs Attention" if stockouts > 0 else "Stable", delta_color="inverse")
    kpi4.metric("Est. Replenishment Cost", f"₹{replenish_cost:,.0f}", delta="Urgent" if replenish_cost > 100000 else "Normal", delta_color="inverse")
    
    st.divider()

    # --- TABS ---
    tab_heat, tab_drill, tab_dist = st.tabs(["🔥 Inventory Heatmap", "📊 Drill-Down Analytics", "🚛 Smart Distributor"])

    # --- 2. INVENTORY HEATMAP ---
    with tab_heat:
        st.subheader("City-Wide Inventory Health Matrix")
        
        # Aggregate Stock Health per Store per Category
        # Score: 0 (Critical) to 100 (Healthy)
        # We define Health as Current / Target. Capped at 1.0 (100%).
        
        heat_data = today_df[today_df['Location_Type'] == 'Store'].copy()
        heat_data['Fill_Rate'] = heat_data['Current_Stock'] / heat_data['Target_Stock']
        
        pivot_heat = heat_data.pivot_table(index='Category', columns='Location_Name', values='Fill_Rate', aggfunc='mean')
        
        # Plotly Heatmap
        fig_heat = go.Figure(data=go.Heatmap(
            z=pivot_heat.values,
            x=pivot_heat.columns,
            y=pivot_heat.index,
            colorscale=[[0, 'red'], [0.5, 'yellow'], [1, '#4ade80']], # Red to Green
            zmin=0, zmax=1.2
        ))
        
        fig_heat.update_layout(
            title="Real-Time Stock Health (Red = Critical, Green = Healthy)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # --- 3. DRILL-DOWN ANALYTICS ---
    with tab_drill:
        st.subheader("Deep Dive Analytics")
        
        d_col1, d_col2 = st.columns([1, 3])
        
        with d_col1:
            st.markdown("### Filters")
            sel_store = st.selectbox("Select Store", sorted(today_df[today_df['Location_Type'] == 'Store']['Location_Name'].unique()))
            
            # Filter categories available in that store
            avail_cats = today_df[today_df['Location_Name'] == sel_store]['Category'].unique()
            sel_cat = st.selectbox("Select Category", sorted(avail_cats))
            
            # Filter Product
            avail_prods = today_df[(today_df['Location_Name'] == sel_store) & (today_df['Category'] == sel_cat)]['Product_Name'].unique()
            sel_prod = st.radio("Select Product", sorted(avail_prods))
            
        with d_col2:
            st.markdown(f"### Forecast vs Actual: {sel_prod}")
            
            # Get History
            hist_df = df[(df['Location_Name'] == sel_store) & (df['Product_Name'] == sel_prod)].sort_values('Date')
            
            # Plot
            fig_drill = px.line(hist_df, x='Date', y='Sales_Qty', title=f"Sales Velocity: {sel_prod} @ {sel_store}")
            fig_drill.update_traces(line_color='#2563eb', line_width=3)
            
            # Add 'Forecast' (Mocking a simple 7-day forecast line extending from last point)
            # Just visualizing a trend line for the 'Future' feel
            last_date = hist_df['Date'].max()
            last_val = hist_df['Sales_Qty'].iloc[-1]
            future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 8)]
            # Mock forecast: average of last 7 days
            forecast_val = hist_df['Sales_Qty'].tail(7).mean()
            future_vals = [forecast_val] * 7
            
            fig_drill.add_trace(go.Scatter(x=future_dates, y=future_vals, mode='lines', name='AI Forecast', line=dict(dash='dash', color='#4ade80')))
            
            fig_drill.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#2d333b')
            )
            
            st.plotly_chart(fig_drill, use_container_width=True)

    # --- 4. SMART DISTRIBUTOR ---
    with tab_dist:
        st.subheader("🚛 Recommended Dispatch Plan (AI Optimized)")
        
        # Logic: 
        # Source = Shamirpet Central Warehouse
        # Dest = Any store with Critical Stock
        # Qty = Target - Current
        # Priority = High if stock < 10%
        
        if not critical_stores.empty:
            dispatch_plan = []
            
            for _, row in critical_stores.iterrows():
                shortage = row['Target_Stock'] - row['Current_Stock']
                priority = "HIGH" if row['Current_Stock'] < (row['Target_Stock'] * 0.1) else "MEDIUM"
                
                dispatch_plan.append({
                    'Source_Warehouse': 'Shamirpet Central',
                    'Destination_Store': row['Location_Name'],
                    'SKU': row['Product_Name'],
                    'Qty_Needed': int(shortage),
                    'Priority_Level': priority
                })
            
            dispatch_df = pd.DataFrame(dispatch_plan)
            
            # Sort by Priority
            dispatch_df['p_rank'] = dispatch_df['Priority_Level'].map({'HIGH': 0, 'MEDIUM': 1})
            dispatch_df = dispatch_df.sort_values('p_rank').drop('p_rank', axis=1)
            
            # Highlight function
            def highlight_priority(row):
                return ['background-color: #7f1d1d; color: white' if row['Priority_Level'] == 'HIGH' else '' for _ in row]
            
            st.dataframe(dispatch_df.style.apply(highlight_priority, axis=1), use_container_width=True)
            
            if st.button("🚀 Approve & Dispatch All"):
                st.success("Dispatch Orders generated and sent to Warehouse Logistics API.")
                st.balloons()
        else:
            st.success("Network health is optimal. No immediate dispatches required.")
