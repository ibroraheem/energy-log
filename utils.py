import pandas as pd
import matplotlib.pyplot as plt
import io
import xlsxwriter
import google.generativeai as genai
from docx import Document
from docx.shared import Inches
import streamlit as st # Need st for st.error, st.info, st.cache_data if used

# Use st.cache_data for performance if we were in handling streamlit, 
# but for pure utils we might want to avoid direct st calls if possible 
# to keep it clean. However, I used st.error in load_data. 
# I will modify load_data to return errors or print them, or pass a logger.
# For simplicity, I'll keep st dependency but check if it's running in streamlit?
# actually, st.error works even if not in streamlit? No, it prints to stderr or no-op?
# Let's keep st calls for now as it makes the app code simpler.

def load_data(file):
    """
    Loads CSV data, identifies relevant columns, and performs unit conversion.
    """
    try:
        df = pd.read_csv(file)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None, None

    # Column Identification
    col_map = {}
    
    # Timestamp identification priority:
    # 1. 'localtime' (explicit user mention)
    # 2. 'Date/Time' (common standard)
    # 3. 'timestamp'
    # 4. Any column with 'date' or 'time'
    
    columns_lower = [c.lower() for c in df.columns]
    
    if 'localtime' in columns_lower:
        col_map['timestamp'] = df.columns[columns_lower.index('localtime')]
    elif 'date/time' in columns_lower:
        col_map['timestamp'] = df.columns[columns_lower.index('date/time')]
    elif 'timestamp' in columns_lower:
        col_map['timestamp'] = df.columns[columns_lower.index('timestamp')]
    else:
        # Fallback to substring search
        time_cols = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower()]
        if time_cols:
            col_map['timestamp'] = time_cols[0]
        else:
            st.error("Could not identify a Timestamp column (looking for 'localtime', 'Date/Time', 'timestamp', etc.).")
            return None, None
            
    st.info(f"Identified Timestamp Column: {col_map['timestamp']}")

    # Power
    power_cols = [c for c in df.columns if ('watt' in c.lower() or 'power' in c.lower()) and 'factor' not in c.lower()]
    if power_cols:
        col_map['power'] = power_cols[0]
        st.info(f"Identified Power Column: {col_map['power']}")
    else:
        st.error("Could not identify a Power column (looking for 'watt' or 'power').")
        return None, None

    # Power Factor
    pf_cols = [c for c in df.columns if 'pf' in c.lower() or 'factor' in c.lower()]
    if pf_cols:
        col_map['pf'] = pf_cols[0]
    else:
        st.warning("Could not identify a Power Factor column. Assuming PF=1.0 for now.")
        col_map['pf'] = None


    # Cleaning and Conversion
    try:
        # Attempt standard parsing, prioritizing dayfirst for DD.MM.YYYY formats common in CSVs
        df[col_map['timestamp']] = pd.to_datetime(df[col_map['timestamp']], dayfirst=True, errors='coerce')
        
        # If too many NaTs (e.g., > 90% failure), maybe it's a unix timestamp?
        # But 'localtime' implies string. 'timestamp' implies unix.
        # If we picked 'timestamp' column which is numeric:
        if df[col_map['timestamp']].isna().mean() > 0.9:
            # Check if it looks like unix epoch (numeric)
            # Re-read or just check the raw values? 
            # It's hard to rollback the .dt conversion in-place easily without reloading or keeping a copy.
            # But wait, to_datetime with errors='coerce' turns non-parsable to NaT.
            # If we selected 'timestamp' (unix), to_datetime might have failed if it expected strings or if numbers were large? 
            # Actually pd.to_datetime on unix int usually works if unit is specified, otherwise it assumes nanoseconds (default) 
            # which for 1714113225 (seconds) -> 1970ish. 
            # Let's not over-engineer unless needed. The user emphasized 'localtime'.
            pass
            
    except Exception as e:
        st.error(f"Error parsing timestamp: {e}")
        return None, None

    # Convert to numeric, forcing errors to NaN
    df[col_map['power']] = pd.to_numeric(df[col_map['power']], errors='coerce')
    if col_map['pf']:
        df[col_map['pf']] = pd.to_numeric(df[col_map['pf']], errors='coerce')
    
    df = df.dropna(subset=[col_map['power'], col_map['timestamp']])

    # Unit Conversion logic
    max_power = df[col_map['power']].max()
    if max_power > 2000:
        df['kW'] = df[col_map['power']] / 1000.0
        st.info(f"Detected Power in Watts (Max: {max_power:.2f}). Converted to kW.")
    else:
        df['kW'] = df[col_map['power']]
        st.info(f"Detected Power in kW (Max: {max_power:.2f}). No conversion needed.")
    
    # Rename for consistency
    rename_dict = {col_map['timestamp']: 'Timestamp', col_map['pf']: 'Power Factor'} if col_map['pf'] else {col_map['timestamp']: 'Timestamp'}
    df = df.rename(columns=rename_dict)
    
    return df, col_map

