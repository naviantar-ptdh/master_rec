import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# ======================
# TITLE
# ======================
st.title("Recruitment Dashboard")

# ======================
# CONNECT TO BIGQUERY
# ======================
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

client = bigquery.Client(
    credentials=credentials,
    project="recruitment-ptdh"
)

# ======================
# QUERY FUNCTION
# ======================
@st.cache_data
def load_data():
    query = """
    SELECT *
    FROM `recruitment-ptdh.recruitment_ptdh.master_rec_native`
    WHERE candidate_id IS NOT NULL
    """
    return client.query(query).to_dataframe()

df = load_data()

# ======================
# HANDLE DATA KOSONG (ANTI ERROR)
# ======================
if df.empty:
    st.warning("No data available")
    st.stop()

# ======================
# CLEANING DATE
# ======================
date_cols = [
    'start_prf_routing', 'complete_prf_routing', 'start_screening_cv',
    'complete_screening_cv','start_interview_hr','complete_interview_hr',
    'start_interview_user','complete_interview_user','start_psychotest',
    'complete_psychotest','start_offering','ol_sent_to_candidate',
    'complete_offering','start_mcu','mcu_date','mcu_issue_date',
    'start_review_mcu','sent_mcu_to_doctor','review_mcu',
    'start_fu_mcu','complete_fu_mcu','date_fit','date_onboarding'
]

for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# ======================
# DISPLAY DATA
# ======================
st.subheader("Raw Data")
st.dataframe(df)

# ======================
# FILTER (ANTI ERROR)
# ======================
st.subheader("Filter Data")

if 'level' in df.columns:
    level = st.selectbox(
        "Select Level",
        sorted(df['level'].dropna().unique())
    )

    filtered_df = df[df['level'] == level]

    st.dataframe(filtered_df)
else:
    st.warning("Column 'level' not found")
    filtered_df = df

# ======================
# KPI SIMPLE
# ======================
st.subheader("Summary")

st.metric("Total Candidate", len(df))
st.metric("Filtered Candidate", len(filtered_df))