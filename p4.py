import subprocess
import re

def get_last_committer(file_path):
    try:
        # p4 filelog -m 1 は最新1件のログを取得
        result = subprocess.run(
            ["p4", "filelog", "-m", "1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None

        # 例: ... #5 change 12345 edit on 2024/01/01 by user@client (text)
        match = re.search(r'by ([^@]+)@', result.stdout)
        if match:
            return match.group(1)
        else:
            print("Could not parse committer.")
            return None

    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# 使用例
file_path = "//depot/project/file.txt"  # p4 depot パス
last_user = get_last_committer(file_path)
if last_user:
    print(f"Last committer: {last_user}")
