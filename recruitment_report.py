import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ======================
# INI PAGE STATE
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

# ======================
# HELPER
# ======================
def create_table_image(df):
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('off')

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        rowLabels=df.index if df.index.name else None,
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches='tight')
    buf.seek(0)
    return buf

def back_button():
    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# ======================
# LANDING PAGE
# ======================
if st.session_state.page == "home":

    st.markdown("<h1 style='text-align:center;'>Recruitment Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("###")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.image("report.png", width=120)
        if st.button("Recruitment Report"):
            st.session_state.page = "report"
            st.rerun()

    with c2:
        st.image("tracking.png", width=120)
        if st.button("Tracking Candidate"):
            st.session_state.page = "tracking"
            st.rerun()

    with c3:
        st.image("dashboard.png", width=120)
        st.button("⚙️ Coming Soon", disabled=True)

# =========================================================
# ====================== REPORT PAGE =======================
# =========================================================
elif st.session_state.page == "report":

    back_button()

    st.set_page_config(
    page_title="Recruitment Report",
    layout="wide"
)

# ======================
# HEADER
# ======================
col_logo, col_title = st.columns([1, 8], vertical_alignment="center")

with col_logo:
    st.image("logo_solid.png", width=70)

with col_title:
    st.markdown("<h1 style='margin:0;'>Recruitment Report</h1>", unsafe_allow_html=True)

# ======================
# REFRESH
# ======================
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# ======================
# LOAD DATA
# ======================
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
    return pd.read_csv(url)

@st.cache_data(ttl=60)
def load_mpp():
    url = "https://docs.google.com/spreadsheets/d/10A2o_8D_C5d0HWl1ve6WNn9V7AdSqSufLnWr3lKtR9I/export?format=csv&gid=0"
    return pd.read_csv(url)

df = load_data()
mpp = load_mpp()

# ======================
# CLEANING
# ======================
df.columns = df.columns.str.lower()
mpp.columns = mpp.columns.str.lower()

# normalize text penting 🔥
for col in ["level", "loc", "status"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

for col in ["level", "loc", "status"]:
    if col in mpp.columns:
        mpp[col] = mpp[col].astype(str).str.strip()

# ======================
# GLOBAL FILTER (1 SOURCE OF TRUTH)
# ======================
st.subheader("Global Filter")

f1, f2, f3 = st.columns(3)

# LEVEL
lvl_sel = "All"
if "level" in mpp.columns:
    lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()))

# LOCATION
loc_sel = "All"
if "loc" in mpp.columns:
    loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()))

# STATUS
st_sel = "All"
if "status" in mpp.columns:
    st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()))

# ======================
# APPLY FILTER KE MPP
# ======================
mpp_filtered = mpp.copy()

if lvl_sel != "All":
    mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]

if loc_sel != "All":
    mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]

if st_sel != "All":
    mpp_filtered = mpp_filtered[mpp_filtered["status"] == st_sel]

# =========================================================
# ================= RECRUITMENT SECTION ====================
# =========================================================

with st.expander("📊 Recruitment Database", expanded=True):

    filtered_df = df.copy()

    # SYNC REC DENGAN FILTER MPP
    if lvl_sel != "All":
        filtered_df = filtered_df[filtered_df["level"] == lvl_sel]

    if loc_sel != "All":
        filtered_df = filtered_df[filtered_df["loc"] == loc_sel]

    if st_sel != "All":
        filtered_df = filtered_df[filtered_df["status"] == st_sel]

    st.subheader("Summary")

    k1, k2 = st.columns(2)
    k1.metric("Total Candidate", len(df))
    k2.metric("Filtered Candidate", len(filtered_df))

    st.subheader("Candidate Status")

    s1, s2, s3 = st.columns(3)

    if "status1" in filtered_df.columns:
        status_series = filtered_df["status1"].str.upper()

        s1.metric("On-Progress", (status_series == "OPEN").sum())
        s2.metric("Failed", (status_series == "FAILED").sum())
        s3.metric("Hiring", (status_series == "CLOSE").sum())

    st.dataframe(filtered_df, use_container_width=True)

# =========================================================
# ====================== MPP SECTION ======================
# =========================================================

