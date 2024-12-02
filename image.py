import cv2
import sys
import os
from datetime import datetime

def extract_frame_from_video(video_path, time_in_seconds, output_image_path):
    """
    動画から指定した時間のフレームを画像として保存する関数

    :param video_path: 動画ファイルのパス
    :param time_in_seconds: 取得したい時間（秒）
    :param output_image_path: 保存する画像ファイルのパス
    """
    # 動画ファイルを開く
    video = cv2.VideoCapture(video_path)

    # 動画のフレームレートを取得
    fps = video.get(cv2.CAP_PROP_FPS)

    # 時間に対応するフレーム番号を計算
    frame_number = int(fps * time_in_seconds)

    # 指定したフレーム番号に移動
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # フレームを読み込む
    success, frame = video.read()

    if success:
        # フレームを画像として保存
        cv2.imwrite(output_image_path, frame)
        print(f"フレームを保存しました: {output_image_path}")
    else:
        print("指定した時間のフレームを取得できませんでした。")

    # 動画を閉じる
    video.release()

def generate_default_image_name(video_path, time_in_seconds):
    """
    出力画像のデフォルトファイル名を生成する関数

    :param video_path: 動画ファイルのパス
    :param time_in_seconds: 取得したい時間（秒）
    :return: デフォルトの画像ファイル名
    """
    # 動画のファイル名を取得
    base_name = os.path.basename(video_path)
    name, _ = os.path.splitext(base_name)

    # 現在の日時を取得
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ファイル名を生成
    return f"{name}_{timestamp}_{int(time_in_seconds)}s.jpg"

if __name__ == "__main__":
    # 引数を取得
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not video_path:
        print("動画ファイルのパスを指定してください。")
        sys.exit(1)

    time_in_seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    output_image_path = sys.argv[3] if len(sys.argv) > 3 else generate_default_image_name(video_path, time_in_seconds)

    # フレーム抽出を実行
    extract_frame_from_video(video_path, time_in_seconds, output_image_path)
