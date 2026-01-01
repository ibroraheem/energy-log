import utils
import pandas as pd
import os

def test_pipeline():
    print("Testing pipeline on pirano2-02.csv...")
    file_path = 'pirano2-02.csv'
    
    df, col_map = utils.load_data(file_path)
    
    if df is None:
        print("Dataset failed to load.")
        return

    print("Data loaded successfully.")
    print(df.head())
    print("Columns identified:", col_map)
    
    # Simple check, no AI test needed for this structure check
    metrics = utils.calculate_metrics(df)
    print("Metrics:", metrics)
    
    excel_bytes = utils.generate_excel(df, metrics['hourly_profile'])
    
    # Generate Word Report (mocking text if needed or using previous response)
    # We need to call this to define word_bytes
    if 'ai_text' not in locals():
         ai_text = "Analysis not available."
    word_bytes = utils.generate_word_report(metrics, fig, ai_text)
    
    print("\nVerifying outputs...")
    with open("test_output.xlsx", "wb") as f:
        f.write(excel_bytes)
    with open("test_output.docx", "wb") as f:
        f.write(word_bytes)
    with open("test_output.docx", "wb") as f:
        f.write(word_bytes)
        
    if os.path.exists("test_output.xlsx") and os.path.exists("test_output.docx"):
        print("SUCCESS: Output files created.")
    else:
        print("FAILURE: Output files missing.")

if __name__ == "__main__":
    test_pipeline()
