import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

API_BASE = "http://127.0.0.1:8000"

@st.cache_data(ttl=3600)
def fetch_jobs(keyword="python", country="in", pages=3):
    response = requests.get(f"{API_BASE}/jobs", params={
        "keyword": keyword,
        "country": country,
        "pages": pages
    })
    data = response.json()
    return pd.DataFrame(data["jobs"])

@st.cache_data(ttl=3600)
def fetch_skills(keyword="python", country="in"):
    response = requests.get(f"{API_BASE}/skills", params={
        "keyword": keyword,
        "country": country
    })
    data = response.json()
    return pd.Series(data["skills"]).sort_values(ascending=False)

@st.cache_data(ttl=3600)
def fetch_locations(keyword="python", country="in"):
    response = requests.get(f"{API_BASE}/locations", params={
        "keyword": keyword,
        "country": country
    })
    data = response.json()
    return pd.Series(data["locations"]).sort_values(ascending=False)

from sklearn.linear_model import LinearRegression
import numpy as np

def predict_skill_demand(skills):
    # Use skill frequency to predict a demand score
    skill_names = skills.index.tolist()
    skill_values = skills.values.reshape(-1, 1)
    
    # Simple demand score = current count + predicted growth
    indices = np.arange(len(skill_names)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(indices, skill_values)
    predicted = model.predict(indices)
    
    demand_df = pd.DataFrame({
        "skill": skill_names,
        "current_mentions": skills.values,
        "demand_score": predicted.flatten().round(2)
    }).sort_values("demand_score", ascending=False)
    
    return demand_df

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
            df = fetch_jobs(keyword, country, pages)
            skills = fetch_skills(keyword, country)
            locations = fetch_locations(keyword, country)
            
            if df.empty:
                st.error("No jobs found. Try a different keyword or country.")
                st.stop()
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

    # ML Prediction
    st.subheader("🤖 ML-Based Skill Demand Prediction")
    demand_df = predict_skill_demand(skills)
    fig5 = px.bar(
        demand_df,
        x="skill",
        y="demand_score",
        color="demand_score",
        color_continuous_scale="reds",
        labels={"demand_score": "Predicted Demand Score"}
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Top locations
    st.subheader("Top Hiring Locations")
    top_locations = locations.head(10)
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

    # CSV Export
    st.subheader("Download Results")
    csv = df[["title", "company", "location"]].to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="job_results.csv",
        mime="text/csv"
    )