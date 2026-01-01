# Deploying to Streamlit Community Cloud

The easiest way to host this app for free is using **Streamlit Community Cloud**.

## Prerequisites
1.  A [GitHub Account](https://github.com/).
2.  A [Streamlit Cloud Account](https://streamlit.io/cloud) (you can sign up with GitHub).

## Step 1: Push Code to GitHub

1.  **Initialize Git** (if not already done):
    ```bash
    git init
    git add .
    git commit -m "Initial commit of Energy Analysis App"
    ```

2.  **Create a New Repository** on GitHub:
    - Go to GitHub -> New Repository.
    - Name it (e.g., `energy-log-analyst`).
    - **Do not** initialize with README/gitignore (you already have them locally).

3.  **Push your code**:
    - Copy the commands provided by GitHub under "…or push an existing repository from the command line".
    - Typically:
      ```bash
      git remote add origin https://github.com/YOUR_USERNAME/energy-log-analyst.git
      git branch -M main
      git push -u origin main
      ```

## Step 2: Deploy on Streamlit Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your GitHub repository (`energy-log-analyst`).
4.  Select the branch (`main`) and file (`app.py`).
5.  Click **"Deploy"**.

## Step 3: Configure Secrets (Crucial!)

Your local `.streamlit/secrets.toml` file is **not** uploaded to GitHub (for security). You must set your API key in the cloud dashboard.

1.  On your deployed app dashboard, click **"Manage app"** (bottom right) or the **Settings** menu.
2.  Go to **Secrets**.
3.  Paste your TOML configuration there:
    ```toml
    [general]
    GEMINI_API_KEY = "AIzaSyDPh-57lPo2JqkjxcHIaS1RO5dFwjOWZk0"
    ```
4.  Click **Save**. The app will restart and work!
