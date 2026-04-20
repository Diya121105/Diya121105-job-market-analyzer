import requests
import pandas as pd
import streamlit as st
import plotly.express as px

APP_ID = "6a00f514"
API_KEY = "e1c19bb14cb5218c8f7ac33e0e88892c"

def fetch_jobs(keyword="python", country="in", pages=3):
    all_jobs = []
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {
            "app_id": APP_ID,
            "app_key": API_KEY,
            "what": keyword,
            "results_per_page": 20
        }
        response = requests.get(url, params=params)
        data = response.json()
        all_jobs.extend(data.get("results", []))
    return all_jobs

def process_jobs(jobs):
    processed = []
    for job in jobs:
        processed.append({
            "title": job.get("title", "N/A"),
            "company": job.get("company", {}).get("display_name", "N/A"),
            "location": job.get("location", {}).get("display_name", "N/A"),
            "salary_min": job.get("salary_min", 0),
            "salary_max": job.get("salary_max", 0),
            "description": job.get("description", "")
        })
    return pd.DataFrame(processed)

def extract_skills(df):
    skills_list = [
        "python", "sql", "machine learning", "django", "flask",
        "pandas", "numpy", "tensorflow", "aws", "docker",
        "javascript", "react", "git", "excel", "power bi"
    ]
    skill_counts = {}
    for skill in skills_list:
        count = df["description"].str.lower().str.contains(skill).sum()
        skill_counts[skill] = count
    return pd.Series(skill_counts).sort_values(ascending=False)

# --- Streamlit UI ---
st.set_page_config(page_title="Job Market Analyzer", layout="wide")
st.title("🔍 Job Market Trend Analyzer")
st.markdown("Analyze real-time job trends powered by Adzuna API")

# Sidebar
st.sidebar.header("Search Settings")
keyword = st.sidebar.text_input("Job Keyword", value="python")
country = st.sidebar.selectbox("Country", ["in", "us", "gb"], index=0)
pages = st.sidebar.slider("Pages to fetch", 1, 5, 3)

if st.sidebar.button("Fetch Jobs"):
    with st.spinner("Fetching jobs..."):
        jobs = fetch_jobs(keyword, country, pages)
        df = process_jobs(jobs)
        skills = extract_skills(df)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jobs Found", len(df))
    col2.metric("Unique Companies", df["company"].nunique())
    col3.metric("Top Skill", skills.idxmax())

    # Skills chart
    st.subheader("Most In-Demand Skills")
    fig1 = px.bar(
        x=skills.index,
        y=skills.values,
        labels={"x": "Skill", "y": "Mentions"},
        color=skills.values,
        color_continuous_scale="blues"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Top locations
    st.subheader("Top Hiring Locations")
    top_locations = df["location"].value_counts().head(10)
    fig2 = px.bar(
        x=top_locations.values,
        y=top_locations.index,
        orientation="h",
        labels={"x": "Job Count", "y": "Location"},
        color=top_locations.values,
        color_continuous_scale="greens"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Top companies
    st.subheader("Top Hiring Companies")
    top_companies = df["company"].value_counts().head(10)
    fig3 = px.pie(
        values=top_companies.values,
        names=top_companies.index,
        title="Jobs by Company"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Raw data
    st.subheader("Raw Job Listings")
    st.dataframe(df[["title", "company", "location"]], use_container_width=True)