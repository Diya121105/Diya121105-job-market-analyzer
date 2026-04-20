# 🔍 Job Market Trend Analyzer
🔴 Live Demo: https://diya121105-job-market-analyzer-snd3bwhfbovnfmrcwwwhbo.streamlit.app/

A real-time job market analysis dashboard built with Python and Streamlit.

## Features
- Fetches live job listings using Adzuna API
- Cleans and processes raw data
- Extracts most in-demand skills from job descriptions
- Visualizes top hiring locations and companies
- Breaks down seniority levels (Junior/Mid/Senior)
- Export results as CSV

## Tech Stack
Python, Streamlit, Pandas, Plotly, Requests

## Architecture
Frontend: Streamlit → Backend: FastAPI → Data Source: Adzuna API

## How to Run
pip install -r requirements.txt
streamlit run app.py
