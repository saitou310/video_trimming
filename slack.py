import requests
from datetime import datetime, timedelta

token = "xoxb-YourToken"
channel_id = "CHANNEL_ID"
oldest = (datetime.now() - timedelta(days=30)).timestamp()
latest = datetime.now().timestamp()

url = "https://slack.com/api/conversations.history"
headers = {"Authorization": f"Bearer {token}"}
params = {"channel": channel_id, "oldest": oldest, "latest": latest, "limit": 1000}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data["ok"]:
    for message in data["messages"]:
        print(message["ts"], message["text"])
else:
    print("Error:", data["error"])
