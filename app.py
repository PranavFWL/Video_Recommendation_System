import pickle
import numpy as np
import pandas as pd
import sqlite3
from sqlite3 import Error
import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from transformers import pipeline  


df_existing = pd.read_csv("Final_DataSet.csv")  # For existing users dataset
df_cold = pd.read_csv("video_dataset_2.csv")  # For new users dataset


with open("ncf_model.pkl", "rb") as f:
    model = pickle.load(f)


sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    
    result = sentiment_pipeline(text)[0]
    label = result.get('label', 'NEUTRAL')
    sentiment_scores = {'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0}
    return sentiment_scores.get(label.upper(), 0)

# Ensure relevant columns exist in df_cold
df_cold["title"] = df_cold["title"].fillna("")
df_cold["post_summary"] = df_cold["post_summary"].fillna("")
df_cold["tags"] = df_cold["tags"].fillna("")

# **Recalculate mood_label since it's missing**
df_cold["combined_text"] = df_cold["title"] + " " + df_cold["post_summary"] + " " + df_cold["tags"]
df_cold["mood_label"] = df_cold["combined_text"].apply(analyze_sentiment)

# Initialize FastAPI
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


def create_connection():
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        # Create the database file if it doesn't exist
        conn = sqlite3.connect('video_recommendations.db')
        return conn
    except Error as e:
        print(e)
    
    return conn

def create_tables(conn):  #Create the necessary tables if they don't exist
   
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create video preferences table with foreign key to users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            video_title TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
    except Error as e:
        print(e)

def store_new_user(name):

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def store_video_preference(user_id, video_id, video_title):
    """Store a user's video preference"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO video_preferences (user_id, video_id, video_title) VALUES (?, ?, ?)",
        (user_id, video_id, video_title)
    )
    conn.commit()
    conn.close()

def get_user_preferences(user_id):
 
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT video_id, video_title FROM video_preferences WHERE user_id = ?",
        (user_id,)
    )
    preferences = cursor.fetchall()
    conn.close()
    return preferences

def init_db():
   
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

# Initialize database at app startup
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
def home():
    return FileResponse("index.html")  # Serves the UI

@app.get("/recommend/{user_id}")
def recommend_videos(user_id: int, top_n: int = 5):
    """
    Recommend top N videos for an existing user.
    """
    max_user_id = 26  # Adjust this based on the trained model
    if user_id >= max_user_id:
        return {"error": f"User ID out of range. Please use a User ID between 0 and {max_user_id - 1}."}

    all_videos = np.array(df_existing["video_id"].unique())  # Get all video IDs

    # Predict engagement scores for all videos for this user
    user_array = np.array([user_id] * len(all_videos))
    predictions = model.predict([user_array, all_videos])

    # Sort and return top N recommendations
    recommendations = sorted(
        zip(all_videos, predictions.flatten()), key=lambda x: x[1], reverse=True
    )[:top_n]

    # Prepare response ensuring video metadata exists in df_cold
    video_recommendations = []
    for vid, _ in recommendations:
        video_info = df_cold[df_cold["id"] == vid]
        if not video_info.empty:
            video_recommendations.append({
                "video_id": int(vid),  # Convert NumPy int to Python int
                "title": video_info["title"].values[0] if "title" in video_info.columns else "",
                "post_summary": video_info["post_summary"].values[0],
                "video_link": video_info["video_link"].values[0]
            })

    return {"user_id": int(user_id), "recommended_videos": video_recommendations}

@app.get("/recommend_by_mood/{mood_label}")
def recommend_by_mood(mood_label: int, top_n: int = 5, user_name: Optional[str] = None):
  
    mood_videos = df_cold[df_cold["mood_label"] == mood_label]

    if mood_videos.empty:
        return {"message": "No videos found for this mood"}

    # Sort by engagement score (or views)
    mood_videos = mood_videos.sort_values(by="view_count", ascending=False)

    # Get top N videos
    top_videos = mood_videos.head(top_n)
    
    # Make sure 'title' column exists for video_title storage
    if "title" not in top_videos.columns:
        # Use post_summary as title if title doesn't exist
        top_videos["title"] = top_videos["post_summary"].str[:50]  # Truncate to 50 chars
    
    recommendations = top_videos[["id", "title", "post_summary", "video_link"]].to_dict(orient="records")
    
    # Store user preferences if a name was provided
    if user_name:
        user_id = store_new_user(user_name)
        # Store each recommended video as a preference
        for video in recommendations:
            store_video_preference(user_id, video["id"], video["title"])
    
    return {
        "mood_label": int(mood_label), 
        "recommended_videos": recommendations,
        "user_saved": bool(user_name)
    }

# Add a new route to get user video history
@app.get("/user_history/{user_name}")
def get_user_history(user_name: str):
    """
    Get a user's video preference history by their name
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # Get user ID by name
    cursor.execute("SELECT id FROM users WHERE name = ?", (user_name,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {"message": "User not found"}
    
    user_id = user[0]
    
    # Get user's video preferences
    cursor.execute(
        "SELECT video_id, video_title, timestamp FROM video_preferences WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,)
    )
    preferences = cursor.fetchall()
    
    conn.close()
    
    # Format the preferences
    formatted_preferences = [
        {"video_id": pref[0], "video_title": pref[1], "timestamp": pref[2]} 
        for pref in preferences
    ]
    
    return {"user_name": user_name, "preferences": formatted_preferences}

# Add a debug endpoint to view all data
@app.get("/debug/database")
def debug_database():
    
    conn = create_connection()
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT * FROM users")
    users = [{"id": user[0], "name": user[1], "created_at": user[2]} for user in cursor.fetchall()]
    
    # Get all preferences
    cursor.execute("SELECT * FROM video_preferences")
    preferences = [
        {"id": pref[0], "user_id": pref[1], "video_id": pref[2], "video_title": pref[3], "timestamp": pref[4]} 
        for pref in cursor.fetchall()
    ]
    
    conn.close()
    
    return {"users": users, "preferences": preferences}

# Run FastAPI Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)