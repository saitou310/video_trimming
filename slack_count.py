# CREATE TABLE messages (
#     id VARCHAR(50) PRIMARY KEY,
#     user VARCHAR(50),
#     text TEXT,
#     ts TIMESTAMP
# );


import re
import requests
import mysql.connector
from collections import defaultdict

# Slack API Token and Channel ID
SLACK_TOKEN = "xoxb-xxxxxx"  # 取得したSlackアプリトークンを入力
CHANNEL_ID = "C12345678"  # 対象チャンネルIDを入力

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'slack_data'
}

# Fetch messages from Slack
def fetch_slack_messages():
    url = "https://slack.com/api/conversations.history"
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
    params = {"channel": CHANNEL_ID, "limit": 1000}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200 or not response.json().get('ok'):
        raise Exception("Failed to fetch messages: " + response.text)
    
    return response.json().get('messages', [])

# Store messages in MySQL
def store_messages_in_db(messages):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR(50) PRIMARY KEY,
                user VARCHAR(50),
                text TEXT,
                ts TIMESTAMP
            )
        """)

        # Insert messages into the table
        for message in messages:
            cursor.execute("""
                INSERT INTO messages (id, user, text, ts) 
                VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
                ON DUPLICATE KEY UPDATE text = VALUES(text)
            """, (message['client_msg_id'], message.get('user', 'bot'), message['text'], float(message['ts'])))

        connection.commit()
    except mysql.connector.Error as e:
        print("Error: ", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Count mentions in messages
def count_mentions():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Retrieve all messages
        cursor.execute("SELECT text FROM messages")
        messages = cursor.fetchall()

        mention_count = defaultdict(int)

        # Regex to find mentions in the form of <@USERID>
        mention_pattern = re.compile(r"<@(\w+)>")
        for (text,) in messages:
            mentions = mention_pattern.findall(text)
            for user_id in mentions:
                mention_count[user_id] += 1

        return mention_count
    except mysql.connector.Error as e:
        print("Error: ", e)
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Main Execution
if __name__ == "__main__":
    print("Fetching Slack messages...")
    messages = fetch_slack_messages()

    print(f"Storing {len(messages)} messages in the database...")
    store_messages_in_db(messages)

    print("Counting mentions...")
    mention_counts = count_mentions()

    print("Mention counts:")
    for user, count in mention_counts.items():
        print(f"User {user}: {count} mentions")
