# analyze_sentiment.py
from sklearn.ensemble import IsolationForest
import redis
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import numpy as np
import time

class SentimentAnalyzer:
    def __init__(self, cache, pipeline_callback):
        self.cache = cache
        self.pipeline_callback = pipeline_callback
        self.tokenizer = DistilBertTokenizer.from_pretrained("D:/Intern/Survey_sparrow/Conversniper/conversniper_bert")
        self.model = DistilBertForSequenceClassification.from_pretrained("D:/Intern/Survey_sparrow/Conversniper/conversniper_bert")
        self.seen_ids = set()

    def analyze_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        sentiment_idx = np.argmax(probs)
        sentiment_map = {0: "Neutral", 1: "Positive", 2: "Negative"}
        sentiment_label = sentiment_map[sentiment_idx]
        sentiment_score = float(probs[sentiment_idx])
        return sentiment_label, sentiment_score

    def analyze_comment_tree(self, post_data):
        comments = post_data.get("comments", [])
        comment_sentiments = {}
        
        def process_comment(comment_id, visited=None):
            if visited is None:
                visited = set()
            if comment_id in visited or comment_id not in [c["id"] for c in comments]:
                return None
            visited.add(comment_id)
            
            comment = next(c for c in comments if c["id"] == comment_id)
            text = comment["body"]
            label, score = self.analyze_text(text)
            
            child_ids = [c["id"] for c in comments if c["parent_id"] == comment_id]
            child_sentiments = [process_comment(child_id, visited) for child_id in child_ids]
            child_sentiments = [cs for cs in child_sentiments if cs is not None]
            
            if child_sentiments:
                avg_child_score = np.mean([cs["score"] for cs in child_sentiments])
                score = (score + avg_child_score) / 2
            
            return {"label": label, "score": score, "support": comment["score"]}

        for comment in comments:
            if comment["id"] not in comment_sentiments:
                comment_sentiments[comment["id"]] = process_comment(comment["id"]) or {"label": "Neutral", "score": 0.0, "support": comment["score"]}

        post_text = post_data.get("title", "") + " " + post_data.get("text", "")
        post_label, post_score = self.analyze_text(post_text)
        top_level_sentiments = [comment_sentiments[c["id"]] for c in comments if c["parent_id"] == post_data["id"]]
        if top_level_sentiments:
            avg_comment_score = np.mean([cs["score"] for cs in top_level_sentiments])
            post_score = (post_score + avg_comment_score) / 2
        
        return post_label, post_score

    def analyze(self):
        
        while True:
            posts = []
            for key in self.cache.keys("post:*") + self.cache.keys("discord:*"):
                post_data = eval(self.cache.get(key))
                post_id = post_data["id"]
                
                if post_id in self.seen_ids:
                    continue
                
                source = post_data.get("source", "Unknown")
                support = post_data.get("support", post_data.get("reactions", 0))
                text = post_data.get("title", post_data.get("content", ""))
                
                if source == "Reddit":
                    sentiment_label, sentiment_score = self.analyze_comment_tree(post_data)
                    comment_count = post_data.get("comment_count", 0)
                else:
                    sentiment_label, sentiment_score = self.analyze_text(text)
                    comment_count = 0
                
                post_data["sentiment_label"] = sentiment_label
                post_data["sentiment_score"] = sentiment_score
                
                result = {
                    "source": source,
                    "content": text,
                    "sentiment": sentiment_label,  # Pass label, not score
                    "support": support,
                    "comment_count": comment_count
                }
                
                self.pipeline_callback(result)
                self.seen_ids.add(post_id)
                posts.append(post_data)
            
            if len(posts) >= 10:
                X = np.array([[p.get("support", p.get("reactions", 0)) + p.get("comment_count", 0), p["sentiment_score"]] for p in posts])
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                predictions = iso_forest.fit_predict(X)
                
                for i, post in enumerate(posts):
                    if predictions[i] == -1:
                        text = post.get("title", post.get("content", ""))
                        support = post.get("support", post.get("reactions", 0))
                        source = post["source"]
                        sentiment_score = float(post["sentiment_score"])
                        sentiment_label = post["sentiment_label"]  # Use label here
                        comment_count = post.get("comment_count", 0)
                        trend_result = {
                            "source": source,
                            "content": text,
                            "sentiment": sentiment_label,  # Pass label, not score
                            "support": support,
                            "comment_count": comment_count,
                            "is_trending": True
                        }
                        print(f"Trending {source}: {text.encode('utf-8', 'replace').decode('utf-8')} {{Sentiment: {sentiment_label}, {source == 'Discord' and 'Reactions' or 'Support'}: {support}, Comments: {comment_count}}}")
                        self.pipeline_callback(trend_result)
            
            time.sleep(60)