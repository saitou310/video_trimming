import subprocess
import re

def get_last_committer_before_changenum(file_path, max_change):
    try:
        # 最大10件の変更履歴を取得
        result = subprocess.run(
            ["p4", "filelog", "-m", "10", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None

        # 行ごとにパース
        lines = result.stdout.splitlines()
        for line in lines:
            # 例: ... #5 change 12345 edit on 2024/01/01 by user@client (text)
            match = re.search(r'change (\d+).*? by ([^@]+)@', line)
            if match:
                changenum = int(match.group(1))
                user = match.group(2)
                if changenum <= max_change:
                    return user  # 最初にマッチしたものが「最後の変更者」
        print("該当する変更が見つかりませんでした。")
        return None

    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# 使用例
file_path = "//depot/project/file.txt"  # depotパスに置き換えてください
last_user = get_last_committer_before_changenum(file_path, max_change=10)
if last_user:
    print(f"Change #10 以前で最後に変更したユーザー: {last_user}")
