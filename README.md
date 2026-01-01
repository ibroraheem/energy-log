# Energy Meter Log Analysis App

A Streamlit application for automating the analysis of energy meter logs. It processes CSV data to generate daily load profiles, calculate key metrics (Peak, Power Factor, Baseload), and create professional Excel and Word reports with AI-generated technical observations.

## Installation

1.  **Install Dependencies**
    Open your terminal/command prompt in this directory and run:
    ```bash
    pip install -r requirements.txt --default-timeout=100
    ```
    *Note: The `--default-timeout=100` flag is recommended if you have a slow internet connection to prevent read timeouts.*

## Configuration

1.  **Gemini API Key**
    The app uses Google's Gemini API for generating technical observations.
    - The API key is configured in `.streamlit/secrets.toml`.
    - You can also enter it manually in the app sidebar if needed.

## Running the App

Run the following command in your terminal:
```bash
streamlit run app.py
```

## Usage Guide

1.  **Upload Data**:
    - Use the sidebar to upload your energy log CSV file.
    - The app expects columns for **Timestamp** (e.g., 'Date/Time'), **Active Power** (e.g., 'Active Power (W)'), and optionally **Power Factor**.
    - *A `mock_data.csv` is provided for testing.*

2.  **View Analysis**:
    - **Metrics**: detailed at the top (Global Peak, Peak Time, Avg PF, Nighttime Baseload).
    - **Chart**: A "Mean Daily Load Profile" chart displaying average kW per hour.

3.  **AI Observations**:
    - Click **"Generate AI Observations"** to get an AI-written summary of the trends.

4.  **Export Reports**:
    - **Excel Report**: Contains "Raw_Analysis" and "Hourly_Profiles" sheets.
    - **Word Memo**: A formal engineering memo including the metrics table, load profile chart, and the AI-generated observations.
