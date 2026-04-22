import streamlit as st
import pandas as pd
import time
import base64

# ======================
# CONFIG (WAJIB PALING ATAS)
# ======================
st.set_page_config(
    page_title="Tracking Candidate",
    layout="wide"
)

st.write("APP STARTED")

# ======================
# SPLASH SCREEN SIMPLE
# ======================
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:

    placeholder = st.empty()

    with placeholder.container():
        st.markdown(
            """
            <style>
            .center {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                height: 80vh;
                color: white;
            }
            body {
                background-color: #0e1117;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://github.com/naviantar-ptdh/master_rec/blob/main/gambar1%20(1).png");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True)

        st.image("logo_solid.png", width=120)

        st.markdown(
            "<h2 style='color:white;'>Recruitment Dashboard</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='color:gray;'>Loading...</p>",
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    time.sleep(5)
    st.session_state.loaded = True
    placeholder.empty()

# ======================
# HEADER
# ======================
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
# BY POSITION
# ======================
if mode == "By Position":

    pos_list = sorted(df["position_name"].dropna().unique())

    selected_pos = st.selectbox("Select Position", pos_list)

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

    # ❗ FIX: tanpa style biar aman
    st.dataframe(display_df, use_container_width=True)

    st.metric("Total Candidate", len(display_df))

# ======================
# BY CANDIDATE
# ======================
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

    # STATUS
    status = str(row.get("status1", "Unknown")).upper()

    if status == "OPEN":
        st.success("🟠 OPEN")
    elif status == "FAILED":
        st.error("🔴 FAILED")
    elif status == "CLOSE":
        st.success("🟢 CLOSE")
    else:
        st.info("UNKNOWN")

    st.divider()

    # ======================
    # PIPELINE
    # ======================
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
            return "Done"
        elif pd.notna(start):
            return "On Progress"
        else:
            return "Not Started"

    progress_data = []

    for step_name, start_col, end_col in steps:
        progress_data.append({
            "Stage": step_name,
            "Start": row.get(start_col),
            "End": row.get(end_col),
            "Status": get_status(row.get(start_col), row.get(end_col))
        })

    progress_df = pd.DataFrame(progress_data)

    st.dataframe(progress_df, use_container_width=True)

    # PROGRESS BAR
    done = (progress_df["Status"] == "Done").sum()
    total = len(progress_df)

    st.progress(done / total if total > 0 else 0)
