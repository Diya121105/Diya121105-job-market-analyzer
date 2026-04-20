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

def clean_data(df):
    # Remove duplicate jobs
    df = df.drop_duplicates(subset=["title", "company"])
    
    # Clean job titles - remove extra spaces and special characters
    df["title"] = df["title"].str.strip()
    df["title"] = df["title"].str.replace(r'[^\w\s]', '', regex=True)
    
    # Categorize seniority level from title
    def get_seniority(title):
        title = title.lower()
        if any(word in title for word in ["senior", "sr", "lead", "principal"]):
            return "Senior"
        elif any(word in title for word in ["junior", "jr", "associate", "intern"]):
            return "Junior"
        else:
            return "Mid Level"
    
    df["seniority"] = df["title"].apply(get_seniority)
    
    # Clean location - keep only city/state
    df["location"] = df["location"].str.strip()
    
    # Replace empty strings with N/A
    df = df.replace("", "N/A")
    
    return df

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
        try:
            jobs = fetch_jobs(keyword, country, pages)
            if not jobs:
                st.error("No jobs found. Try a different keyword or country.")
                st.stop()
            df = process_jobs(jobs)
            df = clean_data(df)
            skills = extract_skills(df)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

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

    # Seniority breakdown
    st.subheader("Seniority Level Breakdown")
    seniority_counts = df["seniority"].value_counts()
    fig4 = px.pie(
        values=seniority_counts.values,
        names=seniority_counts.index,
        title="Jobs by Seniority Level",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Raw data
    st.subheader("Raw Job Listings")
    st.dataframe(df[["title", "company", "location", "seniority"]], use_container_width=True)

    # CSV Export
    st.subheader("Download Results")
    csv = df[["title", "company", "location", "seniority"]].to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="job_results.csv",
        mime="text/csv"
    )