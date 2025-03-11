# redit.py
import logging
logging.getLogger("prawcore").setLevel(logging.ERROR)
import praw
import redis
from datetime import datetime, timedelta

class RedditSniper:
    def __init__(self, cache):
        self.reddit = praw.Reddit(
            client_id="bCj1W7unX_65fp7dNOyyiw",
            client_secret="QCzd3x4hhoZjJw337IrK_bxDgEjLDA",
            user_agent="Conversniper:v1.0 (by /u/Disastrous_Test8814)"
        )
        self.cache = cache
        self.time_cutoff = datetime.utcnow() - timedelta(hours=24)
        self.subreddit = self.reddit.subreddit("python+datascience")

    def run(self):
        print("Starting Reddit stream...")
        for submission in self.subreddit.stream.submissions():
            post_time = datetime.fromtimestamp(submission.created_utc)
            if post_time < self.time_cutoff:
                continue
            
            
            submission.comments.replace_more(limit=0)  # Expand all comments
            comments = []
            for comment in submission.comments.list():
                comments.append({
                    "id": comment.id,
                    "body": comment.body,
                    "score": comment.score,  # Comment upvotes/downvotes
                    "parent_id": comment.parent_id.split('_')[1] if comment.parent_id.startswith('t1_') else submission.id,
                    "timestamp": comment.created_utc
                })
            
            post_data = {
                "id": submission.id,
                "title": submission.title,
                "text": submission.selftext,
                "support": submission.score,  # Upvotes/downvotes
                "comment_count": submission.num_comments,  # Reaction signal
                "source": "Reddit",
                "timestamp": submission.created_utc,
                "comments": comments  # Full comment tree
            }
            
            self.cache.set(f"post:{post_data['id']}", str(post_data))
            