import pymongo
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import os

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["conversniper"]
social_collection = db["social_data"]

def generate_visualizations():
    # Query data for engagement metrics (likes/support and comments)
    engagements = list(social_collection.find({
        "$or": [
            {"support": {"$exists": True, "$ne": None}},
            {"comment_count": {"$exists": True, "$ne": None}}
        ]
    }))

    # Prepare data for visualization
    data = []
    for engagement in engagements:
        data.append({
            "platform": engagement.get("source", "Unknown"),
            "likes": engagement.get("support", 0),
            "comments": engagement.get("comment_count", 0),
            "timestamp": engagement.get("stored_at", datetime.now())
        })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['likes'] = pd.to_numeric(df['likes'], errors='coerce').fillna(0)
    df['comments'] = pd.to_numeric(df['comments'], errors='coerce').fillna(0)

    # Save visualizations as static files
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="platform", y="likes", color='blue', label='Likes')
    sns.barplot(data=df, x="platform", y="comments", color='orange', label='Comments')
    plt.title("Social Media Engagement Metrics by Platform")
    plt.xlabel("Platform")
    plt.ylabel("Count")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/engagement_metrics_by_platform.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="likes", y="comments", hue="platform", style="platform", s=100)
    plt.title("Likes vs. Comments Across Platforms")
    plt.xlabel("Likes")
    plt.ylabel("Comments")
    plt.legend(title="Platform")
    plt.tight_layout()
    plt.savefig("static/likes_vs_comments.png")
    plt.close()

    if not df['timestamp'].isnull().all():
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x="timestamp", y="likes", hue="platform", label='Likes')
        sns.lineplot(data=df, x="timestamp", y="comments", hue="platform", label='Comments', linestyle='--')
        plt.title("Engagement Over Time by Platform")
        plt.xlabel("Timestamp")
        plt.ylabel("Count")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("static/engagement_over_time.png")
        plt.close()
    else:
        print("No timestamp data available for time-based visualization.")

if __name__ == '__main__':
    generate_visualizations()