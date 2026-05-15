import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import streamlit.components.v1 as components
from pptx import Presentation
from pptx.util import Inches
from datetime import datetime
from io import BytesIO

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

    # ==========================================
    # FUNCTION FILL TABLE
    # ==========================================
    def fill_table(table, data, start_row=1):
    
        for i, row_data in enumerate(data):
    
            row_idx = start_row + i
    
            if row_idx >= len(table.rows):
                break
    
            for col_idx, value in enumerate(row_data):
    
                if col_idx >= len(table.columns):
                    break
    
                table.cell(row_idx, col_idx).text = str(value)
    
    
    # ==========================================
    # FUNCTION GENERATE PPT
    # ==========================================
    def generate_recruitment_ppt(df, mpp_filtered, final):
    # Gunakan template yang ada
        try:
            prs = Presentation("Recruitment Report Template.pptx")
        except:
            # Fallback jika file tidak ditemukan saat testing
            prs = Presentation() 
        
        letters = list("ABCDEFGHIJKL")
        
        # Mapping slide berdasarkan urutan di template Anda
        # Format: (Nama Site, Index Slide Summary)
        normal_sites = [
            ("BCP", 1),
            ("KCP", 4),
            ("ACP", 7),
        ]
    
        for site, start_idx in normal_sites:
            summary_slide = prs.slides[start_idx]
            fit_slide = prs.slides[start_idx + 1]
            pipeline_slide = prs.slides[start_idx + 2]
    
            # 1. FILTER DATA SITE (Gunakan .upper() untuk keamanan)
            site_mpp = mpp_filtered[mpp_filtered["loc"].astype(str).str.upper() == site].reset_index(drop=True)
            site_df = df[df["loc"].astype(str).str.upper() == site].reset_index(drop=True)
    
            # 2. SUMMARY REPLACEMENTS
            replacements = {}
            for i, letter in enumerate(letters):
                if i < len(site_mpp):
                    row = site_mpp.iloc[i]
                    # Cari data pipeline di tabel 'final' yang cocok dengan divisi ini
                    # Pastikan kolom 'divisi' ada di dataframe 'final'
                    div_name = row.get("divisi", "")
                    div_pipeline = final[final["divisi"] == div_name]
    
                    replacements[f"{{{{{letter}}}}}"] = str(div_name)
                    replacements[f"{{{{MPP_{letter}}}}}"] = str(int(row.get("2026(r)", 0)))
                    replacements[f"{{{{ACT_{letter}}}}}"] = str(int(row.get("2026(a)", 0)))
                    replacements[f"{{{{DEV_{letter}}}}}"] = str(int(row.get("gap_fullfill_rec", 0)))
                    replacements[f"{{{{ADP_{letter}}}}}"] = str(int(row.get("talent_management", 0)))
                    replacements[f"{{{{EXT_{letter}}}}}"] = str(int(row.get("ext", 0)))
                    
                    # Ambil data dari tabel final (Pipeline)
                    if not div_pipeline.empty:
                        replacements[f"{{{{int_{letter}}}}}"] = str(int(div_pipeline["HR Interview"].values[0]))
                        replacements[f"{{{{psy_{letter}}}}}"] = str(int(div_pipeline["Psychotest"].values[0]))
                        replacements[f"{{{{ofe_{letter}}}}}"] = str(int(div_pipeline["Offering"].values[0]))
                        replacements[f"{{{{mcu_{letter}}}}}"] = str(int(div_pipeline["MCU"].values[0]))
                    else:
                        for k in ["int", "psy", "ofe", "mcu"]: 
                            replacements[f"{{{{{k}_{letter}}}}}"] = "0"
                else:
                    # Jika data kosong, bersihkan placeholder agar tidak merusak tampilan PPT
                    replacements[f"{{{{{letter}}}}}"] = ""
                    for k in ["MPP", "ACT", "DEV", "ADP", "EXT", "int", "psy", "ofe", "mcu"]:
                        replacements[f"{{{{{k}_{letter}}}}}"] = ""
    
            # PROSES REPLACE DI TABEL SUMMARY
            for shape in summary_slide.shapes:
                if shape.has_table:
                    for r in shape.table.rows:
                        for cell in r.cells:
                            for key, val in replacements.items():
                                if key in cell.text:
                                    cell.text = cell.text.replace(key, val)
    
            # 3. FIT TO WORK SLIDE
            fit_df = site_df[site_df["result_fu_mcu"].astype(str).str.upper() == "FIT TO WORK"].reset_index(drop=True)
            fit_replaces = {}
            for i, letter in enumerate(letters):
                if i < len(fit_df):
                    f_row = fit_df.iloc[i]
                    fit_replaces[f"{{{{{letter}}}}}"] = str(f_row.get("candidate_id", ""))
                    fit_replaces[f"{{{{loc_{letter}}}}}"] = str(f_row.get("loc", ""))
                    fit_replaces[f"{{{{Pos_{letter}}}}}"] = str(f_row.get("position_name", ""))
                    fit_replaces[f"{{{{dep_{letter}}}}}"] = str(f_row.get("divisi", ""))
                    fit_replaces[f"{{{{result_{letter}}}}}"] = "FIT TO WORK"
                    fit_replaces[f"{{{{date_{letter}}}}}"] = str(f_row.get("date_onboarding", "-"))
                else:
                    fit_replaces[f"{{{{{letter}}}}}"] = ""
                    # ... bersihkan sisa placeholder fit ...
    
            for shape in fit_slide.shapes:
                if shape.has_table:
                    for r in shape.table.rows:
                        for cell in r.cells:
                            for key, val in fit_replaces.items():
                                if key in cell.text:
                                    cell.text = cell.text.replace(key, val)
    
        # 4. JKT SLIDE (Slide 10)
        jkt_slide = prs.slides[10]
        total_jkt = len(df[df["loc"].astype(str).str.upper() == "JKT"])
        for shape in jkt_slide.shapes:
            if hasattr(shape, "text") and "{{TOTAL_JKT}}" in shape.text:
                shape.text = shape.text.replace("{{TOTAL_JKT}}", str(total_jkt))
    
        ppt_buffer = BytesIO()
        prs.save(ppt_buffer)
        ppt_buffer.seek(0)
        return ppt_buffer
                
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
       
        st.subheader("Candidate Status")
        s1, s2, s3 = st.columns(3)
        if "status1" in filtered_df.columns:
            status_series = filtered_df["status1"].str.upper()
        s1.metric("On-Progress", (status_series == "OPEN").sum())
        s2.metric("Failed", (status_series == "FAILED").sum())
        s3.metric("Hiring", (status_series == "CLOSE").sum())
        st.dataframe(filtered_df, use_container_width=True)

    # SUB 2: MPP DASHBOARD
    with st.expander("📈 MPP Dashboard", expanded=False):
        pivot_df = mpp_filtered[["divisi","2026(r)","2026(a)","talent_management","gap_fullfill_rec"]].copy()
        pivot_df = pivot_df.rename(columns={"2026(r)": "MPP","2026(a)": "Existing","talent_management": "ADP_2026","gap_fullfill_rec": "GAP"})
        pivot = pivot_df.groupby("divisi").sum(numeric_only=True)
        pivot.loc['TOTAL'] = pivot.sum(numeric_only=True)
        st.dataframe(pivot, use_container_width=True)
        st.download_button("Download MPP Image", create_table_image(pivot), "mpp.png", "image/png", key="d1")

    # SUB 3: MPP VS PIPELINE (PENTING!)
    with st.expander("📊 MPP vs Recruitment Pipeline", expanded=False):
        st.subheader("Pipeline Analysis (By Divisi)")
        col_d1, col_d2 = st.columns(2)
        start_date = col_d1.date_input("Start Date", key="sd_rep")
        end_date = col_d2.date_input("End Date", key="ed_rep")
        
        df_pipe = df.copy()
        valid_dept = mpp_filtered["divisi"].unique()
        df_pipe = df_pipe[df_pipe["divisi"].isin(valid_dept)]
        
        date_cols = ["start_screening_cv","start_interview_hr","start_interview_user","start_psychotest","start_offering","start_mcu","start_review_mcu","start_fu_mcu","date_onboarding"]
        for col in date_cols:
            if col in df_pipe.columns: df_pipe[col] = pd.to_datetime(df_pipe[col], errors="coerce")

        def count_stg(col):
            t = df_pipe[(df_pipe[col] >= pd.to_datetime(start_date)) & (df_pipe[col] <= pd.to_datetime(end_date))]
            return t.groupby("divisi")[col].count()

        pipeline = pd.DataFrame()
        stages = ["Screening CV","HR Interview","User Interview","Psychotest","Offering","MCU","Review MCU","FU MCU","Onboarding"]
        cols = ["start_screening_cv","start_interview_hr","start_interview_user","start_psychotest","start_offering","start_mcu","start_review_mcu","start_fu_mcu","date_onboarding"]
        for s, c in zip(stages, cols): pipeline[s] = count_stg(c)
        
        mpp_sum = mpp_filtered.groupby(["divisi"])[["2026(r)","2026(a)","talent_management","gap_fullfill_rec"]].sum(numeric_only=True)
        final = mpp_sum.merge(pipeline.fillna(0), left_on="divisi", right_index=True, how="left").fillna(0).reset_index()
        final.loc['TOTAL'] = final.sum(numeric_only=True)
        st.dataframe(final, use_container_width=True)
        st.download_button("Download Pipeline Image", create_table_image(final), "pipeline.png", "image/png", key="d2")
        # ==========================================
        # GENERATE PPT BUTTON
        # ==========================================
        ppt_file = generate_recruitment_ppt(
            df,
            mpp_filtered,
            final
        )
        
        st.download_button(
            label="📥 Download Recruitment Report PPT",
            data=ppt_file,
            file_name=f"Recruitment_Report_{datetime.today().strftime('%Y%m%d')}.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

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

        
        disp = filtered[["candidate_id","position_name","departement","level","loc","last_progress","total_lt","status1"]].copy()
        disp["total_lt"] = disp["total_lt"].astype(int)
        disp = disp.rename(columns={"status1": "Hiring Status"})
        st.dataframe(disp.style.map(color_st, subset=["Hiring Status"]), use_container_width=True)
        s4, s1, s2, s3 = st.columns(4)
        if "Hiring Status" in disp.columns:
            status_series = disp["Hiring Status"].str.upper()
        s1.metric("On-Progress", (status_series == "OPEN").sum())
        s2.metric("Failed", (status_series == "FAILED").sum())
        s3.metric("Hiring", (status_series == "CLOSE").sum())
        s4.metric("Total Candidate", len(disp))

    # --- BY CANDIDATE ---
    else:
        cand_list = sorted(df["candidate_id"].dropna().unique())
        sel_cand = st.selectbox("Select Candidate", cand_list, key="s_cand")
        filt = df[df["candidate_id"] == sel_cand]
        if filt.empty: st.stop()
        row = filt.iloc[0]

        st.subheader(f"Candidate: {sel_cand}")
        
        # 4 KOLOM METRIK (Sesuai Foto)
        m1, m2, m3, m4, m5 = st.columns([2, 1, 1, 1, 1])
        m1.metric("Position", row.get("position_name", "-"))
        m2.metric("Department", row.get("departement", "-"))
        m3.metric("Level", row.get("level", "-"))
        m4.metric("Location", row.get("loc", "-"))

        sla_value = row.get("total_lt", "-")
        if isinstance(sla_value, (int, float)):
            sla_value = int(sla_value)

        m5.metric("SLA", sla_value)
        

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
# 3. APLIKASI: Stream Dashboard
# ==========================================

def run_rec_dashboard():
    if st.button("⬅ Back to Landing Page", key="back_dash"):
        st.session_state.page = "home"
        st.rerun()
    
    st.divider()

    st.title("Recruitment Dashboard")
    st.caption("Powered by Looker Studio")

    components.html(
        """
        <iframe width="100%" height="700"
        src="https://datastudio.google.com/embed/reporting/a425625f-0af4-4b5c-8826-218a929b1333/page/YwLxF"
        frameborder="0"
        style="border:0"
        allowfullscreen>
        </iframe>
        """,
        height=700
    )

# ==========================================
# 4. ROUTING & LANDING PAGE
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
        if os.path.exists("dashboard.png"):
            st.image("dashboard.png", width=120)

        if st.button("📊 Recruitment Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

elif st.session_state.page == "report": run_rec_report()
elif st.session_state.page == "tracking": run_tracking()
elif st.session_state.page == "dashboard": run_rec_dashboard()
