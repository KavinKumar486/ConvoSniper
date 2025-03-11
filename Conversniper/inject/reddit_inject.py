import logging
logging.getLogger("prawcore").setLevel(logging.ERROR)  # Suppress PRAW warnings
import praw

class RedditInjector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id="bCj1W7unX_65fp7dNOyyiw",
            client_secret="QCzd3x4hhoZjJw337IrK_bxDgEjLDA",
            user_agent="Conversniper:v1.0 (by /u/Disastrous_Test8814)",
            username="Disastrous_Test8814",
            password="k4a5v2i6n4"
        )

    def post(self, response, subreddit="convosniper_test"):
        """Create a new Reddit post with the response as the body."""
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            title = "Automated Response"  # Fixed title; customize as needed
            submission = subreddit_obj.submit(title, selftext=response)
            print(f"Created new Reddit post with title: {title} and response: {response[:50]}...")
            return submission.id
        except Exception as e:
            print(f"Reddit posting error: {e}")
            return None

if __name__ == "__main__":
    injector = RedditInjector()
    response = "Hey crew, AI’s lit! Let’s vibe on this with DataScienceCo!"
    injector.post(response)