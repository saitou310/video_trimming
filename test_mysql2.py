import mysql.connector
from mysql.connector import Error

def create_failure_to_success_table(db_config, job_name):
    """失敗から成功までの時間を保持する新しいテーブルを作成"""
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = connection.cursor()

        # 新しいテーブルを作成
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {job_name}_failure_to_success (
            failure_build_number INT PRIMARY KEY,
            success_build_number INT,
            time_to_success BIGINT
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print(f"テーブル {job_name}_failure_to_success を作成しました。")
    except Error as e:
        print(f"MySQLエラー: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def calculate_and_store_time_to_success(db_config, job_name):
    """失敗から成功までの時間を計算し、新しいテーブルに保存"""
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = connection.cursor(dictionary=True)

        # ジョブ履歴を取得（ビルド番号順）
        select_query = f"""
        SELECT build_number, result, timestamp
        FROM {job_name}_history
        ORDER BY build_number
        """
        cursor.execute(select_query)
        builds = cursor.fetchall()

        # 失敗から成功のデータを保存
        insert_query = f"""
        INSERT INTO {job_name}_failure_to_success (failure_build_number, success_build_number, time_to_success)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        success_build_number = VALUES(success_build_number),
        time_to_success = VALUES(time_to_success)
        """

        # 前回の失敗を記録
        last_failed_build = None

        for build in builds:
            if build['result'] == 'FAILURE':
                # 失敗したビルドを記録
                last_failed_build = build
            elif build['result'] == 'SUCCESS' and last_failed_build:
                # 成功時に前回の失敗からの時間を計算
                time_to_success = (build['timestamp'] - last_failed_build['timestamp']) // 1000  # 秒に変換

                # 新しいテーブルにデータを保存
                data = (
                    last_failed_build['build_number'],
                    build['build_number'],
                    time_to_success
                )
                cursor.execute(insert_query, data)
                print(f"ビルド {last_failed_build['build_number']} からビルド {build['build_number']} までの時間: {time_to_success} 秒")

                # 前回の失敗をリセット
                last_failed_build = None

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

    # 新しいテーブルを作成
    create_failure_to_success_table(db_config, job_name)

    # 失敗から成功までの時間を計算し保存
    calculate_and_store_time_to_success(db_config, job_name)
