# Hyderabad Retail Nexus: AI-Driven Supply Chain ERP

![Banner Placeholder](https://via.placeholder.com/1000x300?text=Hyderabad+Retail+Nexus+Dashboard)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

## 🎯 The Business Problem
**"Solving the ₹10L/month stockout problem."**

In Hyderabad's fast-paced retail sector, manual inventory management leads to two critical failures: **Stockouts** (Lost Revenue) and **Overstocking** (Wasted Capital). Managing supply chains across a Hub-and-Spoke network using spreadsheets is inefficient, error-prone, and lacks predictive capability.

**Hyderabad Retail Nexus** solves this by acting as a "Logistics Control Tower," integrating real-time visibility, AI-driven demand forecasting, and automated dispatch planning into a single glass-pane interface.

## ✨ Key Features

-   **🗺️ Command Center (Map View)**: 
    -   Real-time Folium map centered on Hyderabad.
    -   Visualizes the **Kompally Hub** + 10 Retail Spokes.
    -   **Pulsing Red Markers** instantly identify stores with critical inventory levels (<20%).

-   **📊 Demand Intelligence Engine**:
    -   Interactive Plotly charts for product-level analytics.
    -   **AI Forecasting**: Uses historic trends to predict demand for the next 30 days.
    -   Includes Confidence Intervals to help managers assess risk.

-   **📦 Live Inventory Management**:
    -   **CRUD Operations**: Edit stock levels directly in the dashboard (simulating stock corrections).
    -   **Add Products**: Seamlessly introduce new SKUs to the entire network.
    -   Robust State Management guarantees data persistence during sessions.

-   **🚚 Automated Dispatch Planner**:
    -   Eliminates guesswork for logistics managers.
    -   Auto-generates a prioritized **Manifest** (High/Medium/Low urgency).
    -   One-click **CSV Export** for truck drivers.

## 🛠️ Installation & Setup

Follow these steps to deploy the ERP system locally:

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/hyderabad-retail-nexus.git
    cd hyderabad-retail-nexus
    ```

2.  **Install Dependencies**
    Ensure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    Launch the Streamlit dashboard:
    ```bash
    python -m streamlit run app.py
    ```

4.  **Access the Dashboard**
    Open your browser and navigate to `http://localhost:8501`.

## 📂 Project Structure

```text
hyderabad-retail-nexus/
├── app.py                     # Main Application (Single-file Entry Point)
├── requirements.txt           # Python Project Dependencies
├── data/
│   └── raw/                   # Generated Datasets (CSV)
├── src/                       # Backend Logic Modules
│   ├── generate_data.py       # Legacy Data Generator
│   ├── inventory_system.py    # Core Calculation Engines
│   └── models.py              # Forecasting Models (ARIMA/Prophet)
└── README.md                  # Project Documentation
```

## 🚀 Future Roadmap

-   [ ] **Cloud Integration**: Migrate local CSV storage to **Cloud SQL / PostgreSQL** for multi-user concurrency.
-   [ ] **Dockerization**: Create a `Dockerfile` for seamless containerized deployment on AWS/Azure.
-   [ ] **Advanced AI**: Integrate **Prophet** for seasonality-aware forecasting (Diwali spikes, etc.) in the live dashboard.
-   [ ] **Authentication**: Add User Login (Admin vs. Store Manager roles).

---
*Built with ❤️ for Hyderabad's Retail Ecosystem.*
