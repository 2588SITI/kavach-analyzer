import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="KAVACH SENTINEL WEB", layout="wide")

st.title("🛡️ WR KAVACH RADIO DIAGNOSTIC DASHBOARD")
st.info("Identify if the problem is in LOCOMOTIVE RADIO or STATION TCAS.")

# Sidebar Uploaders
st.sidebar.header("📁 Upload Kavach Logs")
nms_file = st.sidebar.file_uploader("Upload TRNMSNMA Log (CSV)", type=['csv'])
rfcomm_file = st.sidebar.file_uploader("Upload RFCOMM Summary (CSV)", type=['csv'])

if nms_file and rfcomm_file:
    # Load Data
    nms_df = pd.read_csv(nms_file, low_memory=False)
    rf_df = pd.read_csv(rfcomm_file, low_memory=False)

    # 1. Radio Analysis (Loco Side)
    # Cleaning numeric columns
    nms_df['Pkt Len'] = pd.to_numeric(nms_df['Pkt Len'], errors='coerce').fillna(0)
    nms_df['Pkt Len2'] = pd.to_numeric(nms_df['Pkt Len2'], errors='coerce').fillna(0)
    
    r1_fail = (nms_df['Pkt Len'] < 10).mean() * 100
    r2_fail = (nms_df['Pkt Len2'] < 10).mean() * 100

    # 2. Station Analysis (Trackside)
    rf_df['Percentage'] = pd.to_numeric(rf_df['Percentage'], errors='coerce').fillna(0)
    stn_perf = rf_df.groupby('Station Id')['Percentage'].mean().reset_index()

    # Layout: Graphs
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📡 Station Reception %")
        fig1, ax1 = plt.subplots()
        ax1.bar(stn_perf['Station Id'], stn_perf['Percentage'], color='#42A5F5')
        ax1.axhline(y=90, color='red', linestyle='--')
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    with col2:
        st.subheader("🚂 Loco Radio Failure %")
        fig2, ax2 = plt.subplots()
        ax2.bar(['Radio 1', 'Radio 2'], [r1_fail, r2_fail], color=['orange', 'red'])
        ax2.set_ylim(0, 100)
        st.pyplot(fig2)

    # 3. Final Diagnosis
    st.subheader("🔍 Final Diagnostic Report")
    
    # Logic
    bad_stns = stn_perf[stn_perf['Percentage'] < 90]['Station Id'].tolist()
    
    if abs(r1_fail - r2_fail) > 25:
        st.error(f"🚨 **RESULT: LOCOMOTIVE HARDWARE FAULT.** One radio is significantly worse (R1: {r1_fail:.1f}%, R2: {r2_fail:.1f}%). Check Antenna/Cables.")
    elif bad_stns:
        st.warning(f"⚠️ **RESULT: STATION TCAS / TRACKSIDE FAULT.** Poor reception detected at: {', '.join(bad_stns)}. Loco hardware appears healthy.")
    else:
        st.success("✅ **RESULT: SYSTEM HEALTHY.** No major faults detected in Loco or Station Radios.")

else:
    st.warning("Please upload both CSV files from the sidebar to generate the report.")
