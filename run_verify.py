# Run the application to verify the flow
import subprocess

def run_it():
    print("Please follow the manual verification plan in Implementation Plan.")
    print("1. Log in as Super Admin and create a new Store Manager and Cashier.")
    print("2. Log in as the Cashier, start a shift, check in, do a mock 'Offline' sale, and log damage.")
    print("3. Check out the Cashier shift.")
    print("4. Log back in as Super Admin to review the Audit Log and Payroll calculation for the Cashier.")
    print("5. Review the Peak Hour Heatmap and Dead Stock analytics.")
    
    print("\nStarting the app now...")
    subprocess.run(["streamlit", "run", "c:/Users/heman/OneDrive/Documents/PR/data analyist/hyderabad-retail-erp/app.py"])

if __name__ == "__main__":
    run_it()
