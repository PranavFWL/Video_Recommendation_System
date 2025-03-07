import pandas as pd
import numpy as np
from transformers import pipeline
from fastapi import FastAPI
import uvicorn

# Load sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    """Analyze sentiment using Hugging Face transformers."""
    result = sentiment_pipeline(text)[0]
    sentiment_scores = {'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0}
    return sentiment_scores.get(result.get('label', 'NEUTRAL').upper(), 0)

# Load dataset
file_path = "video_dataset_2.csv"
df = pd.read_csv(file_path)

# Ensure required columns exist
df["title"] = df["title"].fillna("")
df["post_summary"] = df["post_summary"].fillna("")
df["tags"] = df["tags"].fillna("")

# If 'view_count' is missing, create a dummy column
if "view_count" not in df.columns:
    df["view_count"] = np.random.randint(100, 1000, size=len(df))  # Fake views

# Combine text and apply sentiment analysis
df["combined_text"] = df["title"] + " " + df["post_summary"] + " " + df["tags"]
df["mood_label"] = df["combined_text"].apply(analyze_sentiment)

# Initialize FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Video Recommendation API!"}

@app.get("/recommend_by_mood/{mood_label}")
def recommend_by_mood(mood_label: int, top_n: int = 5):
    """Recommend top N videos based on mood."""
    mood_videos = df[df["mood_label"] == mood_label]
    if mood_videos.empty:
        return {"message": "No videos found for this mood"}
    
    # Sort by view_count if available
    mood_videos = mood_videos.sort_values(by="view_count", ascending=False)
    
    recommendations = mood_videos.head(top_n)[["id", "title", "mood_label"]].to_dict(orient="records")
    return {"mood_label": mood_label, "recommended_videos": recommendations}

# Run FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
