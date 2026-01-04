import streamlit as st
import utils
import matplotlib.pyplot as plt

# --- Configuration ---
st.set_page_config(page_title="Energy Meter Log Analysis", layout="wide")

# --- Main App ---

st.title("Energy Meter Log Analysis")
st.sidebar.header("Configuration")

# Securely load API Key
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    elif "general" in st.secrets and "GEMINI_API_KEY" in st.secrets["general"]:
        api_key = st.secrets["general"]["GEMINI_API_KEY"]
    else:
        api_key = ""
except FileNotFoundError:
    import os
    api_key = os.environ.get("GEMINI_API_KEY", "")

# Removed sidebar input to keep key hidden

uploaded_file = st.sidebar.file_uploader("Upload Energy Log (CSV/Excel)", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    with st.spinner("Processing Data..."):
        df_raw, col_map = utils.load_data(uploaded_file)
    
    if df_raw is not None:
        metrics = utils.calculate_metrics(df_raw)
        
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Global Peak (kW)", f"{metrics['global_peak_kw']:.2f}")
        col2.metric("Peak Time", metrics['peak_timestamp'].strftime('%H:%M'))
        col3.metric("Avg Power Factor", f"{metrics['avg_pf']:.2f}" if metrics['avg_pf'] else "N/A")
        col4.metric("Baseload (1-4am)", f"{metrics['baseload_kw']:.2f}")

        # Chart
        st.subheader("Load Profile")
        fig = utils.generate_chart(metrics['hourly_profile'], label=metrics.get('metric_label', 'Hourly Load Profile'))
        st.pyplot(fig)

        # AI Analysis
        st.subheader("Technical Observations")
        ai_text = "AI analysis not generated yet."
        
        if 'ai_analysis' not in st.session_state:
             st.session_state['ai_analysis'] = None
 
        if api_key:
            if st.button("Generate AI Observations"):
                with st.spinner("Generating Observations..."):
                    st.session_state['ai_analysis'] = utils.get_ai_analysis(metrics, api_key)

        if st.session_state['ai_analysis']:
            ai_text = st.session_state['ai_analysis']
            st.write(ai_text)
        elif not api_key:
             st.warning("AI observations disabled. Backend API Key not configured.")

        # Downloads
        st.subheader("Downloads")
        
        excel_data = utils.generate_excel(df_raw, metrics['hourly_profile'], agg_method=metrics.get('agg_method', 'sum'))
        st.download_button(
            label="Download Excel Report",
            data=excel_data,
            file_name="energy_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if st.session_state['ai_analysis'] or api_key: 
             word_data = utils.generate_word_report(metrics, fig, st.session_state['ai_analysis'] if st.session_state['ai_analysis'] else "Observations not generated.")
             st.download_button(
                label="Download Word Memo",
                data=word_data,
                file_name="energy_memo.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
