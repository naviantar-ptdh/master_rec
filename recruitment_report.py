import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ==========================================
# 0. GLOBAL CONFIG (Hanya 1x di paling atas)
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = "home"

st.set_page_config(
    page_title="HR Recruitment Portal",
    layout="wide"
)

# Custom CSS untuk Landing Page agar mirip dengan referensi gambar
st.markdown("""
    <style>
    .card-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #FFF5E6;
        border-radius: 20px;
        padding: 20px;
        transition: 0.3s;
        cursor: pointer;
        border: 1px solid #FFE0B2;
    }
    .stButton button {
        border-radius: 15px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. APLIKASI PERTAMA: RECRUITMENT REPORT
# ==========================================
def run_rec_report():
    # TOMBOL BACK
    if st.button("⬅ Back to Landing Page"):
        st.session_state.page = "home"
        st.rerun()
    
    st.divider()

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

    # HEADER
    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo:
        st.image("logo_solid.png", width=70)
    with col_title:
        st.markdown("<h1 style='margin:0;'>Recruitment Report</h1>", unsafe_allow_html=True)

    # REFRESH
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()

    # LOAD DATA
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

    # CLEANING
    df.columns = df.columns.str.lower()
    mpp.columns = mpp.columns.str.lower()
    for col in ["level", "loc", "status"]:
        if col in df.columns: df[col] = df[col].astype(str).str.strip()
        if col in mpp.columns: mpp[col] = mpp[col].astype(str).str.strip()

    # GLOBAL FILTER
    st.subheader("Global Filter")
    f1, f2, f3 = st.columns(3)
    lvl_sel = "All"
    if "level" in mpp.columns:
        lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()), key="report_lvl")
    loc_sel = "All"
    if "loc" in mpp.columns:
        loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()), key="report_loc")
    st_sel = "All"
    if "status" in mpp.columns:
        st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()), key="report_st")

    mpp_filtered = mpp.copy()
    if lvl_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]
    if loc_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]
    if st_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["status"] == st_sel]

    # RECRUITMENT SECTION
    with st.expander("📊 Recruitment Database", expanded=True):
        filtered_df = df.copy()
        if lvl_sel != "All": filtered_df = filtered_df[filtered_df["level"] == lvl_sel]
        if loc_sel != "All": filtered_df = filtered_df[filtered_df["loc"] == loc_sel]
        if st_sel != "All": filtered_df = filtered_df[filtered_df["status"] == st_sel]
        
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

    # MPP SECTION
    with st.expander("📈 MPP Dashboard", expanded=False):
        pivot_df = mpp_filtered[["divisi","2026(r)","2026(a)","talent_management","gap_fullfill_rec"]].copy()
        pivot_df = pivot_df.rename(columns={"2026(r)": "MPP","2026(a)": "Existing","talent_management": "ADP_2026","gap_fullfill_rec": "GAP"})
        pivot = pivot_df.groupby("divisi").sum(numeric_only=True)
        st.dataframe(pivot, use_container_width=True)
        img_mpp = create_table_image(pivot)
        st.download_button(label="Download MPP as Image", data=img_mpp, file_name="mpp_dashboard.png", mime="image/png")

    # PIPELINE SECTION
    with st.expander("📊 MPP vs Recruitment Pipeline", expanded=False):
        st.subheader("Pipeline Analysis (By Departement)")
        col_d1, col_d2 = st.columns(2)
        start_date = col_d1.date_input("Start Date", key="sd1")
        end_date = col_d2.date_input("End Date", key="ed1")
        df_pipeline = df.copy()
        if lvl_sel != "All": df_pipeline = df_pipeline[df_pipeline["level"] == lvl_sel]
        if loc_sel != "All": df_pipeline = df_pipeline[df_pipeline["loc"] == loc_sel]
        if st_sel != "All": df_pipeline = df_pipeline[df_pipeline["status"] == st_sel]
        
        valid_dept = mpp_filtered["departement"].unique()
        df_pipeline = df_pipeline[df_pipeline["departement"].isin(valid_dept)]
        
        date_cols = ["start_screening_cv","start_interview_hr","start_interview_user","start_psychotest","start_offering","start_mcu","start_review_mcu","start_fu_mcu","date_onboarding"]
        for col in date_cols:
            if col in df_pipeline.columns: df_pipeline[col] = pd.to_datetime(df_pipeline[col], errors="coerce")

        def count_stage(col_name):
            temp = df_pipeline[(df_pipeline[col_name] >= pd.to_datetime(start_date)) & (df_pipeline[col_name] <= pd.to_datetime(end_date))]
            return temp.groupby("departement")[col_name].count()

        pipeline = pd.DataFrame()
        stages = ["Screening CV","HR Interview","User Interview","Psychotest","Offering","MCU","Review MCU","FU MCU","Onboarding"]
        cols = ["start_screening_cv","start_interview_hr","start_interview_user","start_psychotest","start_offering","start_mcu","start_review_mcu","start_fu_mcu","date_onboarding"]
        for s, c in zip(stages, cols): pipeline[s] = count_stage(c)
        pipeline = pipeline.fillna(0)

        mpp_summary = mpp_filtered.groupby(["divisi", "departement"])[["2026(r)","2026(a)","talent_management","gap_fullfill_rec"]].sum(numeric_only=True)
        mpp_summary = mpp_summary.rename(columns={"2026(r)": "MPP","2026(a)": "Existing","talent_management": "ADP 2026","gap_fullfill_rec": "GAP"})
        final_table = mpp_summary.merge(pipeline, left_on="departement", right_index=True, how="left").fillna(0).reset_index()
        st.dataframe(final_table, use_container_width=True)
        img_pipeline = create_table_image(final_table)
        st.download_button(label="Download Pipeline as Image", data=img_pipeline, file_name="mpp_vs_pipeline.png", mime="image/png")

# ==========================================
# 2. APLIKASI KEDUA: TRACKING CANDIDATE
# ==========================================
def run_tracking():
    # TOMBOL BACK
    if st.button("⬅ Back to Landing Page"):
        st.session_state.page = "home"
        st.rerun()
    
    st.divider()

    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo: st.image("logo_solid.png", width=70)
    with col_title: st.title("Candidate & Position Tracking")

    @st.cache_data(ttl=60)
    def load_data():
        url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
        return pd.read_csv(url)

    df = load_data()
    if df.empty:
        st.warning("No data available")
        st.stop()
    df.columns = df.columns.str.lower()

    for col in ["candidate_id", "position_name", "departement", "level", "loc", "status1", "last_progress"]:
        if col in df.columns: df[col] = df[col].fillna("Unknown")

    mode = st.radio("Search Mode", ["By Position", "By Candidate"], horizontal=True)

    def color_status(val):
        val = str(val).upper()
        if val == "OPEN": return "color: orange; font-weight: bold;"
        elif val == "FAILED": return "color: red; font-weight: bold;"
        elif val == "CLOSE": return "color: green; font-weight: bold;"
        return ""

    if mode == "By Position":
        pos_list = sorted(df["position_name"].dropna().unique())
        selected_pos = st.selectbox("Select Position", pos_list)
        filtered = df[df["position_name"] == selected_pos]
        st.subheader(f"Candidates for: {selected_pos}")
        display_df = filtered[["candidate_id","position_name","departement","level","loc","status1","last_progress"]].copy()
        display_df = display_df.rename(columns={"status1": "Hiring Status"})
        st.dataframe(display_df.style.map(color_status, subset=["Hiring Status"]), use_container_width=True)
        st.metric("Total Candidate", len(display_df))

    else:
        cand_list = sorted(df["candidate_id"].dropna().unique())
        selected_cand = st.selectbox("Select Candidate", cand_list)
        filtered = df[df["candidate_id"] == selected_cand]
        if filtered.empty:
            st.warning("Candidate not found")
            st.stop()
        row = filtered.iloc[0]
        st.subheader(f"Candidate: {selected_cand}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Position", row.get("position_name", "-"))
        c2.metric("Department", row.get("departement", "-"))
        c3.metric("Level", row.get("level", "-"))
        c4.metric("Location", row.get("loc", "-"))
        
        hiring_status = str(row.get("status1", "Unknown")).upper()
        status_icon = {"OPEN": "🟠 OPEN", "FAILED": "🔴 FAILED", "CLOSE": "🟢 CLOSE"}.get(hiring_status, "⚪ UNKNOWN")
        st.markdown(f"### Hiring Status: {status_icon}")
        st.divider()
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
        progress_data = []
        for step_name, start_col, end_col in steps:
            s_val, e_val = row.get(start_col), row.get(end_col)
            status = "✅ Done" if pd.notna(e_val) else "⏳ On Progress" if pd.notna(s_val) else "⚪ Not Started"
            progress_data.append({"Stage": step_name, "Start": s_val, "End": e_val, "Status": status})
        
        progress_df = pd.DataFrame(progress_data)
        st.dataframe(progress_df, use_container_width=True)
        done_steps = (progress_df["Status"] == "✅ Done").sum()
        st.progress(done_steps / len(steps))
        st.caption(f"{done_steps}/{len(steps)} steps completed")

# ==========================================
# 3. ROUTING & LANDING PAGE
# ==========================================
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;'>Recruitment Portal</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image("report.png", width=120) if io.os.path.exists("report.png") else st.title("📊")
        if st.button("Recruitment Report", use_container_width=True):
            st.session_state.page = "report"
            st.rerun()

    with col2:
        st.image("tracking.png", width=120) if io.os.path.exists("tracking.png") else st.title("🔍")
        if st.button("Tracking Candidate", use_container_width=True):
            st.session_state.page = "tracking"
            st.rerun()

    with col3:
        st.image("dashboard.png", width=120) if io.os.path.exists("dashboard.png") else st.title("⚙️")
        st.button("Coming Soon", disabled=True, use_container_width=True)

elif st.session_state.page == "report":
    run_rec_report()

elif st.session_state.page == "tracking":
    run_tracking()
