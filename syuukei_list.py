from datetime import datetime, timedelta
import pytz
from collections import defaultdict

# ISO 8601形式のデータリスト
timestamps = [
    "2025-01-08T09:30:00.000+0900",
    "2025-01-08T10:15:00.000+0900",
    "2025-01-08T23:45:00.000+0900",
    "2025-01-09T09:30:00.000+0900",
    "2025-01-09T10:15:00.000+0900",
]

# タイムゾーン設定 (日本標準時 JST)
jst = pytz.timezone("Asia/Tokyo")

# 今日の開始時刻 (朝10時) と翌日の終了時刻 (朝9:59:59)
today = datetime.now(jst).replace(hour=0, minute=0, second=0, microsecond=0)
start_time = today.replace(hour=10)  # 今日の朝10時
end_time = start_time + timedelta(days=1) - timedelta(seconds=1)  # 翌日の朝9:59:59

# フォーマットを指定して文字列を datetime に変換
def parse_timestamp(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f%z")

# 指定期間内のデータを日付単位で集計
daily_data = defaultdict(list)  # 日付ごとにデータを格納する辞書

for ts in timestamps:
    dt = parse_timestamp(ts)
    if start_time <= dt < end_time:
        # 日付単位のキーを作成 (JST基準)
        date_key = dt.astimezone(jst).strftime("%Y-%m-%d")
        daily_data[date_key].append(ts)

# 結果を表示
print("集計期間: ", start_time, "から", end_time)
print("日付単位の集計結果:")
for date, data in daily_data.items():
    print(f"{date}: {data}")
