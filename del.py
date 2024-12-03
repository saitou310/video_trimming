import os
import shutil
from datetime import datetime

def clean_old_directories(target_dir):
    try:
        # ディレクトリ内のすべてのサブディレクトリを取得
        subdirs = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]

        # 作成時間順にソート
        subdirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        # 最新の2つを除く
        old_dirs = subdirs[2:]

        # 削除処理
        for old_dir in old_dirs:
            shutil.rmtree(old_dir)
            print(f"削除しました: {old_dir}")
        
        print("処理完了。最新2ディレクトリを残しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    # 処理対象のディレクトリを指定
    target_directory = r"C:\example\path"  # 対象のディレクトリパスを変更してください
    clean_old_directories(target_directory)
