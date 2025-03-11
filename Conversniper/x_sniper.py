
import requests
import time

# Your API credentials
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAIUJzgEAAAAARdV42Fzm02ZOPEVcPJUW7eoq%2F3s%3DYA5fhW4ECeDMBlmXN00z3hWfBCMTbzAi54AHB89QrzCxrFh4qV'

# Function to extract data based on a specific topic
def extract_data(topic, max_results=10):
    search_url = 'https://api.twitter.com/2/tweets/search/recent'
    headers = {
        'Authorization': f'Bearer {bearer_token}',
    }

    params = {
        'query': topic,
        'tweet.fields': 'created_at,author_id,text',
        'expansions': 'author_id',
        'user.fields': 'username',
        'max_results': max_results
    }

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    elif response.status_code == 429:
        # Rate limit exceeded
        reset_time = int(response.headers.get('x-rate-limit-reset', 0))
        current_time = int(time.time())
        sleep_time = reset_time - current_time + 5  # Add a 5-second buffer
        if sleep_time > 0:
            print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            # Retry after sleeping
            return extract_data(topic, max_results)
        else:
            print("Rate limit exceeded. Retrying now...")
            return extract_data(topic, max_results)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Extract data for a specific topic
topic = 'python lang:en -is:retweet'  # Modify your query as needed
data = extract_data(topic, max_results=10)

if data and 'data' in data:
    # Map user IDs to usernames
    users = {user['id']: user['username'] for user in data.get('includes', {}).get('users', [])}

    # Display tweets
    for tweet in data['data']:
        username = users.get(tweet['author_id'], 'Unknown')
        timestamp = tweet['created_at']
        text = tweet['text']
        print(f"[{timestamp}] @{username}: {text}\n")
else:
    print(f"Failed to extract data for topic '{topic}'.")
