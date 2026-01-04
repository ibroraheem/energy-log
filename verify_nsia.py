import pandas as pd
import utils
import io
import os
import streamlit as st

# MOCK st
st.error = lambda x: print(f"ST_ERROR: {x}")
st.info = lambda x: print(f"ST_INFO: {x}")
st.warning = lambda x: print(f"ST_WARNING: {x}")

def get_mock_file(filepath):
    print(f"Reading file: {filepath}")
    with open(filepath, 'rb') as f:
        data = f.read()
    file_obj = io.BytesIO(data)
    file_obj.name = os.path.basename(filepath)
    return file_obj

def test_nsia():
    file_path = "NSIA 02.csv"
    try:
        # Load data
        df, col_map = utils.load_data(get_mock_file(file_path))
        if df is None:
             print("Failed to load data.")
             return

        print(f"\n--- Loaded {len(df)} rows ---\nKey Columns: {col_map}")
        if 'Timestamp' in df.columns:
             print(f"First Timestamp: {df['Timestamp'].iloc[0]}")
             print(f"Type: {type(df['Timestamp'].iloc[0])}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nsia()
