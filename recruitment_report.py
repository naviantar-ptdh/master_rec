import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

# ==========================================
# 0. GLOBAL CONFIG
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = "home"

st.set_page_config(page_title="Recruitment System", layout="wide")

# CSS khusus agar tampilan rapi dan tombol seragam
st.markdown("""
    <style>
    .stButton button { border-radius: 10px; }
    .status-box { padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. APLIKASI: RECRUITMENT REPORT (100% SAME)
# ==========================================
def run_rec_report():
    if st.button("⬅ Back to Landing Page", key="back_rep"):
        st.session_state.page = "home"
        st.rerun()
    
    st.divider()
    
    def create_table_image(df):
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.axis('off')
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        buf = io.BytesIO()
        plt.savefig(buf, bbox_inches='tight')
        buf.seek(0)
        return buf

    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo:
        if os.path.exists("logo_solid.png"): st.image("logo_solid.png", width=70)
        else: st.markdown("### 🏢")
    with col_title:
        st.markdown("<h1 style='margin:0;'>Recruitment Report</h1>", unsafe_allow_html=True)

    if st.button("🔄 Refresh Data", key="ref_rep"): st.cache_data.clear()

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
    df.columns = df.columns.str.lower()
    mpp.columns = mpp.columns.str.lower()

    # FILTER SECTION
    st.subheader("Global Filter")
    f1, f2, f3 = st.columns(3)
    lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()), key="l1")
    loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()), key="l2")
    st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()), key="l3")

    mpp_filtered = mpp.copy()
    if lvl_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]
    if loc_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]
    if st_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["status"] == st_sel]

    # SUB 1: DATABASE
    with st.expander("📊 Recruitment Database", expanded=True):
        filtered_df = df.copy()
        if lvl_sel != "All": filtered_df = filtered_df[filtered_df["level"] == lvl_sel]
        if loc_sel != "All": filtered_df = filtered_df[filtered_df["loc"] == loc_sel]
        if st_sel != "All": filtered_df = filtered_df[filtered_df["status"] == st_sel]
        
        st.subheader("Summary")
        k1, k2 = st.columns(2)
        k1.metric("Total Candidate", len(df))
        k2.metric("Filtered Candidate", len(filtered_df))
        st.dataframe(filtered_df, use_container_width=True)
        st.subheader("Candidate Status")
        s1, s2, s3 = st.columns(3)
        if "status" in filtered_df.columns:
        status_series = filtered_df["status"].str.upper()
        s1.metric("On-Progress", (status_series == "OPEN").sum())
        s2.metric("Failed", (status_series == "FAILED").sum())
        s3.metric("Hiring", (status_series == "CLOSE").sum())
        st.dataframe(filtered_df, use_container_width=True)

    # SUB 2: MPP DASHBOARD
    with st.expander("📈 MPP Dashboard", expanded=False):
        pivot_df = mpp_filtered[["divisi","2026(r)","2026(a)","talent_management","gap_fullfill_rec"]].copy()
        pivot_df = pivot_df.rename(columns={"2026(r)": "MPP","2026(a)": "Existing","talent_management": "ADP_2026","gap_fullfill_rec": "GAP"})
        pivot = pivot_df.groupby("divisi").sum(numeric_only=True)
        st.dataframe(pivot, use_container_width=True)
        st.download_button("Download MPP Image", create_table_image(pivot), "mpp.png", "image/png", key="d1")

    # SUB 3: MPP VS PIPELINE (PENTING!)
    with st.expander("📊 MPP vs Recruitment Pipeline", expanded=False):
        st.subheader("Pipeline Analysis (By Departement)")
        col_d1, col_d2 = st.columns(2)
        start_date = col_d1.date_input("Start Date", key="sd_rep")
        end_date = col_d2.date_input("End Date", key="ed_rep")
        
        df_pipe = df.copy()
        valid_dept = mpp_filtered["departement"].unique()
        df_pipe = df_pipe[df_pipe["departement"].isin(valid_dept)]
        
        date_cols = ["start_screening_cv","start_interview_hr","start_interview_user","start_psychotest","start_offering","start_mcu","start_review_mcu","start_fu_mcu","date_onboarding"]
        for col in date_cols:
            if col in df_pipe.columns: df_pipe[col] = pd.to_datetime(df_pipe[col], errors="coerce")

        def count_stg(col):
            t = df_pipe[(df_pipe[col] >= pd.to_datetime(start_date)) & (df_pipe[col] <= pd.to_datetime(end_date))]
            return t.groupby("departement")[col].count()

        pipeline = pd.DataFrame()
        stages = ["Screening CV","HR Interview","User Interview","Psychotest","Offering","MCU","Review MCU","FU MCU","Onboarding"]
        cols = ["start_screening_cv","start_interview_hr","start_interview_user","start_psychotest","start_offering","start_mcu","start_review_mcu","start_fu_mcu","date_onboarding"]
        for s, c in zip(stages, cols): pipeline[s] = count_stg(c)
        
        mpp_sum = mpp_filtered.groupby(["divisi", "departement"])[["2026(r)","2026(a)","talent_management","gap_fullfill_rec"]].sum(numeric_only=True)
        final = mpp_sum.merge(pipeline.fillna(0), left_on="departement", right_index=True, how="left").fillna(0).reset_index()
        st.dataframe(final, use_container_width=True)
        st.download_button("Download Pipeline Image", create_table_image(final), "pipeline.png", "image/png", key="d2")

# ==========================================
# 2. APLIKASI: TRACKING CANDIDATE (100% SAME)
# ==========================================
def run_tracking():
    if st.button("⬅ Back to Landing Page", key="back_track"):
        st.session_state.page = "home"
        st.rerun()
    
    st.divider()
    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo:
        if os.path.exists("logo_solid.png"): st.image("logo_solid.png", width=70)
        else: st.markdown("### 🏢")
    with col_title: st.title("Candidate & Position Tracking")

    @st.cache_data(ttl=60)
    def load_data():
        url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
        return pd.read_csv(url)

    df = load_data()
    df.columns = df.columns.str.lower()
    for col in ["candidate_id", "position_name", "departement", "level", "loc", "status1"]:
        if col in df.columns: df[col] = df[col].fillna("Unknown")

    mode = st.radio("Search Mode", ["By Position", "By Candidate"], horizontal=True, key="m_track")

    # --- BY POSITION ---
    if mode == "By Position":
        pos_list = sorted(df["position_name"].dropna().unique())
        sel_pos = st.selectbox("Select Position", pos_list, key="s_pos")
        filtered = df[df["position_name"] == sel_pos]
        
        st.info("💡 **Legend Status:** 🟠 OPEN | 🟢 CLOSE | 🔴 FAILED") # Penjelasan warna
        
        def color_st(val):
            v = str(val).upper()
            if v == "OPEN": return "color: orange; font-weight: bold;"
            if v == "FAILED": return "color: red; font-weight: bold;"
            if v == "CLOSE": return "color: green; font-weight: bold;"
            return ""

        disp = filtered[["candidate_id","position_name","departement","level","loc","status1","last_progress"]].copy()
        disp = disp.rename(columns={"status1": "Hiring Status"})
        st.dataframe(disp.style.map(color_st, subset=["Hiring Status"]), use_container_width=True)
        st.metric("Total Candidate", len(disp))

    # --- BY CANDIDATE ---
    else:
        cand_list = sorted(df["candidate_id"].dropna().unique())
        sel_cand = st.selectbox("Select Candidate", cand_list, key="s_cand")
        filt = df[df["candidate_id"] == sel_cand]
        if filt.empty: st.stop()
        row = filt.iloc[0]

        st.subheader(f"Candidate: {sel_cand}")
        
        # 4 KOLOM METRIK (Sesuai Foto)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Position", row.get("position_name", "-"))
        m2.metric("Department", row.get("departement", "-"))
        m3.metric("Level", row.get("level", "-"))
        m4.metric("Location", row.get("loc", "-"))

        # BOX STATUS WARNA (Sesuai Foto)
        h_st = str(row.get("status1", "Unknown")).upper()
        st_map = {"OPEN": "🟠 OPEN", "FAILED": "🔴 FAILED", "CLOSE": "🟢 CLOSE"}
        st.markdown(f"### Hiring Status: {st_map.get(h_st, '⚪ Unknown')}")
        
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
        
        p_data = []
        for name, s_col, e_col in steps:
            st_txt = "✅ Done" if pd.notna(row.get(e_col)) else "⏳ On Progress" if pd.notna(row.get(s_col)) else "⚪ Not Started"
            p_data.append({"Stage": name, "Start": row.get(s_col), "End": row.get(e_col), "Status": st_txt})
        
        st.dataframe(pd.DataFrame(p_data), use_container_width=True)
        done = (pd.DataFrame(p_data)["Status"] == "✅ Done").sum()
        st.progress(done / len(steps))
        st.caption(f"{done}/{len(steps)} steps completed")

# ==========================================
# 3. ROUTING & LANDING PAGE
# ==========================================
if st.session_state.page == "home":
    # Membuat 3 kolom: [kiri, tengah, kanan]
    # Kolom tengah (rasio 3) akan menampung logo dan judul
    _, center_col, _ = st.columns([1, 3, 1])

    with center_col:
        # Di dalam kolom tengah, bagi lagi menjadi 2 kolom untuk Logo & Teks
        # vertical_alignment="center" membuat teks sejajar tengah dengan logo
        col_logo, col_title = st.columns([1, 2], vertical_alignment="center")
        
        with col_logo:
            if os.path.exists("logo_solid.png"):
                st.image("logo_solid.png", width=120)
            else:
                st.markdown("### LOGO")
        
        with col_title:
            st.markdown("""
                <h1 style='margin: 0; white-space: nowrap;'>
                    HR System Portal
                </h1>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ... sisa kode menu (c1, c2, c3) tetap sama ...
    c1, c2, c3 = st.columns(3)
    with c1:
        if os.path.exists("report.png"): st.image("report.png", width=120)
        if st.button("📊 Recruitment Report", use_container_width=True):
            st.session_state.page = "report"; st.rerun()
    with c2:
        if os.path.exists("tracking.png"): st.image("tracking.png", width=120)
        if st.button("🔍 Tracking Candidate", use_container_width=True):
            st.session_state.page = "tracking"; st.rerun()
    with c3:
        if os.path.exists("dashboard.png"): st.image("dashboard.png", width=120)
        st.button("⚙️ Coming Soon", disabled=True, use_container_width=True)

elif st.session_state.page == "report": run_rec_report()
elif st.session_state.page == "tracking": run_tracking()
