import streamlit as st
import pandas as pd
from mock_data import (
    exam_schedule,
    professors,
    modules,
    rooms,
    formations,
    departments,
    get_validation_summary,
    get_global_validation
)

st.set_page_config(layout="wide")

st.title("👨‍🏫 Professor View")

# ---------------- VISIBILITY CHECK ----------------
global_status = get_global_validation()

if global_status != "Finalized":
    st.info("ℹ️ The final exam schedule has not been officially published yet. Please check back later.")
    st.stop()
    
# Get valid departments
dept_summary = get_validation_summary()
valid_depts = [d["department"] for d in dept_summary if d["status"] == "Validate"]

# ---------------- PREPARE DATA ----------------
df_exams = pd.DataFrame(exam_schedule)
df_profs = pd.DataFrame(professors)
df_modules = pd.DataFrame(modules)
df_rooms = pd.DataFrame(rooms)
df_formations = pd.DataFrame(formations)

# ---------------- PROFESSOR SELECTION ----------------
st.subheader("🎯 Select Professor")

# Map Name -> ID
prof_map = {p["nom"]: p["id"] for p in professors}
selected_prof_name = st.selectbox("Choose a professor", list(prof_map.keys()))
selected_prof_id = prof_map[selected_prof_name]

# ---------------- FILTER EXAMS ----------------
profs_exams = df_exams[df_exams["prof_id"] == selected_prof_id]

if profs_exams.empty:
    st.warning("No exams assigned to this professor.")
else:
    # Enrich Data
    # Join with Modules
    enriched = pd.merge(profs_exams, df_modules, left_on="module_id", right_on="id", suffixes=("", "_mod"))
    # Join with Rooms
    enriched = pd.merge(enriched, df_rooms, left_on="salle_id", right_on="id", suffixes=("", "_salle"))
    # Join with Formations (via Module)
    # Join with Formations (via Module)
    enriched = pd.merge(enriched, df_formations, left_on="formation_id", right_on="id", suffixes=("", "_form"))
    
    # Join with Formations -> Join with Departments
    df_depts = pd.DataFrame(departments)
    enriched = pd.merge(enriched, df_depts, left_on="dept_id", right_on="id", suffixes=("", "_dept"))

    # FILTER: Only show exams from VALIDATED departments
    # 'nom_dept' comes from the merge above
    enriched = enriched[enriched["nom_dept"].isin(valid_depts)]
    
    if enriched.empty:
        st.warning("No exams scheduled for you in currently validated departments.")
        st.stop()

    # Rename for Display
    # تحويل التاريخ والوقت
    enriched["date"] = pd.to_datetime(enriched["date_heure"]).dt.date
    enriched["time"] = pd.to_datetime(enriched["date_heure"]).dt.time
    enriched["duration"] = enriched["duree_minutes"]
    display_df = enriched[[
        "nom",          # Module Name
        "nom_form",     # Formation Name
        "nom_salle",
        "date" ,
        "time"  ,
        "duration"  # Room Name
    ]]
    
    display_df.columns = ["Module", "Formation", "Date", "Time", "Room", "Duration (min)"]
    
    st.subheader(f"📅 Exams supervised by {selected_prof_name}")
    st.dataframe(display_df.sort_values(by=["Date", "Time"]), use_container_width=True)

    # ---------------- METRICS ----------------
    st.subheader("📊 Workload Overview")
    
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Total Exams", len(display_df))
    c2.metric("Exam Days", display_df["Date"].nunique())
    c3.metric("Unique Rooms", display_df["Room"].nunique())
