# Manufacturing Analytics Web App

This folder now includes a Streamlit application for processing Excel input files and generating downloadable reports.

## Run locally

1. Open a terminal.
2. Activate your Python environment.
3. Change into the `ManufacturingAnalytics` folder.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the web app:

```bash
streamlit run app.py
```

6. Open the browser URL that Streamlit shows.

## How it works

- Upload a `.xlsx` file.
- Choose either:
  - `EOL pivot / comment matrix` for the EOLData-style pivot output
  - `Analytics summary and dashboard` for the main analytics workbook
- Download the generated Excel report.

## Packaging for users without Python

After the app is working, you can package it as an executable using `PyInstaller` or deploy it to a hosting service such as Streamlit Cloud.
