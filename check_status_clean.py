import requests
import json

URL = "https://exam-scheduler-test.onrender.com"

def check_status():
    print("--- CHECKING STATUS REPORT ---")
    try:
        # Global
        r_glob = requests.get(f"{URL}/analytics/validation/global")
        if r_glob.status_code == 200:
            print(f"GLOBAL STATUS: {r_glob.json().get('status')}")
        else:
            print(f"GLOBAL ERROR: {r_glob.status_code}")
        
        # Depts
        r_dept = requests.get(f"{URL}/analytics/validation/status")
        if r_dept.status_code == 200:
            data = r_dept.json()
            print(f"DEPT COUNT: {len(data)}")
            for d in data:
                print(f"DEPT: {d['department']} = {d['status']}")
        else:
            print(f"DEPT ERROR: {r_dept.status_code}")
        
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    check_status()
