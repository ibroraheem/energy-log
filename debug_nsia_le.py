import pandas as pd
import io

def inspect_nsia_le():
    file_path = "NSIA 02.csv"
    print(f"Inspecting {file_path} with utf-16-le")
    
    try:
        with open(file_path, 'rb') as f:
            df = pd.read_csv(f, encoding='utf-16-le', nrows=5)
        
        print(f"Columns (Raw): {df.columns.tolist()}")
        
        cols_clean = [str(c).strip().lstrip('\ufeff').lower() for c in df.columns]
        print(f"Columns (Cleaned): {cols_clean}")
        
        if 'date' in cols_clean:
            print("Found 'date'")
        
        if 'time' in cols_clean:
            print("Found 'time'")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    inspect_nsia_le()
