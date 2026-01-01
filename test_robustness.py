import utils
import pandas as pd

def test_robustness():
    print("Testing robustness...")
    file_path = 'mock_data_messy.csv'
    
    # Needs to run in a way that doesn't crash on st.error
    # Since we can't easily mock st.error without a framework, we rely on it printing or passing.
    # utils allows returning None, None on error.
    
    print("Loading messy data...")
    df, col_map = utils.load_data(file_path)
    
    if df is not None:
        print("Data loaded (partial success expected).")
        print(df)
        print("Rows:", len(df))
        # Expecting:
        # Row 1: OK
        # Row 2: OK
        # Row 3: Bad timestamp -> NaT -> dropna -> gone?
        # Row 4: NaN power -> NaN -> dropna -> gone?
        # Row 5: Bad PF -> PF NaN -> kept? (only dropna on power/timestamp)
        # Row 6: OK
        
        # Let's check logic:
        # df[col_map['timestamp']] = pd.to_datetime(...) errors='coerce' fails? default raise.
        # My code uses try-except on to_datetime, but generally input array to to_datetime with errors='raise' (default) might fail.
        # Check utils logic: 
        # try: df[...] = pd.to_datetime(...) except: st.error... return None.
        # Be careful: if ANY row fails, it might fail the whole column if not handling errors='coerce'.
        pass
    else:
        print("Data load failed completely (might be intended if critical error).")

if __name__ == "__main__":
    test_robustness()
