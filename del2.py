import os
import shutil
import time
import sys

def load_exclude_list(file_path):
    """除外リストをファイルから読み込む"""
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"除外リストファイルが見つかりません: {file_path}")
        return []

def delete_old_directories(target_dir, days, exclude_list_file):
    """指定した日数より古いディレクトリを削除する"""
    # 現在時刻のタイムスタンプを取得
    current_time = time.time()

    # 除外リストを読み込む
    exclude_list = load_exclude_list(exclude_list_file)

    # ターゲットディレクトリ内をスキャン
    for entry in os.scandir(target_dir):
        if entry.is_dir():
            # サブディレクトリ名を取得
            dir_name = os.path.basename(entry.path)
            
            # 除外リストに含まれているかチェック
            if dir_name in exclude_list:
                print(f"除外対象のためスキップ: {dir_name}")
                continue
            
            # 最終変更時刻を取得
            last_modified_time = os.path.getmtime(entry.path)
            
            # 指定日数以上経過しているか判定
            if (current_time - last_modified_time) / (24 * 3600) >= days:
                try:
                    # ディレクトリを削除
                    shutil.rmtree(entry.path)
                    print(f"削除しました: {entry.path}")
                except Exception as e:
                    print(f"削除中にエラーが発生しました: {entry.path}, エラー: {e}")

if __name__ == "__main__":
    # コマンドライン引数の確認
    if len(sys.argv) < 2:
        print("使用方法: python script_name.py <削除対象を調べるディレクトリパス> <日数(デフォルト10日)> <除外リストファイル>")
        sys.exit(1)

    # 引数の取得
    target_directory = sys.argv[1]  # 必須: 処理対象のディレクトリ
    days_threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 10  # オプション: 日数（デフォルト10日）
    exclude_list_path = sys.argv[3] if len(sys.argv) > 3 else "exclude_list.txt"  # オプション: 除外リストファイル

    # 対象ディレクトリの存在確認
    if not os.path.isdir(target_directory):
        print(f"指定されたディレクトリが存在しません: {target_directory}")
        sys.exit(1)

    # 除外リストファイルの確認（存在しない場合警告を表示）
    if not os.path.isfile(exclude_list_path):
        print(f"警告: 除外リストファイルが存在しません: {exclude_list_path}")

    # ディレクトリ削除処理を実行
    delete_old_directories(target_directory, days_threshold, exclude_list_path)
