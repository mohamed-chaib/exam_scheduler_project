import streamlit as st
import pandas as pd
from mock_data import (
    exam_schedule,
    rooms_usage,
    department_conflicts,
    professor_workload,
    departments,
    modules,
    formations,
    rooms,
    professors,
    require_auth,
    get_validation_summary,
    get_global_validation,
    set_global_validation
)

st.set_page_config(layout="wide")
require_auth(["dean", "admin"])

st.title("👨‍💼 Vice-Dean / Dean – Strategic Dashboard")

# ---------------- PREPARE DATA ----------------
print(rooms_usage)
df_rooms_usage = pd.DataFrame(rooms_usage)
df_conflicts = pd.DataFrame(department_conflicts)
df_workload = pd.DataFrame(professor_workload)

# Build the enriched EDT for display
df_exams = pd.DataFrame(exam_schedule)
df_modules = pd.DataFrame(modules)
df_formations = pd.DataFrame(formations)
df_depts = pd.DataFrame(departments)
df_rooms = pd.DataFrame(rooms)
df_profs = pd.DataFrame(professors)

# Joins
master_df = pd.merge(df_exams, df_modules, left_on="module_id", right_on="id")
master_df = pd.merge(master_df, df_formations, left_on="formation_id", right_on="id", suffixes=("", "_form"))
master_df = pd.merge(master_df, df_depts, left_on="dept_id", right_on="id", suffixes=("", "_dept"))
master_df = pd.merge(master_df, df_rooms, left_on="salle_id", right_on="id", suffixes=("", "_salle"))
master_df = pd.merge(master_df, df_profs, left_on="prof_id", right_on="id", suffixes=("", "_prof"))

master_df = master_df.rename(columns={
    "nom_dept": "Department",
    "date_heure": "Date",
    "nom": "Module",
    "nom_salle": "Room"
})
master_df["Date"] = pd.to_datetime(master_df["Date"]).dt.date


# ---------------- KPIs ----------------
st.subheader("📌 Global Strategic KPIs")

c1, c2, c3, c4 = st.columns(4)

total_conflicts = df_conflicts["conflicts"].sum()
avg_room_usage = int(df_rooms_usage["usage_rate"].mean())
total_hours = df_workload["hours"].sum()

c1.metric("Total Departments", len(departments))
c2.metric("Pending Conflicts", total_conflicts)
c3.metric("Avg Room Usage (%)", f"{avg_room_usage}%")
c4.metric("Total Professor Hours", total_hours)

# ---------------- GLOBAL EXAM TIMETABLE ----------------
st.subheader("📅 Global Exam Timetable (Read-Only)")

col1, col2 = st.columns(2)

with col1:
    dept_options = ["All"] + sorted(master_df["Department"].unique().tolist())
    selected_department = st.selectbox("Filter by Department", dept_options)

with col2:
    date_options = ["All"] + sorted(master_df["Date"].unique().tolist())
    selected_date = st.selectbox("Filter by Date", date_options)

filtered_edt = master_df.copy()

if selected_department != "All":
    filtered_edt = filtered_edt[filtered_edt["Department"] == selected_department]

if selected_date != "All":
    filtered_edt = filtered_edt[filtered_edt["Date"] == selected_date]

st.dataframe(
    filtered_edt[["Department", "Module", "Date", "Room"]], 
    use_container_width=True
)

# ---------------- ROOM OCCUPATION ----------------
st.subheader("🏫 Global Room & Playing Fields")

c_chart, c_data = st.columns([2, 1])
with c_chart:
    st.caption("Room Usage Rate (%)")
    st.bar_chart(df_rooms_usage.set_index("room")["usage_rate"])

with c_data:
    st.caption("Detailed Usage")
    st.dataframe(df_rooms_usage[["room", "usage_rate", "capacity_check"]], use_container_width=True)

# ---------------- CONFLICTS BY DEPARTMENT ----------------
st.subheader("⚠️ Conflict Analysis")

if total_conflicts > 0:
    st.bar_chart(df_conflicts.set_index("department")["conflicts"])
else:
    st.success("No conflicts reported across any department.")

# ---------------- FINAL VALIDATION ----------------
# ---------------- FINAL VALIDATION ----------------
st.subheader("✅ Final Exam Timetable Validation")

# 1. Departmental Validation Status
st.markdown("### Departmental Approvals")
dept_status_list = get_validation_summary()
df_status = pd.DataFrame(dept_status_list)

if not df_status.empty:
    # Use metrics or dataframe
    cols = st.columns(len(df_status) if len(df_status) < 5 else 3)
    # Simple table for now
    st.dataframe(df_status, use_container_width=True)
    
    validated_counts = df_status[df_status["status"] == "Validate"].shape[0]
    total_depts = df_status.shape[0]
    st.progress(validated_counts / total_depts if total_depts > 0 else 0)
    st.caption(f"{validated_counts}/{total_depts} Departments Validated")
else:
    st.warning("No department status available.")

st.markdown("---")

# 2. Global Sign-off
st.markdown("### Dean Final Sign-off")
global_status = get_global_validation()

val_cols = st.columns([1, 1])

with val_cols[0]:
    st.info(f"Current Global Status: **{global_status}**")

with val_cols[1]:
    options = ["Pending", "Finalized"]
    index = 0 
    if global_status in options:
        index = options.index(global_status)
        
    final_decision = st.radio("Final Decision", options, index=index, horizontal=True)
    
    if st.button("Update Global Status"):
        if set_global_validation(final_decision):
            st.success("Global status updated.")
            st.rerun()
        else:
            st.error("Failed to update status.")

if final_decision == "Finalized":
    st.success("✅ The exam timetable has been OFFICIALY FINALIZED and PUBLISHED.")
else:
    st.warning("⏳ The exam timetable is still PENDING final approval.")
