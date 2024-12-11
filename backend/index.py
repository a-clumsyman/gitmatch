from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import requests
from phi.agent import Agent
from phi.model.xai import xAI
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware
import os
from config.mongodb import get_mongodb_client
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get environment variables with fallback values
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
if not GITHUB_CLIENT_ID:
    raise ValueError("GITHUB_CLIENT_ID must be set")

GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
if not GITHUB_CLIENT_SECRET:
    raise ValueError("GITHUB_CLIENT_SECRET must be set")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://gitmatch-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GitHub API Base URL
GITHUB_API_URL = "https://api.github.com"

# Initialize MongoDB
mongo_client, database_name = get_mongodb_client()
db = mongo_client[database_name]
users_collection = db.users
compatibility_cache = db.compatibility_cache

# Fetch GitHub user data
def fetch_github_user(username, access_token):
    try:
        url = f"{GITHUB_API_URL}/users/{username}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid GitHub token")
        elif response.status_code == 403:
            raise HTTPException(status_code=403, detail="GitHub API rate limit exceeded")
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"GitHub user {username} not found")
        elif response.status_code != 200:
            error_detail = response.json().get("message", "Unknown error occurred")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitHub API error: {error_detail}"
            )
        
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch GitHub user data: {str(e)}"
        )

# Fetch top 20 latest repositories for a GitHub user
def fetch_latest_repos(username, access_token):
    url = f"{GITHUB_API_URL}/users/{username}/repos"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, params={"per_page": 20, "sort": "updated"}, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch repositories for {username}")

# Fetch followers data
def fetch_followers(username, access_token):
    url = f"{GITHUB_API_URL}/users/{username}/followers"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [user["login"] for user in response.json()]
    return []

def fetch_following(username, access_token):
    url = f"{GITHUB_API_URL}/users/{username}/following"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [user["login"] for user in response.json()]
    return []

# Calculate compatibility metrics
def calculate_compatibility(user1_data, user2_data, access_token):
    # Fetch repositories and data with OAuth token
    user1_repos = fetch_latest_repos(user1_data["login"], access_token)
    user2_repos = fetch_latest_repos(user2_data["login"], access_token)
    
    user1_languages = {repo.get("language") for repo in user1_repos if repo.get("language")}
    user2_languages = {repo.get("language") for repo in user2_repos if repo.get("language")}
    shared_languages = user1_languages & user2_languages
    complementarity_languages = user1_languages ^ user2_languages

    # Technical Alignment
    technical_alignment = len(shared_languages) / max(len(user1_languages | user2_languages), 1) * 10
    skill_complementarity = len(complementarity_languages) / max(len(user1_languages | user2_languages), 1) * 10

    # Collaborative Potential
    activity_match = min(user1_data["public_repos"], user2_data["public_repos"]) / max(
        user1_data["public_repos"], user2_data["public_repos"], 1
    ) * 10

    # Network Synergy
    user1_followers = set(fetch_followers(user1_data["login"]))
    user2_followers = set(fetch_followers(user2_data["login"]))
    common_followers = len(user1_followers & user2_followers) / max(len(user1_followers | user2_followers), 1) * 10

    # Cultural Synergy
    shared_topics = sum(
        1 for repo1 in user1_repos for repo2 in user2_repos if repo1.get("topics") and set(repo1["topics"]) & set(repo2.get("topics", []))
    )
    cultural_alignment = shared_topics / max(len(user1_repos), len(user2_repos), 1) * 10

    # Community Impact
    user1_avg_stars = sum(repo["stargazers_count"] for repo in user1_repos) / max(len(user1_repos), 1)
    user2_avg_stars = sum(repo["stargazers_count"] for repo in user2_repos) / max(len(user2_repos), 1)
    popularity_match = min(user1_avg_stars, user2_avg_stars) / max(user1_avg_stars, user2_avg_stars, 1) * 10

    # Weighting system
    weights = {
        "technical_alignment": 0.2,
        "skill_complementarity": 0.1,
        "activity_match": 0.1,
        "common_followers": 0.1,
        "cultural_alignment": 0.2,
        "popularity_match": 0.1,
    }

    compatibility_score = (
        weights["technical_alignment"] * (technical_alignment ** 1.2) +  #  scaling for strong alignment
        weights["skill_complementarity"] * (skill_complementarity ** 1.1) +  # Slight boost for complementarity
        weights["activity_match"] * activity_match +  # Keep linear for activity match
        weights["common_followers"] * common_followers +  # Keep linear for network overlap
        weights["cultural_alignment"] * (cultural_alignment ** 1.3) +  # Higher emphasis on cultural alignment
        weights["popularity_match"] * (popularity_match ** 1.1)  # Slight boost for popularity match
    )

    # Add a bonus for strong technical alignment
    if len(shared_languages) > 5:
        compatibility_score += 2

    # Penalize if activity levels are too low
    if activity_match < 3:
        compatibility_score -= 2

    # Ensure the score stays within 0–100
    compatibility_score = max(0, min(compatibility_score, 100))

    return {
        "compatibility_score": round(compatibility_score, 2),
        "technical_alignment_score": round(technical_alignment, 2),
        "skill_complementarity_score": round(skill_complementarity, 2),
        "activity_match_score": round(activity_match, 2),
        "network_synergy_score": round(common_followers, 2),
        "cultural_alignment_score": round(cultural_alignment, 2),
        "community_impact_score": round(popularity_match, 2),
        "shared_languages": list(shared_languages),
        "shared_repos": [],  # Fill this with relevant repository overlap
        "shared_followers": list(user1_followers & user2_followers),
    }

