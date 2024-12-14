import re
import requests
import mysql.connector
from collections import defaultdict

# Slack API Token and Channel ID
SLACK_TOKEN = "xoxb-xxxxxx"  # Slackトークン
CHANNEL_ID = "C12345678"  # 対象チャンネルID

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'slack_data'
}

# Fetch all users from Slack
def fetch_users():
    url = "https://slack.com/api/users.list"
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200 or not response.json().get('ok'):
        raise Exception("Failed to fetch users: " + response.text)

    # Create a mapping of user_id to user_name
    users = response.json().get('members', [])
    return {user['id']: user['profile'].get('real_name', user['name']) for user in users}

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
def store_messages_in_db(messages, user_map):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR(50) PRIMARY KEY,
                user_id VARCHAR(50),
                user_name VARCHAR(100),
                text TEXT,
                ts TIMESTAMP
            )
        """)

        # Insert messages into the table
        for message in messages:
            message_id = message.get('client_msg_id') or f"system_{message['ts']}"
            user_id = message.get('user', 'system')
            user_name = user_map.get(user_id, 'Unknown')  # デフォルトで 'Unknown' を設定
            text = message.get('text', '')

            cursor.execute("""
                INSERT INTO messages (id, user_id, user_name, text, ts) 
                VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
                ON DUPLICATE KEY UPDATE text = VALUES(text)
            """, (message_id, user_id, user_name, text, float(message['ts'])))

        connection.commit()
    except mysql.connector.Error as e:
        print("Error: ", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Main Execution
if __name__ == "__main__":
    print("Fetching user data from Slack...")
    user_map = fetch_users()

    print("Fetching Slack messages...")
    messages = fetch_slack_messages()

    print(f"Storing {len(messages)} messages in the database...")
    store_messages_in_db(messages, user_map)

    print("Messages successfully stored with user names!")
