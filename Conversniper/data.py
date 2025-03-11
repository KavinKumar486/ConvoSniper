# Run this in Python to generate and save
import pandas as pd
import random

posts = [
    "Python’s killing it today 🔥", "This code’s a mess—ugh", "Datascience thread’s meh",
    "Discord’s hype—love this!", "Reddit’s algo’s trash—wtf", "New ML trick—cool stuff",
    "BERT’s back 🔥—so excited!", "Why’s this bug here—annoying", "Chatting AI—whatever",
    "Python script dropped—lit!", "Discord lag—sucks bad", "Reddit post—interesting",
] * 9  # Repeat to bulk up
sentiments = ["Positive", "Negative", "Neutral"] * 33  # Balance it
random.shuffle(posts)
random.shuffle(sentiments)

data = [{"text": post, "sentiment": sentiment} for post, sentiment in zip(posts[:100], sentiments[:100])]
df = pd.DataFrame(data)
df.to_csv("D:/Intern/Survey_sparrow/Conversniper/social_synthetic_data.csv", index=False)
print("Dataset saved as social_synthetic_data.csv!")