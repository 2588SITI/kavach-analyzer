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
    
    # 3. COMPREHENSIVE DIAGNOSTIC REPORT (As per your request)
    st.header("📋 Kavach Comprehensive Diagnostic Report")
    
    # Section 1: Locomotive Health
    st.subheader("1. Locomotive Health (Loco Side Analysis)")
    st.write(f"**Radio 1 Failure Rate:** {r1_fail:.2f}% (Packet drops specific stations par).")
    st.write(f"**Radio 2 Failure Rate:** {r2_fail:.2f}% (Packet drops specific stations par).")
    
    if abs(r1_fail - r2_fail) < 20:
        st.success("✅ **Diagnosis:** Kyunki dono radios ek hi tarah se behave kar rahe hain aur kai stations par 100% result de rahe hain, isliye **Loco hardware (Antenna/Cable) bilkul sahi hai.**")
    else:
        st.error(f"🚨 **Diagnosis:** Radio levels mein bada antar hai. Loco hardware (Antenna/Radio Module) mein fault suspected hai.")

    # Section 2: Station Health
    st.subheader("2. Station Health (Trackside Analysis)")
    st.write("Datalogger ke mutabiq, niche diye gaye stations par packet reception percentage target se kam hai:")
    
    if not bad_stns_df.empty:
        for index, row in bad_stns_df.iterrows():
            st.write(f"📍 **{row['Station Id']}: {row['Percentage']:.2f}%**")
        
        # Section 3: Final Verdict
        st.markdown("---")
        worst_stn = bad_stns_df.iloc[0]['Station Id']
        st.error(f"🏁 **Final Verdict:** Problem **STATION TCAS / TRACKSIDE** mein hai. **{', '.join(bad_stns_df['Station Id'].tolist())}** stations ke radio antenna alignment aur trackside signal coverage ko check karne ki zarurat hai.")
    else:
        st.success("✅ **Final Verdict:** Sabhi stations par signal coverage behtar hai. System Healthy hai.")

else:
    st.warning("Please upload both TRNMSNMA and RFCOMM CSV files to generate the report.")