# Compatibility analysis agent
compatibility_agent = Agent(
    model=xAI(id="grok-beta"),
    show_tool_calls=True,
    structured_output=True,
    instructions=["""
    You are a collaboration strategist with a creative flair for connecting GitHub users. Your goal is to analyze the compatibility metrics of two users and provide an insightful, holistic, and motivating report.

    **Guidelines**:
    - **Define a Match Type**:
      Dynamically generate a fun and creative match-type phrase based on the metrics (e.g., "A match made in code heaven!" or "Synergy waiting to happen!").
    - **Evaluate Overall Compatibility**:
      Summarize their collaboration potential in one holistic statement based on the metrics provided.
    - **Identify Strengths and Opportunities**:
      Highlight shared programming languages or repositories and complementary skills or expertise.
    - **Propose a Collaboration Plan**:
      Suggest specific projects, tools, or domains where their strengths could be leveraged effectively.
    - **Engage with a Motivational Tone**:
      Craft an optimistic and encouraging message to inspire collaboration.
    - **Provide Valuable Insights**:
      Include additional data-driven insights:
        - **Activity Trends**: Insights into activity levels or engagement.
        - **Repository Impact**: Highlights of popular repositories.
        - **Follower Engagement**: Analysis of shared or complementary followers.

    **Response format**:
    {
        "match_type": "A creative phrase describing the match type, based on the metrics.",
        "compatibility_summary": "A single statement summarizing their compatibility holistically.",
        "strengths_and_opportunities": "A detailed analysis of shared strengths and complementary skills.",
        "collaboration_plan": "Specific, actionable suggestions for how they can work together effectively.",
        "motivational_message": "An inspiring, witty, or lighthearted message to encourage collaboration.",
        "valuable_insights": {
            "activity_trends": "Specific insights into activity levels or engagement.",
            "repository_impact": "Highlights of popular repositories, such as stars, forks, or contributions.",
            "follower_engagement": "Analysis of shared or complementary followers to showcase network overlap."
        }
    }

    **Notes**:
    - Strictly adhere to the response format defined above.
    - Populate every field. Use placeholders (e.g., "No data available") for missing values.
    - Use concise, engaging language that resonates with GitHub users while maintaining professionalism.
"""]


)

# FastAPI route to analyze compatibility between two GitHub usernames
@app.get("/analyze-compatibility")
async def analyze_compatibility(username1: str, username2: str, request: Request):
    # Validate authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
    
    access_token = auth_header.split(" ")[1]
    
    try:
        # Validate the access token by making a test request
        test_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if test_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid GitHub token")
        
        # Check cache first
        cache_key = f"{username1}:{username2}"
        cached_result = compatibility_cache.find_one({
            "users": cache_key,
            "timestamp": {"$gt": datetime.utcnow() - timedelta(hours=24)}
        })
        
        if cached_result:
            return cached_result["results"]
        
        # Get metrics
        user1 = fetch_github_user(username1, access_token)
        user2 = fetch_github_user(username2, access_token)
        
        # Calculate compatibility
        compatibility_metrics = calculate_compatibility(user1, user2, access_token)
        
        # Generate insights using the agent
        insights = compatibility_agent.run(compatibility_metrics)
        
        # Combine metrics with insights
        final_results = {
            **compatibility_metrics,
            "match_type": insights.get("match_type", "Match type unavailable"),
            "compatibility_summary": insights.get("compatibility_summary", "Summary unavailable"),
            "strengths_and_opportunities": insights.get("strengths_and_opportunities", "Analysis unavailable"),
            "collaboration_plan": insights.get("collaboration_plan", "Plan unavailable"),
            "motivational_message": insights.get("motivational_message", "Message unavailable"),
            "valuable_insights": insights.get("valuable_insights", {
                "activity_trends": "Trends unavailable",
                "repository_impact": "Impact unavailable",
                "follower_engagement": "Engagement unavailable"
            })
        }
        
        # Cache results
        compatibility_cache.update_one(
            {"users": cache_key},
            {"$set": {
                "results": final_results,
                "timestamp": datetime.utcnow().isoformat()
            }},
            upsert=True
        )
        
        return final_results
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_compatibility: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze compatibility: {str(e)}"
        )

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "GitHub Compatibility Tool is live!"}

@app.get("/auth/github")
async def github_auth():
    try:
        if not GITHUB_CLIENT_ID:
            print("Error: GITHUB_CLIENT_ID is not set")
            raise HTTPException(
                status_code=500,
                detail="GitHub Client ID not configured"
            )
        
        auth_url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={GITHUB_CLIENT_ID}"
            "&scope=read:user,repo"
            f"&redirect_uri={FRONTEND_URL}/auth/callback"
            f"&state={os.urandom(16).hex()}"
        )
        
        print(f"Generated auth URL: {auth_url}")
        return RedirectResponse(url=auth_url, status_code=302)
    except Exception as e:
        print(f"Error in github_auth: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/auth/github/callback")
async def github_callback(request: Request):
    try:
        data = await request.json()
        code = data.get("code")
        
        if not code:
            raise HTTPException(status_code=400, detail="No code provided")
        
        # Exchange code for access token
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": f"{FRONTEND_URL}/auth/callback"
            }
        )
        
        if token_response.status_code != 200:
            print(f"Token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Fetch user data from GitHub
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            print(f"User data fetch failed: {user_response.text}")
            raise HTTPException(status_code=400, detail="Failed to fetch user data")
        
        user_data = user_response.json()
        
        # Store in MongoDB
        users_collection.update_one(
            {"github_id": str(user_data["id"])},
            {
                "$set": {
                    "username": user_data["login"],
                    "access_token": access_token,
                    "avatar_url": user_data.get("avatar_url"),
                    "last_updated": datetime.utcnow().isoformat()
                }
            },
            upsert=True
        )
        
        return {"access_token": access_token}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Callback error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
