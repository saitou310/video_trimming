import cv2
import numpy as np
import librosa
import json
import sys
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from moviepy.editor import VideoFileClip

# ユーザーに対してGUIでシークバーとビデオプレビューを使用して開始フレームと終了フレームを指定させる関数
def prompt_for_frames_gui(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.35)
    ax.set_title("Select Start and End Points for Trimming")

    # 開始点と終了点のスライダーを作成
    ax_start = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    ax_end = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    
    slider_start = Slider(ax_start, 'Start', 0, duration, valinit=0)
    slider_end = Slider(ax_end, 'End', 0, duration, valinit=duration)

    # スライダーを更新する関数
    def update(val):
        start_time = slider_start.val
        end_time = slider_end.val
        if start_time >= end_time:
            slider_end.set_val(start_time + 1 if start_time + 1 <= duration else duration)
        fig.canvas.draw_idle()
        show_frame(start_time)

    slider_start.on_changed(update)
    slider_end.on_changed(update)

    # スライダーの位置に対応するビデオフレームを表示する関数
    def show_frame(time):
        cap.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (800, 450))  # Resize for better display
            cv2.imshow('Video Preview', frame)

    # スライダーの動きを処理し、ビデオプレビューを更新する関数
    def on_slider_change(val):
        show_frame(slider_start.val)

    slider_start.on_changed(on_slider_change)
    slider_end.on_changed(lambda val: show_frame(slider_end.val))

    # matplotlibの終了イベント
    def on_select(event):
        plt.close(fig)
        cap.release()
        cv2.destroyAllWindows()

    btn_select = plt.axes([0.8, 0.025, 0.1, 0.04])
    button = Button(btn_select, 'Select')
    button.on_clicked(on_select)

    # ビデオプレビューを表示
    show_frame(0)
    cv2.namedWindow('Video Preview', cv2.WINDOW_NORMAL)  # Allow resizing of the video window
    plt.show()

    start_frame = int(slider_start.val * fps)
    end_frame = int(slider_end.val * fps)
    
    return start_frame, end_frame

# 分析のために2秒間のビデオおよび音声セグメントを抽出する関数
def extract_segments(video_path, start_frame, end_frame, fps):
    start_time = max(0, (start_frame / fps) - 2)
    end_time = min((end_frame / fps) + 2, VideoFileClip(video_path).duration)
    
    video_clip = VideoFileClip(video_path).subclip(start_time, end_time)
    audio_clip = video_clip.audio
    
    return video_clip, audio_clip

# 音声の特徴を分析する関数
def analyze_audio(audio_clip, sr=22050):
    if audio_clip is None:
        print("No audio track found in the video segment. Skipping audio analysis.")
        return None
    # 音声データをnumpy配列として抽出
    audio_data = audio_clip.to_soundarray(fps=sr)
    audio_mono = librosa.to_mono(audio_data.T)
    
    # 音声の特徴を抽出（例: RMS、スペクトル重心）
    rms = librosa.feature.rms(y=audio_mono)[0]
    spectral_centroids = librosa.feature.spectral_centroid(y=audio_mono, sr=sr)[0]
    
    return {
        'rms': rms.tolist(),
        'spectral_centroids': spectral_centroids.tolist()
    }

# 分析データを保存する関数
def save_analysis_data(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file)

# 分析データを読み込む関数
def load_analysis_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as json_file:
            return json.load(json_file)
    return []