def calculate_metrics(df):
    """
    Aggregates data and calculates required metrics.
    """
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    
    hourly_profile = df.groupby('Hour')['kW'].mean()

    global_peak_kw = df['kW'].max()
    peak_timestamp = df.loc[df['kW'].idxmax(), 'Timestamp']
    
    avg_pf = df['Power Factor'].mean() if 'Power Factor' in df.columns else None

    baseload_mask = (df['Hour'] >= 1) & (df['Hour'] <= 4)
    baseload_kw = df.loc[baseload_mask, 'kW'].mean()

    return {
        'hourly_profile': hourly_profile,
        'global_peak_kw': global_peak_kw,
        'peak_timestamp': peak_timestamp,
        'avg_pf': avg_pf,
        'baseload_kw': baseload_kw
    }

def generate_chart(hourly_profile):
    """
    Generates Matplotlib figure for the hourly profile.
    """
    plt.style.use('ggplot') # Ensure style is set
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(hourly_profile.index, hourly_profile.values, marker='o', linestyle='-')
    ax.set_title("Mean Daily Load Profile")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Power (kW)")
    ax.set_xticks(range(0, 24))
    ax.grid(True)
    return fig

def generate_excel(df_raw, hourly_profile):
    """
    Generates an Excel file with raw data, formulas, and charts.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write Raw Data
        df_raw.to_excel(writer, sheet_name='Raw_Analysis', index=False)
        workbook = writer.book
        worksheet_raw = writer.sheets['Raw_Analysis']
        worksheet_profile = workbook.add_worksheet('Hourly_Profiles')
        
        # Identify columns for formulas
        # We need the Excel column letter for 'Hour' and 'kW' in 'Raw_Analysis'
        # df_raw columns are written starting at A1 (headers). Data starts row 2.
        cols = df_raw.columns.tolist()
        
        def get_col_letter(name):
            try:
                idx = cols.index(name)
                # Convert 0-index to letter (A, B, C...)
                # Simple implementation for < 26 columns
                return chr(65 + idx)
            except ValueError:
                return None

        col_hour = get_col_letter('Hour')
        col_kw = get_col_letter('kW')
        
        # Write Headers for Profile
        worksheet_profile.write('A1', 'Hour of Day')
        worksheet_profile.write('B1', 'Average Power (kW)')
        
        # Write Formulas for 0-23 hours
        # Formula: =AVERAGEIF(Raw_Analysis!C:C, A2, Raw_Analysis!D:D)
        # assuming C is Hour and D is kW.
        
        if col_hour and col_kw:
            desc_format = workbook.add_format({'num_format': '0.00'})
            
            for i in range(24):
                row = i + 2 # Excel is 1-indexed, +1 for header
                
                # Write Hour
                worksheet_profile.write(f'A{row}', i)
                
                # Write Formula
                # AVERAGEIF(range, criteria, [average_range])
                # Range: Raw_Analysis!HourColumn:HourColumn
                # Criteria: A{row} (the hour value in this sheet)
                # AvgRange: Raw_Analysis!kWColumn:kWColumn
                formula = f'=AVERAGEIF(Raw_Analysis!{col_hour}:{col_hour}, A{row}, Raw_Analysis!{col_kw}:{col_kw})'
                worksheet_profile.write_formula(f'B{row}', formula, desc_format)
        else:
            # Fallback if columns not found (shouldn't happen if Calculate Metrics ran)
            worksheet_profile.write('C1', 'Error: Could not locate data columns for formulas.')
            # Write static data as backup
            hourly_profile.to_excel(writer, sheet_name='Hourly_Profiles_Backup')

        # --- Add Chart ---
        chart = workbook.add_chart({'type': 'line'})
        
        # Configure Series
        # Categories (X): Hourly_Profiles!$A$2:$A$25
        # Values (Y): Hourly_Profiles!$B$2:$B$25
        chart.add_series({
            'name':       'Mean Daily Load Profile',
            'categories': '=Hourly_Profiles!$A$2:$A$25',
            'values':     '=Hourly_Profiles!$B$2:$B$25',
            'line':       {'color': 'blue'},
        })
        
        chart.set_title ({'name': 'Daily Load Profile'})
        chart.set_x_axis({'name': 'Hour of Day'})
        chart.set_y_axis({'name': 'Power (kW)'})
        chart.set_style(10) # A nice built-in style
        
        worksheet_profile.insert_chart('D2', chart)

    return output.getvalue()

def get_ai_analysis(metrics, api_key):
    """
    Generates technical observations using Gemini.
    """
    if not api_key:
        return "API Key missing."
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a Technical Data Analyst writing for a Senior Project Engineer.
    Write a comprehensive and detailed technical analysis (approx. 500-600 words) based on the following energy meter metrics.
    
    Structure your response into these sections:
    1. Load Profile Analysis: Discuss the daily consumption pattern, peak timing, and baseload.
    2. Power Factor Assessment: Evaluate the efficiency implications of the average power factor.
    3. Anomaly Detection: Highlight any unusual spikes or dips if evident from the metrics.
    4. Operational Implications: Discuss what these metrics mean for the electrical system's health.
    
    Tone: Professional, objective, and observation-based. Avoid generic advice; focus on the data.
    
    Metrics:
    - Global Peak: {metrics['global_peak_kw']:.2f} kW at {metrics['peak_timestamp']}
    - Average Power Factor: {metrics['avg_pf']:.2f}
    - Nighttime Baseload (01:00-04:00): {metrics['baseload_kw']:.2f} kW
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI analysis: {e}"

def generate_word_report(metrics, chart_fig, ai_text):
    """
    Generates a Word document.
    """
    doc = Document()
    doc.add_heading('Energy Audit Report', 0)
    
    doc.add_paragraph(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    doc.add_paragraph("To: Senior Project Engineer")
    doc.add_paragraph("From: Technical Data Analyst")
    
    doc.add_heading('Summary', level=1)
    
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Metric'
    hdr_cells[1].text = 'Value'
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Global Peak Load'
    row_cells[1].text = f"{metrics['global_peak_kw']:.2f} kW"
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Peak Timestamp'
    row_cells[1].text = str(metrics['peak_timestamp'])
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Average Power Factor'
    row_cells[1].text = f"{metrics['avg_pf']:.2f}"
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'Nighttime Baseload'
    row_cells[1].text = f"{metrics['baseload_kw']:.2f} kW"
    
    doc.add_heading('Daily Load Profile', level=1)
    
    # Save plot to buffer
    img_buffer = io.BytesIO()
    chart_fig.savefig(img_buffer, format='png', dpi=300)
    img_buffer.seek(0)
    doc.add_picture(img_buffer, width=Inches(6.0))
    
    doc.add_heading('Observation', level=1)
    doc.add_paragraph(ai_text)
    
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()
