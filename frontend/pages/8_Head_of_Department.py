import streamlit as st
import pandas as pd
from mock_data import (
    exam_schedule,
    modules,
    formations,
    departments,
    rooms,
    professors,
    department_conflicts,
    require_auth,
    get_dept_validation,
    set_dept_validation
)

st.set_page_config(layout="wide")
require_auth(["head_of_dept", "admin"])

st.title("🎓 Head of Department")



# ---------------- PREPARE DATA ----------------
# Load raw data
df_exams = pd.DataFrame(exam_schedule)
df_modules = pd.DataFrame(modules)
df_formations = pd.DataFrame(formations)
df_depts = pd.DataFrame(departments)
df_rooms = pd.DataFrame(rooms)
df_profs = pd.DataFrame(professors)

# Joins
master_df = pd.merge(df_exams, df_modules, left_on="module_id", right_on="id")
# Join formations with suffix to avoid 'name' collision
master_df = pd.merge(master_df, df_formations, left_on="formation_id", right_on="id", suffixes=("", "_form"))
# Join depts with suffix
master_df = pd.merge(master_df, df_depts, left_on="dept_id", right_on="id", suffixes=("", "_dept"))
# Join rooms with suffix
master_df = pd.merge(master_df, df_rooms, left_on="salle_id", right_on="id", suffixes=("", "_salle"))
# Join profs with suffix
master_df = pd.merge(master_df, df_profs, left_on="prof_id", right_on="id", suffixes=("", "_prof"))

# Rename columns for clear usage
master_df = master_df.rename(columns={
    "nom_dept": "Department",
    "nom_form": "Formation",
    "nom": "Module",
    "nom_salle": "Room",
    "nom_prof": "Professor",
    "date_heure": "Date",
    "duree_minutes": "Duration"
})
master_df["Time"] = pd.to_datetime(master_df["Date"]).dt.time
master_df["Date"] = pd.to_datetime(master_df["Date"]).dt.date


# ---------------- DEPARTMENT SELECTION ----------------
st.sidebar.header("Configuration")

# Filter list based on logged-in user
if st.session_state.role == "head_of_dept" and st.session_state.department_id:
    # Get department name from df_depts
    try:
        user_dept_name = df_depts[df_depts["id"] == st.session_state.department_id]["nom"].iloc[0]
        dept_list = [user_dept_name]
    except:
        st.error("Error identifying your department.")
        dept_list = []
else:
    dept_list = sorted(master_df["Department"].unique().tolist())

selected_dept = st.sidebar.selectbox("Select your Department", dept_list)

# Filter data for this department
dept_df = master_df[master_df["Department"] == selected_dept]

st.subheader(f"Department Management: {selected_dept}")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["✅ Validation", "📊 Statistics", "⚠️ Conflicts by Formation"])

with tab1:
    st.header("Timetable Validation")
    
    st.dataframe(
        dept_df[["Formation", "Module", "Date", "Time", "Room", "Professor", "Duration"]].sort_values(["Date", "Time"]),
        use_container_width=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Please review the schedule slots above.")
    
    with col2:
        # Get Dept ID
        try:
            current_dept_id = int(df_depts[df_depts["nom"] == selected_dept]["id"].iloc[0])
            
            # Fetch current status
            current_status = get_dept_validation(current_dept_id)
            
            # Map API status to UI options
            # Backend uses "Pending", "Validated", "Rejected" ? Wait, model default is "Pending"
            # Logic in set_validation_status uses update.status directly. 
            # So if I send "Validate", it saves "Validate".
            # UI options: ["Pending", "Validate", "Reject"]
            
            options = ["Pending", "Validate", "Reject"]
            
            # Resolve current status to index
            index = 0
            if current_status in options:
                index = options.index(current_status)
            
            status = st.radio("Head of Department Decision", options, index=index, horizontal=True, key=f"status_{selected_dept}")
            
            if status != current_status:
                if set_dept_validation(current_dept_id, status):
                    st.toast(f"Status updated to: {status}")
                    # We might want to update local var to stop re-triggering
                    current_status = status
                else:
                    st.error("Failed to save status.")

            if status == "Validate":
                st.success(f" The schedule for {selected_dept} has been **VALIDATED**.")
            elif status == "Reject":
                st.error(f" The schedule for {selected_dept} has been **REJECTED**.")
        except Exception as e:
            st.error(f"Could not load validation status: {e}")

with tab2:
    st.header("Department Statistics")
    
    c1, c2, c3 = st.columns(3)
    
    num_formations = dept_df["Formation"].nunique()
    num_modules = dept_df["Module"].nunique()
    num_exams = len(dept_df)
    
    c1.metric("Formations", num_formations)
    c2.metric("Modules", num_modules)
    c3.metric("Total Exams", num_exams)
    
    # Chart: Exams per Formation
    exams_per_form = dept_df["Formation"].value_counts().reset_index()
    exams_per_form.columns = ["Formation", "Exam Count"]
    
    st.bar_chart(exams_per_form.set_index("Formation"))

with tab3:
    st.header("Conflicts by Formation")
    
    # Simulate conflict detection logic for the selected department
    # For now, we simulate this based on the 'department_conflicts' mock data
    # but theoretically we would check overlap here.
    
    # 1. Simple Check: Do any exams in the SAME formation overlap?
    # (Mock logic: grouping by formation, date, time and counting > 1)
    
    conflicts_found = []
    
    for formation in dept_df["Formation"].unique():
        form_exams = dept_df[dept_df["Formation"] == formation]
        
        # 1. Check for duplicates in Date + Time (Direct Overlap)
        overlaps = form_exams[form_exams.duplicated(subset=["Date", "Time"], keep=False)]
        if not overlaps.empty:
            conflicts_found.append({
                "Formation": formation,
                "Type": "Time Overlap",
                "Details": f"{len(overlaps)} exams scheduled at the exact same time."
            })
            
        # 2. Check for duplicates in Date Only (More than 1 exam per day)
        day_counts = form_exams.groupby("Date").size()
        bad_days = day_counts[day_counts > 1]
        
        if not bad_days.empty:
            for day_val, count in bad_days.items():
                conflicts_found.append({
                    "Formation": formation,
                    "Type": "Overload (Same Day)",
                    "Details": f"{count} exams scheduled on {day_val}."
                })

    # Also pull from the global mock data
    mock_conflict = next((item for item in department_conflicts if item["department"] == selected_dept), None)
    
    if mock_conflict and mock_conflict["conflicts"] > 0:
        st.warning(f"Central system detects {mock_conflict['conflicts']} conflicts for this department.")
    else:
        st.success("No major conflicts reported by the central system.")

    if conflicts_found:
        st.error("Conflicts detected within formations:")
        st.table(pd.DataFrame(conflicts_found))
    else:
        st.info("No direct time overlaps detected in formations.")