with st.expander("📈 MPP Dashboard", expanded=False):

    pivot_df = mpp_filtered[[
        "divisi",
        "2026(r)",
        "2026(a)",
        "talent_management",
        "gap_fullfill_rec"
    ]].copy()

    pivot_df = pivot_df.rename(columns={
        "2026(r)": "MPP",
        "2026(a)": "Existing",
        "talent_management": "ADP_2026",
        "gap_fullfill_rec": "GAP"
    })

    pivot = pivot_df.groupby("divisi").sum(numeric_only=True)

    st.dataframe(pivot, use_container_width=True)
    # DOWNLOAD IMAGE MPP
    img_mpp = create_table_image(pivot)

    st.download_button(
        label="Download MPP as Image",
        data=img_mpp,
        file_name="mpp_dashboard.png",
        mime="image/png"
)

# =========================================================
# ========== MPP vs RECRUITMENT PIPELINE ===================
# =========================================================

with st.expander("📊 MPP vs Recruitment Pipeline", expanded=False):

    st.subheader("Pipeline Analysis (By Departement)")

    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input("Start Date")
    end_date = col_d2.date_input("End Date")

    df_pipeline = df.copy()

    # SYNC FILTER
    if lvl_sel != "All":
        df_pipeline = df_pipeline[df_pipeline["level"] == lvl_sel]

    if loc_sel != "All":
        df_pipeline = df_pipeline[df_pipeline["loc"] == loc_sel]

    if st_sel != "All":
        df_pipeline = df_pipeline[df_pipeline["status"] == st_sel]

    # filter by dept (biar match MPP)
    valid_dept = mpp_filtered["departement"].unique()
    df_pipeline = df_pipeline[df_pipeline["departement"].isin(valid_dept)]

    # DATE
    date_cols = [
        "start_screening_cv",
        "start_interview_hr",
        "start_interview_user",
        "start_psychotest",
        "start_offering",
        "start_mcu",
        "start_review_mcu",
        "start_fu_mcu",
        "date_onboarding"
    ]

    for col in date_cols:
        if col in df_pipeline.columns:
            df_pipeline[col] = pd.to_datetime(df_pipeline[col], errors="coerce")

    def count_stage(col_name):
        temp = df_pipeline[
            (df_pipeline[col_name] >= pd.to_datetime(start_date)) &
            (df_pipeline[col_name] <= pd.to_datetime(end_date))
        ]
        return temp.groupby("departement")[col_name].count()

    pipeline = pd.DataFrame()
    pipeline["Screening CV"] = count_stage("start_screening_cv")
    pipeline["HR Interview"] = count_stage("start_interview_hr")
    pipeline["User Interview"] = count_stage("start_interview_user")
    pipeline["Psychotest"] = count_stage("start_psychotest")
    pipeline["Offering"] = count_stage("start_offering")
    pipeline["MCU"] = count_stage("start_mcu")
    pipeline["Review MCU"] = count_stage("start_review_mcu")
    pipeline["FU MCU"] = count_stage("start_fu_mcu")
    pipeline["Onboarding"] = count_stage("date_onboarding")

    pipeline = pipeline.fillna(0)

    mpp_summary = mpp_filtered.groupby(["divisi", "departement"])[[
        "2026(r)",
        "2026(a)",
        "talent_management",
        "gap_fullfill_rec"
    ]].sum(numeric_only=True)

    mpp_summary = mpp_summary.rename(columns={
        "2026(r)": "MPP",
        "2026(a)": "Existing",
        "talent_management": "ADP 2026",
        "gap_fullfill_rec": "GAP"
    })

    final_table = mpp_summary.merge(
        pipeline,
        left_on="departement",
        right_index=True,
        how="left"
    ).fillna(0)

    final_table = final_table.reset_index()

    st.dataframe(final_table, use_container_width=True)
    # DOWNLOAD IMAGE PIPELINE
    img_pipeline = create_table_image(final_table)
    
    st.download_button(
        label="Download Pipeline as Image",
        data=img_pipeline,
        file_name="mpp_vs_pipeline.png",
        mime="image/png"
    )

# =========================================================
# ==================== TRACKING PAGE =======================
# =========================================================
elif st.session_state.page == "tracking":

    back_button()

    st.set_page_config(
    page_title="Tracking Candidate",
    layout="wide"
)
col_logo, col_title = st.columns([1, 8], vertical_alignment="center")

with col_logo:
    st.image("logo_solid.png", width=70)

with col_title: 
    st.title("Candidate & Position Tracking")

# ======================
# LOAD DATA
# ======================
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
    return pd.read_csv(url)

df = load_data()

