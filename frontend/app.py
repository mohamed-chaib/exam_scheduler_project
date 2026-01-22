import streamlit as st
from mock_data import login_user

st.set_page_config(
    page_title="Exam Scheduling System",
    layout="wide"
)

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.user_email = None
    st.session_state.department_id = None

def login_form():
    st.title("🔐 Login Portal")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Please authenticate to access the system")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if email and password:
                with st.spinner("Authenticating..."):
                    data = login_user(email, password)
                    if data:
                        st.session_state.token = data["access_token"]
                        st.session_state.role = data["role"]
                        st.session_state.user_email = email
                        st.session_state.department_id = data.get("department_id")
                        st.success(f"Welcome back, {data['role'].upper()}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
            else:
                st.warning("Please fill in all fields")

if not st.session_state.token:
    login_form()
    st.markdown("---")
    st.info("Authorized Personnel Only: Dean, Exam Admin, Head of Department")
    st.stop()
    
# LOGGED IN VIEW
st.sidebar.success(f"Logged in as: {st.session_state.role}")
if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.session_state.role = None
    st.rerun()

st.title("📘 Exam Scheduling System")
st.markdown(f"""
Welcome **{st.session_state.user_email}**!

You have access to the **{st.session_state.role.replace('_', ' ').title()}** dashboard.
Use the sidebar to navigate to your specific tools.
""")

# Optional: Add role-specific information or restrictions here
if st.session_state.role == "student":
    st.warning("Students should use the generic view.")
