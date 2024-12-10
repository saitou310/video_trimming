import requests
import mysql.connector
from mysql.connector import Error

def fetch_jenkins_builds(base_url, job_name, username, api_token):
    """Jenkins APIを利用してビルド履歴を取得"""
    builds = []
    start = 0
    while True:
        url = f"{base_url}/job/{job_name}/api/json?tree=builds[number,status,timestamp,duration,result]&start={start}"
        try:
            response = requests.get(url, auth=(username, api_token))
            response.raise_for_status()
            data = response.json().get('builds', [])
            if not data:
                break  # データが空の場合、すべて取得完了
            builds.extend(data)
            start += len(data)  # 次の開始位置を設定
        except requests.exceptions.RequestException as e:
            print(f"Jenkins APIリクエストエラー: {e}")
            break
    return builds

def save_to_mysql(db_config, job_name, builds):
    """MySQLにビルド履歴を挿入または更新"""
    try:
        # MySQLに接続
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = connection.cursor()

        # テーブルを作成（存在しない場合）
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {job_name}_history (
            build_number INT PRIMARY KEY,
            status VARCHAR(255),
            timestamp BIGINT,
            duration BIGINT,
            result VARCHAR(50)
        );
        """
        cursor.execute(create_table_query)

        # データを挿入または更新
        insert_query = f"""
        INSERT INTO {job_name}_history (build_number, status, timestamp, duration, result)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        status = VALUES(status),
        timestamp = VALUES(timestamp),
        duration = VALUES(duration),
        result = VALUES(result);
        """
        for build in builds:
            data = (
                build.get('number'),
                'SUCCESS' if build.get('result') == 'SUCCESS' else 'FAILED',
                build.get('timestamp'),
                build.get('duration'),
                build.get('result')
            )
            cursor.execute(insert_query, data)

        connection.commit()
        print(f"{len(builds)}件のビルド履歴を保存または更新しました。")
    except Error as e:
        print(f"MySQLエラー: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Jenkins設定
    jenkins_base_url = "http://your-jenkins-url"
    job_name = "your_job_name"
    username = "your_username"
    api_token = "your_api_token"

    # MySQL設定
    db_config = {
        "host": "localhost",
        "user": "your_mysql_user",
        "password": "your_mysql_password",
        "database": "your_database"
    }

    # Jenkinsビルド履歴を取得
    builds = fetch_jenkins_builds(jenkins_base_url, job_name, username, api_token)

    if builds:
        # データをMySQLに保存
        save_to_mysql(db_config, job_name, builds)
    else:
        print("ビルド履歴が見つかりませんでした。")
