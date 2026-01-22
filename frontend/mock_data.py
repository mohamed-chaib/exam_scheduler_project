import requests
import streamlit as st

url = "https://exam-scheduler-test.onrender.com"

def login_user(email, password):
    try:
        response = requests.post(f"{url}/auth/login", json={"email": email, "password": password})
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def require_auth(allowed_roles=None):
    if "token" not in st.session_state or not st.session_state.token:
        st.warning("Please log in via the main page to access this tool.")
        st.stop()
    
    if allowed_roles:
        # Check for single role string or list of roles
        if isinstance(allowed_roles, str):
            allowed_roles = [allowed_roles]
            
        if st.session_state.role not in allowed_roles:
            st.error(f"Access Denied: This page is restricted to {', '.join(allowed_roles)}.")
            st.stop()

def generate_schedule(start_date):
    try:
        response = requests.post(f"{url}/examens/generate", params={"start_date": start_date})
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to connect to backend"}
    except Exception as e:
        return {"error": str(e)}

def get_dept_validation(dept_id):
    try:
        response = requests.get(f"{url}/departments/{dept_id}/validation")
        if response.status_code == 200:
            return response.json().get("status")
        return "Pending"
    except:
        return "Pending"

def set_dept_validation(dept_id, status):
    try:
        requests.post(f"{url}/departments/{dept_id}/validation", json={"status": status})
        return True
    except:
        return False

def get_validation_summary():
    try:
        response = requests.get(f"{url}/analytics/validation/status")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_global_validation():
    try:
        response = requests.get(f"{url}/analytics/validation/global")
        if response.status_code == 200:
            return response.json().get("status")
        return "Pending"
    except:
        return "Pending"
        
def set_global_validation(status):
    try:
        requests.post(f"{url}/analytics/validation/global", json={"status": status})
        return True
    except:
        return False

# 1. Departments (7 total)
departments =  requests.get(url+"/departments").json()

# 2. Formations (A distinct set of formations linked to departments)
# Formations have 6-9 modules typically.
formations = requests.get(url+"/formations").json()

# 3. Modules (Linked to Formations)
modules = requests.get(url+"/modules").json()
# 4. Students (Linked to Formations - Inherit modules automatically)
students =  requests.get(url+"/etudiants").json()
# ---------------- RESOURCES ----------------

# Rooms with capacities
# Rooms limited to 20 students max (Exam mode)
rooms = requests.get(url+"/lieu_examen").json()

professors = requests.get(url+"/professeurs").json()


# ---------------- EXAM SCHEDULE ----------------

# Exams are scheduled per MODULE.
exam_schedule = requests.get(url+"/examens").json()

# ---------------- ANALYTICS MOCK DATA ----------------

rooms_usage = requests.get(url+"/analytics/room_usage").json()

department_conflicts = requests.get(url+"/analytics/department_conflicts").json()

professor_workload = requests.get(url+"/analytics/professor_workload").json()