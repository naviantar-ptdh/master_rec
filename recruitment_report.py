import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ======================
# CONFIG (HARUS PALING ATAS)
# ======================
st.set_page_config(
    page_title="Recruitment Dashboard",
    layout="wide"
)

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

    # HEADER
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        st.image("logo_solid.png", width=70)
    with col_title:
        st.markdown("<h1>Recruitment Report</h1>", unsafe_allow_html=True)

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

    # FILTER
    f1, f2, f3 = st.columns(3)
    lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()))
    loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()))
    st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()))

    # APPLY
    mpp_filtered = mpp.copy()
    if lvl_sel != "All":
        mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]
    if loc_sel != "All":
        mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]
    if st_sel != "All":
        mpp_filtered = mpp_filtered[mpp_filtered["status"] == st_sel]

    # ================= MPP
    with st.expander("📈 MPP Dashboard"):

        pivot = mpp_filtered.groupby("divisi")[[
            "2026(r)", "2026(a)", "talent_management", "gap_fullfill_rec"
        ]].sum()

        pivot.columns = ["MPP", "Existing", "ADP_2026", "GAP"]

        st.dataframe(pivot)

        # ✅ TOTAL FIX
        total = pivot.sum().to_frame().T
        total.index = ["TOTAL"]

        st.write("### Total")
        st.dataframe(total)

# =========================================================
# ==================== TRACKING PAGE =======================
# =========================================================
elif st.session_state.page == "tracking":

    back_button()

    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        st.image("logo_solid.png", width=70)
    with col_title:
        st.title("Candidate & Position Tracking")

    @st.cache_data(ttl=60)
    def load_data():
        url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
        return pd.read_csv(url)

    df = load_data()
    df.columns = df.columns.str.lower()

    mode = st.radio("Search Mode", ["By Position", "By Candidate"], horizontal=True)

    if mode == "By Position":
        pos = st.selectbox("Select Position", df["position_name"].unique())
        st.dataframe(df[df["position_name"] == pos])

    else:
        cand = st.selectbox("Select Candidate", df["candidate_id"].unique())
        st.dataframe(df[df["candidate_id"] == cand])
