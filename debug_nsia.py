import pandas as pd
import io

def inspect_nsia():
    file_path = "NSIA 02.csv"
    print(f"Inspecting {file_path}")
    
    encodings = ['utf-8', 'utf-16', 'ISO-8859-1']
    
    with open("debug_out_nsia.txt", "w", encoding='utf-8') as outfile:
        def log(msg):
            print(msg)
            outfile.write(str(msg) + "\n")

        for enc in encodings:
            log(f"\n--- Trying Encoding: {enc} ---")
            try:
                with open(file_path, 'rb') as f:
                    df = pd.read_csv(f, encoding=enc, nrows=5)
                
                log(f"Columns (Raw): {df.columns.tolist()}")
                
                cols_clean = [str(c).strip().lstrip('\ufeff').lower() for c in df.columns]
                log(f"Columns (Cleaned): {cols_clean}")
                
                if 'date' in cols_clean:
                    log("Found 'date'")
                else:
                    log("Missing 'date'")

                if 'time' in cols_clean:
                    log("Found 'time'")
                else:
                    log("Missing 'time'")
                    
            except Exception as e:
                log(f"Failed with {enc}: {e}")

if __name__ == "__main__":
    inspect_nsia()
