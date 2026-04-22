import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ======================
# INIT PAGE STATE
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

    st.set_page_config(page_title="Recruitment Report", layout="wide")

    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo:
        st.image("logo_solid.png", width=70)
    with col_title:
        st.markdown("<h1 style='margin:0;'>Recruitment Report</h1>", unsafe_allow_html=True)

    # LOAD
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

    # ======================
    # GLOBAL FILTER
    # ======================
    st.subheader("Global Filter")

    f1, f2, f3 = st.columns(3)

    lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()))
    loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()))
    st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()))

    mpp_filtered = mpp.copy()

    if lvl_sel != "All":
        mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]
    if loc_sel != "All":
        mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]
    if st_sel != "All":
        mpp_filtered = mpp_filtered[mpp_filtered["status"] == st_sel]

    # ======================
    # MPP DASHBOARD
    # ======================
    with st.expander("📈 MPP Dashboard", expanded=True):

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

        # 🔥 TOTAL ROW (INI YANG LO MINTA)
        total_row = pivot.sum().to_frame().T
        total_row.index = ["TOTAL"]

        st.markdown("### Total")
        st.dataframe(total_row, use_container_width=True)

        img_mpp = create_table_image(pivot)

        st.download_button(
            label="Download MPP as Image",
            data=img_mpp,
            file_name="mpp_dashboard.png",
            mime="image/png"
        )

    # ======================
    # PIPELINE
    # ======================
    with st.expander("📊 MPP vs Recruitment Pipeline", expanded=False):

        col_d1, col_d2 = st.columns(2)
        start_date = col_d1.date_input("Start Date")
        end_date = col_d2.date_input("End Date")

        df_pipeline = df.copy()

        date_cols = [
            "start_screening_cv","start_interview_hr","start_interview_user",
            "start_psychotest","start_offering","start_mcu",
            "start_review_mcu","start_fu_mcu","date_onboarding"
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

        mpp_summary = mpp_filtered.groupby(["divisi","departement"])[[
            "2026(r)","2026(a)","talent_management","gap_fullfill_rec"
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

        # 🔥 TOTAL ROW PIPELINE
        total_pipeline = final_table.select_dtypes("number").sum().to_frame().T
        total_pipeline.insert(0, "departement", "TOTAL")

        st.markdown("### Total")
        st.dataframe(total_pipeline, use_container_width=True)

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

    st.set_page_config(page_title="Tracking Candidate", layout="wide")

    st.title("Candidate & Position Tracking")

    @st.cache_data(ttl=60)
    def load_data():
        url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
        return pd.read_csv(url)

    df = load_data()
    df.columns = df.columns.str.lower()

    for col in ["candidate_id","position_name","departement","level","loc","status1","last_progress"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    mode = st.radio("Search Mode", ["By Position","By Candidate"], horizontal=True)

    if mode == "By Position":

        pos = st.selectbox("Select Position", sorted(df["position_name"].unique()))
        filtered = df[df["position_name"] == pos]

        st.dataframe(filtered)

    else:

        cand = st.selectbox("Select Candidate", sorted(df["candidate_id"].unique()))
        row = df[df["candidate_id"] == cand].iloc[0]

        st.write(row)
