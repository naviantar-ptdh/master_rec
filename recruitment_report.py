import streamlit as st
import pandas as pd
import time
import base64

# ======================
# LOAD IMAGE BASE64
# ======================
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = get_base64("gambar1.JPG")

# ======================
# SPLASH SCREEN
# ======================
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:

    splash = st.empty()

    with splash.container():
        st.markdown(
            f"""
            <style>
            .splash {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url("data:image/jpg;base64,{bg_img}");
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: white;
                z-index: 9999;
            }}

            .logo {{
                width: 120px;
            }}

            .title {{
                margin-top: 20px;
                font-size: 28px;
                font-weight: bold;
            }}

            .loading {{
                margin-top: 10px;
                font-size: 18px;
                opacity: 0.8;
                animation: blink 1.5s infinite;
            }}

            @keyframes blink {{
                0% {{ opacity: 0.2; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.2; }}
            }}
            </style>

            <div class="splash">
                <img src="logo_solid.png" class="logo">
                <div class="title">Recruitment Dashboard</div>
                <div class="loading">Loading...</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    time.sleep(2.5)

    st.session_state.loaded = True
    splash.empty()

# ======================
# CONFIG
# ======================
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
