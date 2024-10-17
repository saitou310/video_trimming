import os
import random
import sys
import cv2
import numpy as np

# 動画を処理する関数
def trim_video(input_path, output_dir, num_videos):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 元の動画を読み込み
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {input_path}")
        return

    # FFmpegが使用可能かどうかを確認
    ffmpeg_available = os.system("ffmpeg -version") == 0
    if not ffmpeg_available:
        print("Warning: FFmpeg is not available. Audio will not be included in the output videos.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    for i in range(1, num_videos + 1):
        # ランダムに開始時間と終了時間を決定 (0〜5秒)
        start_trim = random.uniform(0, 5)
        end_trim = random.uniform(0, 5)

        # トリミング後の開始・終了時間を計算
        start_time = start_trim
        end_time = max(0, duration - end_trim)

        # 開始時間が終了時間を超えないように調整
        if start_time >= end_time:
            start_time = 0
            end_time = duration

        # 開始フレームと終了フレームを計算
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        # 動画をトリミング
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_path = os.path.join(output_dir, f"output_{i:03d}.mp4")
        out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        for frame_num in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        out.release()

        if ffmpeg_available:
            # トリミングした動画に音声を追加（映像と音声を同時にトリミング）
            final_output_path = os.path.join(output_dir, f"output_with_audio_{i:03d}.mp4")
            os.system(f"ffmpeg -i {input_path} -ss {start_time} -to {end_time} -c:v copy -c:a aac -strict experimental {final_output_path} -y")

            # 一時ファイルを削除
            os.remove(output_path)
        else:
            final_output_path = output_path

    # リソースを解放
    cap.release()

# 引数からのパラメータ取得
if len(sys.argv) > 3:
    input_video_path = sys.argv[1]
    output_directory = sys.argv[2]
    number_of_videos = int(sys.argv[3])
else:
    # 入力動画ファイルのパス
    input_video_path = "Screen_Recording_20241013_070631.mp4"
    # 出力ディレクトリ
    output_directory = "output_videos"
    # 作成したい動画の数
    number_of_videos = 10

# 動画を処理
trim_video(input_video_path, output_directory, number_of_videos)
