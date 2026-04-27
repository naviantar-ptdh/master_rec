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

# CSS untuk centering gambar dan styling tombol
st.markdown("""
    <style>
    /* Memaksa semua st.image di dalam kolom untuk ke tengah */
    [data-testid="stHorizontalBlock"] [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    .stButton button {
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI LOAD DATA (Agar tidak duplikasi kode) ---
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
    return pd.read_csv(url)

@st.cache_data(ttl=60)
def load_mpp():
    url = "https://docs.google.com/spreadsheets/d/10A2o_8D_C5d0HWl1ve6WNn9V7AdSqSufLnWr3lKtR9I/export?format=csv&gid=0"
    return pd.read_csv(url)

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

# ==========================================
# 1. HALAMAN: RECRUITMENT REPORT
# ==========================================
def run_rec_report():
    if st.button("⬅ Back to Landing Page", key="back_rep"):
        st.session_state.page = "home"
        st.rerun()
    st.divider()

    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo:
        if os.path.exists("logo_solid.png"): st.image("logo_solid.png", width=70)
        else: st.markdown("### 🏢")
    with col_title:
        st.markdown("<h1 style='margin:0;'>Recruitment Report</h1>", unsafe_allow_html=True)

    df = load_data()
    mpp = load_mpp()
    df.columns = df.columns.str.lower()
    mpp.columns = mpp.columns.str.lower()

    # --- Bagian Filter & Sub-bab (Sesuai kode Anda sebelumnya) ---
    st.subheader("Global Filter")
    f1, f2, f3 = st.columns(3)
    lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()), key="l1")
    loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()), key="l2")
    st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()), key="l3")
    
    # ... (lanjutkan logika filter dan expander Anda di sini) ...
    st.info("Halaman Report Aktif")

# ==========================================
# 2. HALAMAN: TRACKING CANDIDATE
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

    df = load_data()
    df.columns = df.columns.str.lower()
    
    # ... (lanjutkan logika tracking Anda di sini) ...
    st.info("Halaman Tracking Aktif")

# ==========================================
# 3. ROUTING & LANDING PAGE (DIPERBAIKI)
# ==========================================
if st.session_state.page == "home":
    # --- HEADER TENGAH ---
    _, center_col, _ = st.columns([1, 3, 1])
    with center_col:
        col_logo, col_title = st.columns([1, 2], vertical_alignment="center")
        with col_logo:
            if os.path.exists("logo_solid.png"): st.image("logo_solid.png", width=120)
            else: st.markdown("### LOGO")
        with col_title:
            st.markdown("<h1 style='margin: 0; white-space: nowrap;'>HR System Portal</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- MENU ICON (DENGAN INDENTASI BENAR) ---
    c1, c2, c3 = st.columns(3)

    with c1:
        if os.path.exists("report.png"): st.image("report.png", width=150)
        else: st.markdown("<h1 style='text-align: center;'>📊</h1>", unsafe_allow_html=True)
        
        if st.button("Recruitment Report", use_container_width=True, key="btn_rep"):
            st.session_state.page = "report"
            st.rerun()

    with c2:
        if os.path.exists("tracking.png"): st.image("tracking.png", width=150)
        else: st.markdown("<h1 style='text-align: center;'>🔍</h1>", unsafe_allow_html=True)
            
        if st.button("Tracking Candidate", use_container_width=True, key="btn_track"):
            st.session_state.page = "tracking"
            st.rerun()

    with c3:
        if os.path.exists("dashboard.png"): st.image("dashboard.png", width=150)
        else: st.markdown("<h1 style='text-align: center;'>⚙️</h1>", unsafe_allow_html=True)
            
        st.button("Coming Soon", disabled=True, use_container_width=True, key="btn_soon")

# --- KONTROL HALAMAN ---
elif st.session_state.page == "report":
    run_rec_report()

elif st.session_state.page == "tracking":
    run_tracking()
