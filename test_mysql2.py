import mysql.connector
from mysql.connector import Error

def calculate_time_to_success(db_config, job_name):
    """失敗から成功までの時間を計算して保存"""
    try:
        # MySQLに接続
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = connection.cursor(dictionary=True)

        # ジョブ履歴を取得（ビルド番号順）
        select_query = f"""
        SELECT build_number, result, timestamp, time_to_success
        FROM {job_name}_history
        ORDER BY build_number
        """
        cursor.execute(select_query)
        builds = cursor.fetchall()

        # 前回の失敗を記録
        last_failed_timestamp = None

        # 時間を更新
        for build in builds:
            if build['result'] == 'FAILURE':
                # 失敗時のタイムスタンプを記録
                last_failed_timestamp = build['timestamp']
            elif build['result'] == 'SUCCESS' and last_failed_timestamp:
                # 成功時に前回の失敗からの時間を計算
                time_to_success = (build['timestamp'] - last_failed_timestamp) // 1000  # 秒に変換

                # データベースを更新
                update_query = f"""
                UPDATE {job_name}_history
                SET time_to_success = %s
                WHERE build_number = %s
                """
                cursor.execute(update_query, (time_to_success, build['build_number']))
                print(f"ビルド {build['build_number']} の失敗から成功までの時間: {time_to_success} 秒")

                # 前回の失敗タイムスタンプをリセット
                last_failed_timestamp = None

        # 変更をコミット
        connection.commit()
    except Error as e:
        print(f"MySQLエラー: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # MySQL設定
    db_config = {
        "host": "localhost",
        "user": "your_mysql_user",
        "password": "your_mysql_password",
        "database": "your_database"
    }

    # Jenkinsジョブ名
    job_name = "your_job_name"

    # 失敗から成功までの時間を計算
    calculate_time_to_success(db_config, job_name)
