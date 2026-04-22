import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Recruitment App", layout="wide")

# ======================
# SESSION NAVIGATION
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

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

df.columns = df.columns.str.lower()
mpp.columns = mpp.columns.str.lower()

# ======================
# LANDING PAGE
# ======================
if st.session_state.page == "home":

    st.markdown("<h1 style='text-align:center;'>Recruitment Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("###")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
        if st.button("📊 Recruitment Report"):
            st.session_state.page = "report"
            st.rerun()

    with c2:
        st.image("https://cdn-icons-png.flaticon.com/512/747/747376.png", width=120)
        if st.button("🔍 Tracking Candidate"):
            st.session_state.page = "tracking"
            st.rerun()

    with c3:
        st.image("https://cdn-icons-png.flaticon.com/512/1828/1828817.png", width=120)
        st.button("⚙️ Coming Soon", disabled=True)

# ======================
# BACK BUTTON
# ======================
def back_button():
    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# =========================================================
# ====================== REPORT PAGE =======================
# =========================================================
if st.session_state.page == "report":

    back_button()

    st.title("📊 Recruitment Report")

    # ======================
    # FILTER
    # ======================
    f1, f2, f3 = st.columns(3)

    lvl = f1.selectbox("Level", ["All"] + sorted(df["level"].dropna().unique()))
    loc = f2.selectbox("Location", ["All"] + sorted(df["loc"].dropna().unique()))
    stt = f3.selectbox("Status", ["All"] + sorted(df["status"].dropna().unique()))

    df_filtered = df.copy()

    if lvl != "All":
        df_filtered = df_filtered[df_filtered["level"] == lvl]
    if loc != "All":
        df_filtered = df_filtered[df_filtered["loc"] == loc]
    if stt != "All":
        df_filtered = df_filtered[df_filtered["status"] == stt]

    # ======================
    # MPP TABLE
    # ======================
    st.subheader("MPP Dashboard")

    pivot = mpp.groupby("divisi")[[
        "2026(r)", "2026(a)", "talent_management", "gap_fullfill_rec"
    ]].sum()

    pivot = pivot.rename(columns={
        "2026(r)": "MPP",
        "2026(a)": "Existing",
        "talent_management": "ADP_2026",
        "gap_fullfill_rec": "GAP"
    })

    # TOTAL ROW 🔥
    total_row = pivot.sum()
    total_row.name = "TOTAL"
    pivot = pd.concat([pivot, total_row.to_frame().T])

    st.dataframe(pivot, use_container_width=True)

    # ======================
    # PIPELINE
    # ======================
    st.subheader("Pipeline Analysis")

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
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    pipeline = pd.DataFrame()

    def count(col):
        return df.groupby("departement")[col].count()

    pipeline["Screening CV"] = count("start_screening_cv")
    pipeline["HR Interview"] = count("start_interview_hr")
    pipeline["User Interview"] = count("start_interview_user")
    pipeline["Onboarding"] = count("date_onboarding")

    pipeline = pipeline.fillna(0)

    # TOTAL ROW 🔥
    total_pipeline = pipeline.sum()
    total_pipeline.name = "TOTAL"
    pipeline = pd.concat([pipeline, total_pipeline.to_frame().T])

    st.dataframe(pipeline, use_container_width=True)

# =========================================================
# ===================== TRACKING PAGE ======================
# =========================================================
if st.session_state.page == "tracking":

    back_button()

    st.title("🔍 Candidate Tracking")

    mode = st.radio("Mode", ["By Position", "By Candidate"], horizontal=True)

    # ======================
    # BY POSITION
    # ======================
    if mode == "By Position":

        pos = st.selectbox("Select Position", sorted(df["position_name"].dropna().unique()))
        data = df[df["position_name"] == pos]

        show = data[[
            "candidate_id",
            "departement",
            "level",
            "loc",
            "status1",
            "last_progress"
        ]].rename(columns={"status1": "Hiring Status"})

        st.dataframe(show, use_container_width=True)
        st.metric("Total Candidate", len(show))

    # ======================
    # BY CANDIDATE
    # ======================
    else:

        cand = st.selectbox("Select Candidate", sorted(df["candidate_id"].dropna().unique()))
        row = df[df["candidate_id"] == cand].iloc[0]

        st.subheader(f"Candidate: {cand}")

        st.write({
            "Position": row.get("position_name"),
            "Dept": row.get("departement"),
            "Level": row.get("level"),
            "Location": row.get("loc"),
            "Status": row.get("status1")
        })

        steps = [
            ("Screening", "start_screening_cv", "complete_screening_cv"),
            ("HR", "start_interview_hr", "complete_interview_hr"),
            ("User", "start_interview_user", "complete_interview_user"),
            ("Onboarding", "date_onboarding", "date_onboarding"),
        ]

        prog = []
        for name, s, e in steps:
            prog.append({
                "Stage": name,
                "Start": row.get(s),
                "End": row.get(e)
            })

        st.dataframe(pd.DataFrame(prog), use_container_width=True)
