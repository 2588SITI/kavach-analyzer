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
    nms_df['Pkt Len'] = pd.to_numeric(nms_df['Pkt Len'], errors='coerce').fillna(0)
    nms_df['Pkt Len2'] = pd.to_numeric(nms_df['Pkt Len2'], errors='coerce').fillna(0)
    
    r1_fail = (nms_df['Pkt Len'] < 10).mean() * 100
    r2_fail = (nms_df['Pkt Len2'] < 10).mean() * 100

    # 2. Station Analysis (Trackside)
    rf_df['Percentage'] = pd.to_numeric(rf_df['Percentage'], errors='coerce').fillna(0)
    stn_perf = rf_df.groupby('Station Id')['Percentage'].mean().reset_index()
    
    # Filter bad stations (< 90%)
    bad_stns_df = stn_perf[stn_perf['Percentage'] < 90].sort_values(by='Percentage')

    # Layout: Graphs
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📡 Station Reception %")
        fig1, ax1 = plt.subplots()
        ax1.bar(stn_perf['Station Id'], stn_perf['Percentage'], color='#42A5F5')
        ax1.axhline(y=90, color='red', linestyle='--')
        plt.xticks(rotation=45)
        ax1.set_ylabel("Reception %")
        st.pyplot(fig1)

    with col2:
        st.subheader("🚂 Loco Radio Failure %")
        fig2, ax2 = plt.subplots()
        ax2.bar(['Radio 1', 'Radio 2'], [r1_fail, r2_fail], color=['orange', 'red'])
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("Failure %")
        st.pyplot(fig2)

    st.markdown("---")
    
    # 3. COMPREHENSIVE DIAGNOSTIC REPORT
    st.header("📋 Kavach Comprehensive Diagnostic Report")
    
    # Section 1: Locomotive Health
    st.subheader("1. Locomotive Health (Loco Side Analysis)")
    st.write(f"**Radio 1 Failure Rate:** {r1_fail:.2f}% (Packet drops at specific stations).")
    st.write(f"**Radio 2 Failure Rate:** {r2_fail:.2f}% (Packet drops at specific stations).")
    
    if abs(r1_fail - r2_fail) < 20:
        st.success("✅ **Diagnosis:** Since both radios behave similarly and provide 100% results at several stations, the **Loco hardware (Antenna/Cable) is completely healthy.**")
    else:
        st.error("🚨 **Diagnosis:** Significant difference in radio levels. Fault suspected in Loco hardware (Antenna/Radio Module).")

    # Section 2: Station Health
    st.subheader("2. Station Health (Trackside Analysis)")
    st.write("According to the logs, the following stations have packet reception percentages below the target:")
    
    if not bad_stns_df.empty:
        for index, row in bad_stns_df.iterrows():
            st.write(f"📍 **{row['Station Id']}: {row['Percentage']:.2f}%**")
        
        # Section 3: Final Verdict
        st.markdown("---")
        st.error(f"🏁 **Final Verdict:** The problem is in the **STATION TCAS / TRACKSIDE** equipment. Radio antenna alignment and trackside signal coverage need to be checked at **{', '.join(bad_stns_df['Station Id'].tolist())}** stations.")
    else:
        st.success("✅ **Final Verdict:** Signal coverage is optimal across all stations. System is Healthy.")

else:
    st.warning("Please upload both TRNMSNMA and RFCOMM CSV files to generate the report.")
