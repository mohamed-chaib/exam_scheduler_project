import requests
import pandas as pd

URL = "http://127.0.0.1:8000"

def check():
    print("--- SIMULATING STUDENT VIEW LOGIC ---")
    
    # 1. Departments
    try:
        r_depts = requests.get(f"{URL}/departments")
        depts = r_depts.json()
        print(f"1. Fetched {len(depts)} Departments from Backend.")
        dept_names = [d["nom"] for d in depts]
        print(f"   Names: {dept_names}")
    except Exception as e:
        print(f"CRITICAL: Failed to fetch departments: {e}")
        return

    # 2. Global Validation
    try:
        r_glob = requests.get(f"{URL}/analytics/validation/global")
        glob_status = r_glob.json().get("status")
        print(f"2. Global Status: '{glob_status}'")
    except Exception as e:
        print(f"CRITICAL: Failed to fetch global status: {e}")
        return

    # 3. Dept Validation
    try:
        r_val = requests.get(f"{URL}/analytics/validation/status")
        val_data = r_val.json()
        print(f"3. Validation Data: {val_data}")
        
        valid_depts = [d["department"] for d in val_data if d["status"] == "Validate"]
        print(f"   -> Validated Depts List: {valid_depts}")
    except Exception as e:
        print(f"CRITICAL: Failed to fetch val status: {e}")
        return

    # 4. Logic Test
    print("\n--- LOGIC TEST ---")
    if glob_status != "Finalized":
        print("RESULT: BLOCKED by Global Lock (Not Finalized).")
    else:
        print("Global Lock is OPEN.")
        if not valid_depts:
            print("RESULT: BLOCKED. Global is Open, but NO departments are validated.")
        else:
            print(f"RESULT: PARTIAL ACCESS. Students in {valid_depts} can see exams.")
            print("Students in other departments are BLOCKED.")

if __name__ == "__main__":
    check()
