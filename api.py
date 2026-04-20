from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
import requests
import pandas as pd
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_ID = "6a00f514"
API_KEY = "e1c19bb14cb5218c8f7ac33e0e88892c"

# Simple in-memory cache
cache = {}

def fetch_jobs(keyword="python", country="in", pages=3):
    cache_key = f"{keyword}_{country}_{pages}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    all_jobs = []
    
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {
            "app_id": APP_ID,
            "app_key": API_KEY,
            "what": keyword,
            "results_per_page": 50
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            all_jobs.extend(data.get("results", []))
        except:
            continue
    
    cache[cache_key] = all_jobs
    return all_jobs

@app.get("/jobs")
def get_jobs(keyword: str = "python", country: str = "in", pages: int = 3):
    jobs = fetch_jobs(keyword, country, pages)
    processed = []
    for job in jobs:
        processed.append({
            "title": job.get("title", "N/A"),
            "company": job.get("company", {}).get("display_name", "N/A"),
            "location": job.get("location", {}).get("display_name", "N/A"),
            "description": job.get("description", "")
        })
    return {"total": len(processed), "jobs": processed}

@app.get("/skills")
def get_skills(keyword: str = "python", country: str = "in"):
    jobs = fetch_jobs(keyword, country)
    df = pd.DataFrame([{
        "description": job.get("description", "")
    } for job in jobs])
    
    skills_list = [
        "python", "sql", "machine learning", "django", "flask",
        "pandas", "numpy", "tensorflow", "aws", "docker",
        "javascript", "react", "git", "excel", "power bi"
    ]
    
    skill_counts = {}
    for skill in skills_list:
        count = df["description"].str.lower().str.contains(skill).sum()
        skill_counts[skill] = int(count)
    
    return {"skills": skill_counts}

@app.get("/locations")
def get_locations(keyword: str = "python", country: str = "in"):
    jobs = fetch_jobs(keyword, country)
    locations = {}
    for job in jobs:
        loc = job.get("location", {}).get("display_name", "N/A")
        locations[loc] = locations.get(loc, 0) + 1
    return {"locations": locations}