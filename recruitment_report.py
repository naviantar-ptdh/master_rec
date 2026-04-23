import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ==========================================
# 1. GLOBAL CONFIG (Hanya boleh 1x di awal)
# ==========================================
st.set_page_config(
    page_title="HR Recruitment Portal",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS untuk gaya Kartu (Grid) seperti di gambar
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        border-radius: 12px;
        height: 150px;
        background-color: #FFFFFF;
        border: 2px solid #F0F2F6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stButton button:hover {
        border-color: #FF9800;
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .main-title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 30px;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE & NAVIGATION
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = "home"

def go_home():
    st.session_state.page = "home"
    st.rerun()

# ==========================================
# 3. FUNGSI APLIKASI 1: REC REPORT
# ==========================================
def app_recruitment_report():
    if st.button("⬅ Kembali ke Menu"): go_home()
    
    # --- KODE ASLI APP 1 (Rec Report) START ---
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
    with col_logo: st.image("https://cdn-icons-png.flaticon.com/512/3094/3094837.png", width=70) # Placeholder logo
    with col_title: st.markdown("<h1 style='margin:0;'>Recruitment Report</h1>", unsafe_allow_html=True)

    if st.button("🔄 Refresh Data"): st.cache_data.clear()

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

    st.subheader("Global Filter")
    f1, f2, f3 = st.columns(3)
    lvl_sel = f1.selectbox("Level", ["All"] + sorted(mpp["level"].dropna().unique()))
    loc_sel = f2.selectbox("Location", ["All"] + sorted(mpp["loc"].dropna().unique()))
    st_sel = f3.selectbox("Status", ["All"] + sorted(mpp["status"].dropna().unique()))

    with st.expander("📊 Recruitment Database", expanded=True):
        filtered_df = df.copy()
        if lvl_sel != "All": filtered_df = filtered_df[filtered_df["level"] == lvl_sel]
        st.dataframe(filtered_df, use_container_width=True)
    # --- KODE ASLI APP 1 END ---

# ==========================================
# 4. FUNGSI APLIKASI 2: TRACKING
# ==========================================
def app_tracking_candidate():
    if st.button("⬅ Kembali ke Menu"): go_home()

    # --- KODE ASLI APP 2 (Tracking) START ---
    col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
    with col_logo: st.image("https://cdn-icons-png.flaticon.com/512/2643/2643506.png", width=70) # Placeholder logo
    with col_title: st.title("Candidate & Position Tracking")

    @st.cache_data(ttl=60)
    def load_data():
        url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
        return pd.read_csv(url)

    df = load_data()
    df.columns = df.columns.str.lower()

    mode = st.radio("Search Mode", ["By Position", "By Candidate"], horizontal=True)

    if mode == "By Position":
        pos_list = sorted(df["position_name"].dropna().unique())
        selected_pos = st.selectbox("Select Position", pos_list)
        filtered = df[df["position_name"] == selected_pos]
        st.dataframe(filtered, use_container_width=True)
    else:
        cand_list = sorted(df["candidate_id"].dropna().unique())
        selected_cand = st.selectbox("Select Candidate", cand_list)
        filtered = df[df["candidate_id"] == selected_cand]
        if not filtered.empty:
            row = filtered.iloc[0]
            st.subheader(f"Candidate: {selected_cand}")
            st.progress(0.5) # Placeholder progress
    # --- KODE ASLI APP 2 END ---

# ==========================================
# 5. LANDING PAGE UI
# ==========================================
if st.session_state.page == "home":
    st.markdown("<div class='main-title'>Recruitment Portal</div>", unsafe_allow_html=True)
    
    # Layout Grid Kartu
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📊")
        if st.button("RECRUITMENT\nREPORT"):
            st.session_state.page = "report"
            st.rerun()

    with col2:
        st.markdown("### 🔍")
        if st.button("TRACKING\nCANDIDATE"):
            st.session_state.page = "tracking"
            st.rerun()

    with col3:
        st.markdown("### ⚙️")
        st.button("MORE\nCOMING SOON", disabled=True)

    st.markdown("---")
    st.info("Pilih salah satu menu di atas untuk masuk ke aplikasi.")

# ==========================================
# 6. ROUTING LOGIC
# ==========================================
elif st.session_state.page == "report":
    app_recruitment_report()

elif st.session_state.page == "tracking":
    app_tracking_candidate()
