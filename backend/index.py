from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import requests
from phi.agent import Agent
from phi.model.xai import xAI
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware
import os

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
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GitHub API Base URL
GITHUB_API_URL = "https://api.github.com"
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")

# Common headers for GitHub API requests
HEADERS = {
    "Authorization": f"token {GITHUB_API_KEY}"
}

# Fetch GitHub user data
def fetch_github_user(username):
    url = f"{GITHUB_API_URL}/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    # Improved error handling
    error_detail = response.json().get("message", "Unknown error occurred.")
    raise HTTPException(status_code=response.status_code, detail=f"GitHub user {username} not found. Error: {error_detail}")

# Fetch top 20 latest repositories for a GitHub user
def fetch_latest_repos(username):
    url = f"{GITHUB_API_URL}/users/{username}/repos"
    response = requests.get(url, params={"per_page": 20, "sort": "updated"}, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch repositories for {username}")

# Fetch followers and following data
def fetch_followers(username):
    url = f"{GITHUB_API_URL}/users/{username}/followers"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return [user["login"] for user in response.json()]
    return []

def fetch_following(username):
    url = f"{GITHUB_API_URL}/users/{username}/following"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return [user["login"] for user in response.json()]
    return []

# Calculate compatibility metrics
def calculate_compatibility(user1_data, user2_data):
    # Fetch repositories and data
    user1_repos = fetch_latest_repos(user1_data["login"])
    user2_repos = fetch_latest_repos(user2_data["login"])
    
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
def analyze_compatibility(username1: str, username2: str):
    user1 = fetch_github_user(username1)
    user2 = fetch_github_user(username2)

    # Calculate compatibility metrics
    compatibility_metrics = calculate_compatibility(user1, user2)

    # Prepare insights for the agent
    compatibility_metrics_summary = {
        "shared_languages": compatibility_metrics["shared_languages"][:10],
        "shared_repos": compatibility_metrics["shared_repos"][:5],
        "common_followers": compatibility_metrics["shared_followers"],
        "valuable_insights": {
            "activity_trends": f"{username1} has {user1['public_repos']} public repos, while {username2} has {user2['public_repos']}.",
            "repository_impact": f"{username1}'s repos average {compatibility_metrics['community_impact_score']} stars, while {username2}'s are gaining momentum.",
            "follower_engagement": f"Shared followers include {', '.join(compatibility_metrics['shared_followers'][:3])}."
        }
    }

    message = [
        {"role": "user", "content": f"Analyze the collaboration potential between GitHub users {username1} and {username2}."},
        {"role": "system", "content": json.dumps(compatibility_metrics_summary)}  # Ensure content is a JSON string
    ]

    # Get insights from the agent
    try:
        agent_response = compatibility_agent.run(json.dumps(message))
        # Check if the response is empty
        if not agent_response.content:
            raise ValueError("Received empty response from the agent.")
        clean_response = (
            agent_response.content
            .replace('```json', '')
            .replace('```', '')
            .strip()
        )
        insights = json.loads(clean_response)
        # insights = json.loads(agent_response.content) if isinstance(agent_response.content, str) else agent_response.content
    except Exception as e:
        # Log the error and the response content for debugging
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}. Response content: {getattr(agent_response, 'content', 'No content')}")
    
    # Return insights from the agent
    return {
        "match_type": insights.get("match_type", "No match type provided."),
        "compatibility_summary": insights.get("compatibility_summary", "Unable to generate summary."),
        "strengths_and_opportunities": insights.get("strengths_and_opportunities", "No detailed insights available."),
        "collaboration_plan": insights.get("collaboration_plan", "No collaboration suggestions provided."),
        "motivational_message": insights.get("motivational_message", "Keep building and collaborating!"),
        "valuable_insights": insights.get("valuable_insights", {
            "activity_trends": "No activity data available.",
            "repository_impact": "No repository impact data available.",
            "follower_engagement": "No follower data available."
        })
    }

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "GitHub Compatibility Tool is live!"}

@app.get("/auth/github")
async def github_auth():
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GitHub Client ID not configured"
        )
    
    auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        "&scope=read:user,repo"
        f"&redirect_uri={FRONTEND_URL}/auth/callback"
    )
    
    return RedirectResponse(url=auth_url, status_code=302)

@app.post("/auth/github/callback")
async def github_callback(code: str):
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
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")
    
    return {"access_token": access_token}
