import requests

URL = "http://127.0.0.1:8000"

def check_status():
    print("--- CHECKING STATUS ---")
    try:
        # Global
        r_glob = requests.get(f"{URL}/analytics/validation/global")
        print(f"Global Status Code: {r_glob.status_code}")
        print(f"Global JSON: {r_glob.json()}")
        
        # Depts
        r_dept = requests.get(f"{URL}/analytics/validation/status")
        print(f"Dept Summary Status Code: {r_dept.status_code}")
        print(f"Dept Summary JSON: {r_dept.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_status()