if df.empty:
    st.warning("No data available")
    st.stop()

df.columns = df.columns.str.lower()

# ======================
# CLEANING
# ======================
for col in ["candidate_id", "position_name", "departement", "level", "loc", "status1", "last_progress"]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# ======================
# SEARCH MODE
# ======================
mode = st.radio(
    "Search Mode",
    ["By Position", "By Candidate"],
    horizontal=True
)

# ======================
# COLOR FUNCTION
# ======================
def color_status(val):
    val = str(val).upper()
    if val == "OPEN":
        return "color: orange; font-weight: bold;"
    elif val == "FAILED":
        return "color: red; font-weight: bold;"
    elif val == "CLOSE":
        return "color: green; font-weight: bold;"
    else:
        return ""

# =========================================================
# ===================== BY POSITION ========================
# =========================================================
if mode == "By Position":

    pos_list = sorted(df["position_name"].dropna().unique())

    selected_pos = st.selectbox(
        "Select Position",
        pos_list
    )

    filtered = df[df["position_name"] == selected_pos]

    st.subheader(f"Candidates for: {selected_pos}")

    display_df = filtered[[
        "candidate_id",
        "position_name",
        "departement",
        "level",
        "loc",
        "status1",
        "last_progress"
    ]].copy()

    display_df = display_df.rename(columns={
        "status1": "Hiring Status"
    })

    st.dataframe(
        display_df.style.map(color_status, subset=["Hiring Status"]),
        use_container_width=True
    )

    st.metric("Total Candidate", len(display_df))


# =========================================================
# ===================== BY CANDIDATE =======================
# =========================================================
else:

    cand_list = sorted(df["candidate_id"].dropna().unique())

    selected_cand = st.selectbox(
        "Select Candidate",
        cand_list
    )

    filtered = df[df["candidate_id"] == selected_cand]

    if filtered.empty:
        st.warning("Candidate not found")
        st.stop()

    row = filtered.iloc[0]

    # ======================
    # HEADER INFO
    # ======================
    st.subheader(f"Candidate: {selected_cand}")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Position", row.get("position_name", "-"))
    c2.metric("Department", row.get("departement", "-"))
    c3.metric("Level", row.get("level", "-"))
    c4.metric("Location", row.get("loc", "-"))

    # ======================
    # HIRING STATUS
    # ======================
    hiring_status = str(row.get("status1", "Unknown")).upper()

    def color_box(status):
        if status == "OPEN":
            return "🟠 OPEN"
        elif status == "FAILED":
            return "🔴 FAILED"
        elif status == "CLOSE":
            return "🟢 CLOSE"
        else:
            return "⚪ UNKNOWN"

    st.markdown(f"### Hiring Status: {color_box(hiring_status)}")

    st.divider()

    # ======================
    # PIPELINE TRACKING
    # ======================
    st.subheader("Recruitment Progress")

    steps = [
        ("Screening CV", "start_screening_cv", "complete_screening_cv"),
        ("HR Interview", "start_interview_hr", "complete_interview_hr"),
        ("User Interview", "start_interview_user", "complete_interview_user"),
        ("Psychotest", "start_psychotest", "complete_psychotest"),
        ("Offering", "start_offering", "complete_offering"),
        ("MCU", "start_mcu", "mcu_date"),
        ("Review MCU", "start_review_mcu", "review_mcu"),
        ("FU MCU", "start_fu_mcu", "complete_fu_mcu"),
        ("Onboarding", "date_onboarding", "date_onboarding"),
    ]

    def get_status(start, end):
        if pd.notna(end):
            return "✅ Done"
        elif pd.notna(start):
            return "⏳ On Progress"
        else:
            return "⚪ Not Started"

    progress_data = []

    for step_name, start_col, end_col in steps:
        start_val = row.get(start_col)
        end_val = row.get(end_col)

        status = get_status(start_val, end_val)

        progress_data.append({
            "Stage": step_name,
            "Start": start_val,
            "End": end_val,
            "Status": status
        })

    progress_df = pd.DataFrame(progress_data)

    st.dataframe(progress_df, use_container_width=True)

    # ======================
    # PROGRESS BAR
    # ======================
    total_steps = len(progress_df)
    done_steps = (progress_df["Status"] == "✅ Done").sum()

    progress = done_steps / total_steps if total_steps > 0 else 0

    st.progress(progress)

    st.caption(f"{done_steps}/{total_steps} steps completed")
