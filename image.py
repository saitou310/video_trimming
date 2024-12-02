import cv2
import sys

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

if __name__ == "__main__":
    # 引数が3つあるか確認
    if len(sys.argv) != 4:
        print("使用方法: python script_name.py <動画ファイルパス> <秒数> <出力画像パス>")
        sys.exit(1)

    # コマンドライン引数を取得
    video_path = sys.argv[1]
    time_in_seconds = float(sys.argv[2])  # 秒数を浮動小数点数に変換
    output_image_path = sys.argv[3]

    # フレーム抽出を実行
    extract_frame_from_video(video_path, time_in_seconds, output_image_path)
