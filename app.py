import streamlit as st
import utils
import matplotlib.pyplot as plt

# --- Configuration ---
st.set_page_config(page_title="Energy Meter Log Analysis", layout="wide")

# --- Main App ---

st.title("Energy Meter Log Analysis")
st.sidebar.header("Configuration")

# Try to get key from secrets, otherwise input
default_key = st.secrets["general"]["GEMINI_API_KEY"] if "general" in st.secrets and "GEMINI_API_KEY" in st.secrets["general"] else ""
api_key = st.sidebar.text_input("Gemini API Key", value=default_key, type="password")

uploaded_file = st.sidebar.file_uploader("Upload Energy Log (CSV)", type=['csv'])

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
        fig = utils.generate_chart(metrics['hourly_profile'])
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
             st.warning("Enter Gemini API Key to enable AI observations.")

        # Downloads
        st.subheader("Downloads")
        
        excel_data = utils.generate_excel(df_raw, metrics['hourly_profile'])
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
