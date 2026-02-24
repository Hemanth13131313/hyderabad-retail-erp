# Hyderabad Retail Nexus

**Hyderabad Retail Nexus** is a state-of-the-art Logistic Control Tower built to solve the ₹10L/month stockout problem in the high-velocity retail networks of Hyderabad. It provides an AI-driven, real-time Supply Chain ERP system mimicking a Hub-and-Spoke model, streamlining operations between the main Hub and local retail stores.

The application features a clean, professional, and role-based architecture bridging administrative operations (Admin Hub) and fast point-of-sale updates (Employee Store View).

---

## 🎨 Design Philosophy
The UI relies on a monolithic, monochromatic layout focusing entirely on dense information grouping. This clean design highlights critical data alerts (like stock deficits) and seamlessly blends form with function. It’s strictly modular, keeping Admin and Employee experiences fully independent and cleanly segmented. 

---

## 🚀 Features

- **Role-Based Views**: Securely segmented layouts locking Admin commands to the HQ and Point-of-Sale (POS) capabilities to individual retail locations.
- **Command Center (Admin)**:
  - 📊 **Network Sales Analytics**: Track aggregate sales globally using interactive charts and live event logs.
  - 🚚 **Dispatch Monitoring**: Fully track stock transit events and manually increment destination inventory upon successful delivery.
  - 🔮 **AI Predictor Hub**: Automated dispatch priority logic highlighting critical inventory shortages across the region.
  - 📥 **Store Requests Dashboard**: Real-time review and fulfillment pipeline for inventory requested by Store Managers.
- **Store Dashboard (Employee)**:
  - 📦 **Local Tracker**: Minimalist overview of floor stock with automated health tags.
  - 🛒 **POS Interface**: Quickly capture sales, instantly synchronizing global stock and publishing event logs to HQ.
  - 📤 **Supply Requisitions**: Request rapid fulfillment from the Kompally Hub directly.

---

## 🛠️ Technologies Used

- **Frontend core**: `Streamlit` (Interactive, data-driven web elements)
- **Data Engineering**: `Pandas`, `NumPy` (Optimized vectorized database manipulation)
- **Geospatial Mapping**: `Folium`, `Streamlit-Folium`
- **Data Visualization**: `Plotly`

---

## 📂 File Structure

```text
hyderabad-retail-erp/
│
├── app.py                  # Primary Application (Role-based secure entry point)
├── requirements.txt        # Production Python Dependencies
├── Dockerfile              # Docker Container build instructions
└── README.md               # Application Documentation (You are here)
```

*(Note: Legacy documentation files strictly pertaining to academic assignments or incomplete mock tests have been cleaned up to maintain repository hygiene).*

---

## 💻 Installation

Ensure you have **Python 3.9+** installed on your system. 

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/hyderabad-retail-nexus.git
   cd hyderabad-retail-nexus
   ```

2. **Install Dependencies**
   Install the required core libraries into your virtual environment: 
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Portal**
   Run the Streamlit frontend. This will automatically open `localhost:8501` in your browser.
   ```bash
   streamlit run app.py
   ```

---

## 📚 Usage Guide

The application natively handles authentication inside the UI to grant permissions securely. Upon launching the server:

* **Log in as Admin**:
  * Username: `admin`
  * Password: `admin123`
  * *Purpose*: Global Analytics, automated dispatch logic, map tracking, and approving internal invoices.

* **Log in as Store Employee** (e.g., Hitech City):
  * Username: `employee`
  * Password: `emp123`
  * *Purpose*: Checking your location's shelves, hitting maximum capacity via request submissions, and logging real-time point-of-sale stock deductions.

*All data modifications are handled inside a streamlined `session_state` engine ensuring you don't need to configure a local SQlite proxy just to evaluate the ERP!*
