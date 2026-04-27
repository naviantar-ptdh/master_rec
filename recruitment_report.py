import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os  

#Tambahkan import os untuk mengecek file

# ==========================================
# 0. GLOBAL CONFIG
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Cek apakah set_page_config sudah pernah dipanggil (untuk keamanan)
try:
    st.set_page_config(
        page_title="HR Recruitment Portal",
        layout="wide"
    )
except:
    pass

# CSS untuk Landing Page
st.markdown("""
    <style>
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

    # --- KODE ASLI REPORT ---
    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo:
        if os.path.exists("logo_solid.png"):
            st.image("logo_solid.png", width=70)
        else:
            st.write("LOGO")
            
    with col_title:
        st.markdown("<h1 style='margin:0;'>Recruitment Report</h1>", unsafe_allow_html=True)

    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()

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

    for col in ["level", "loc", "status"]:
        if col in df.columns: df[col] = df[col].astype(str).str.strip()
        if col in mpp.columns: mpp[col] = mpp[col].astype(str).str.strip()

    st.subheader("Global Filter")
    f1, f2, f3 = st.columns(3)
    lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()), key="rep_lvl")
    loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()), key="rep_loc")
    st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()), key="rep_st")

    mpp_filtered = mpp.copy()
    if lvl_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["level"] == lvl_sel]
    if loc_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["loc"] == loc_sel]
    if st_sel != "All": mpp_filtered = mpp_filtered[mpp_filtered["status"] == st_sel]

    with st.expander("📊 Recruitment Database", expanded=True):
        filtered_df = df.copy()
        if lvl_sel != "All": filtered_df = filtered_df[filtered_df["level"] == lvl_sel]
        if loc_sel != "All": filtered_df = filtered_df[filtered_df["loc"] == loc_sel]
        if st_sel != "All": filtered_df = filtered_df[filtered_df["status"] == st_sel]
        st.dataframe(filtered_df, use_container_width=True)

    with st.expander("📈 MPP Dashboard", expanded=False):
        pivot_df = mpp_filtered[["divisi","2026(r)","2026(a)","talent_management","gap_fullfill_rec"]].copy()
        pivot_df = pivot_df.rename(columns={"2026(r)": "MPP","2026(a)": "Existing","talent_management": "ADP_2026","gap_fullfill_rec": "GAP"})
        pivot = pivot_df.groupby("divisi").sum(numeric_only=True)
        st.dataframe(pivot, use_container_width=True)

# ==========================================
# 2. APLIKASI KEDUA: TRACKING CANDIDATE
# ==========================================
def run_tracking():
    if st.button("⬅ Back to Landing Page"):
        st.session_state.page = "home"
        st.rerun()
    
    st.divider()

    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo:
        if os.path.exists("logo_solid.png"):
            st.image("logo_solid.png", width=70)
        else:
            st.write("LOGO")

    with col_title: 
        st.title("Candidate & Position Tracking")

    @st.cache_data(ttl=60)
    def load_data():
        url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
        return pd.read_csv(url)

    df = load_data()
    df.columns = df.columns.str.lower()
    
    for col in ["candidate_id", "position_name", "departement", "level", "loc", "status1", "last_progress"]:
        if col in df.columns: df[col] = df[col].fillna("Unknown")

    mode = st.radio("Search Mode", ["By Position", "By Candidate"], horizontal=True, key="track_mode")

    if mode == "By Position":
        pos_list = sorted(df["position_name"].dropna().unique())
        selected_pos = st.selectbox("Select Position", pos_list, key="track_pos")
        filtered = df[df["position_name"] == selected_pos]
        st.dataframe(filtered, use_container_width=True)
    else:
        cand_list = sorted(df["candidate_id"].dropna().unique())
        selected_cand = st.selectbox("Select Candidate", cand_list, key="track_cand")
        filtered = df[df["candidate_id"] == selected_cand]
        if not filtered.empty:
            row = filtered.iloc[0]
            st.subheader(f"Candidate: {selected_cand}")
            st.metric("Position", row.get("position_name", "-"))

# ==========================================
# 3. LANDING PAGE
# ==========================================
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;'>Recruitment Portal</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Cek apakah file report.png ada, jika tidak pakai icon 📊
        if os.path.exists("report.png"):
            st.image("report.png", width=120)
        else:
            st.markdown("<h1 style='text-align:center;'>📊</h1>", unsafe_allow_html=True)
            
        if st.button("📊 Recruitment Report", use_container_width=True):
            st.session_state.page = "report"
            st.rerun()

    with c2:
        # Cek apakah file tracking.png ada, jika tidak pakai icon 🔍
        if os.path.exists("tracking.png"):
            st.image("tracking.png", width=120)
        else:
            st.markdown("<h1 style='text-align:center;'>🔍</h1>", unsafe_allow_html=True)
            
        if st.button("🔍 Tracking Candidate", use_container_width=True):
            st.session_state.page = "tracking"
            st.rerun()

    with c3:
        if os.path.exists("dashboard.png"):
            st.image("dashboard.png", width=120)
        else:
            st.markdown("<h1 style='text-align:center;'>⚙️</h1>", unsafe_allow_html=True)
        st.button("⚙️ Coming Soon", disabled=True, use_container_width=True)

elif st.session_state.page == "report":
    run_rec_report()

elif st.session_state.page == "tracking":
    run_tracking()