# OpenCVを使用してビデオをトリミングするメイン関数（高速処理のため）
def trim_video_with_analysis(video_path, output_path, learn_mode=False):
    analysis_data_file = "analysis_data.json"
    analysis_data = load_analysis_data(analysis_data_file)
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if learn_mode:
        # 学習モードの場合、ユーザーに開始フレームと終了フレームを指定させる
        print("Learning mode activated. Please specify trim points manually.")
        start_frame, end_frame = prompt_for_frames_gui(video_path)
        # 将来使用するために分析データを保存
        new_data = {
            'video_path': video_path,
            'start_frame': start_frame,
            'end_frame': end_frame
        }
        analysis_data.append(new_data)
        print(f"Saving analysis data to {analysis_data_file}")
        save_analysis_data(analysis_data, analysis_data_file)
        print(f"Finished saving analysis data to {analysis_data_file}")
        confidence = 100  # Learning mode confidence is 100%
    elif any(item.get('video_path') == video_path for item in analysis_data):
        print("Using previously saved analysis data for trimming.")
        previous_data = next(item for item in analysis_data if item.get('video_path') == video_path)
        start_frame = previous_data['start_frame']
        end_frame = previous_data['end_frame']
        confidence = 100  # 正確に以前のデータを使用
    else:
        if analysis_data:
            print("Using generalized analysis data for suggesting trim points.")
            # 一般化されたデータを使用して開始フレームと終了フレームを提案
            avg_start = int(sum(item['start_frame'] for item in analysis_data) / len(analysis_data))
            avg_end = int(sum(item['end_frame'] for item in analysis_data) / len(analysis_data))
            start_frame = max(0, min(avg_start, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
            end_frame = max(start_frame + 1, min(avg_end, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
            # 平均値への近さに基づいて信頼度を計算
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            confidence = int((1 - (abs(avg_start - start_frame) + abs(avg_end - end_frame)) / (2 * total_frames)) * 100)
        else:
            # 分析データが利用できない場合、デフォルトのトリムポイントを設定
            print("No previous analysis data found. Using default trim points.")
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            start_frame = int(0.1 * total_frames)  # Default to 10% into the video
            end_frame = int(0.9 * total_frames)  # Default to 90% into the video
            confidence = 0  # No prior data available, lowest confidence
            
        # Save analysis data for future use
        new_data = {
            'video_path': video_path,
            'start_frame': start_frame,
            'end_frame': end_frame
        }
        analysis_data.append(new_data)
        print(f"Saving analysis data to {analysis_data_file}")
        save_analysis_data(analysis_data, analysis_data_file)
        print(f"Finished saving analysis data to {analysis_data_file}")
    
    # 出力ディレクトリが存在することを確認
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # OpenCVを使用してトリミングしたビデオをユニークなファイル名で保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_path, f"trimmed_{timestamp}.mp4")
    print(f"Starting to write trimmed video to {output_file}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame = start_frame
    
    while current_frame <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Finished writing trimmed video to {output_file}")

    # 分析のために2秒間のビデオと音声セグメントを抽出
    print(f"Extracting video and audio segments for analysis from {video_path}")
    video_segment, audio_segment = extract_segments(video_path, start_frame, end_frame, fps)
    print(f"Finished extracting video and audio segments from {video_path}")
    
    # 音声の特徴を分析
    if audio_segment is not None:
        print(f"Analyzing audio features for {output_file}")
        audio_features = analyze_audio(audio_segment)
        print(f"Finished analyzing audio features for {output_file}")
    else:
        audio_features = None
        print("No audio found in the trimmed segment. Skipping audio analysis.")
    
    # 音声の特徴と一般化されたデータを含めて分析データを保存
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    analysis_data[-1]['audio_features'] = audio_features
    analysis_data[-1]['average_start_frame'] = int((analysis_data[-1].get('average_start_frame', start_frame) + start_frame) / 2)
    analysis_data[-1]['average_end_frame'] = int((analysis_data[-1].get('average_end_frame', end_frame) + end_frame) / 2)
    print(f"Saving updated analysis data to {analysis_data_file}")
    save_analysis_data(analysis_data, analysis_data_file)
    print(f"Finished saving updated analysis data to {analysis_data_file}")

    # 信頼度を出力
    print(f"Estimated confidence level for trimming: {confidence}%")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python import_cv2_4.py <video_path> <output_path> [learn_mode]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2]
    learn_mode = len(sys.argv) > 3 and sys.argv[3].lower() == 'learn'
    
    trim_video_with_analysis(video_path, output_path, learn_mode)
