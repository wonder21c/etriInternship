import cv2
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

def extract_frame(video_path, frame_idx, output_folder, video_idx):
    frame_folder = os.path.join(output_folder, f"{str(frame_idx + 1)}", "images")
    os.makedirs(frame_folder, exist_ok=True)
    
    # 이미지 파일 이름을 비디오 인덱스로 지정
    frame_output = os.path.join(frame_folder, f"{str(video_idx).zfill(3)}.png")
    
    if os.path.exists(frame_output):
        print(f"이미 존재하는 파일: {frame_output}, 건너뜁니다.")
        return
    
    command = [
        'ffmpeg', '-i', video_path,
        '-vf', f"select=eq(n\\,{frame_idx})",
        '-vsync', 'vfr',
        '-q:v', '2',
        '-frames:v', '1',
        '-pix_fmt', 'rgb24', 
        frame_output
    ]
    subprocess.run(command)

def extract_frames_from_folder(folder_path, output_folder):
    video_paths = [
        os.path.join(folder_path, filename)
        for filename in sorted(os.listdir(folder_path))
        if filename.endswith(('.MP4', '.avi', '.mov', '.mkv'))
    ]
    
    if not video_paths:
        print("해당 폴더에 동영상 파일이 없습니다.")
        return
    
    frame_counts = []
    max_frames = 0
    
    for video_path in video_paths:
        cap = cv2.VideoCapture(video_path)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_counts.append(frames)
        max_frames = max(max_frames, frames)
        cap.release()
    
    with ThreadPoolExecutor() as executor:
        for frame_idx in range(max_frames):
            for video_idx, video_path in enumerate(video_paths):
                if frame_idx < frame_counts[video_idx]:
                    # video_idx를 전달하여 이미지 파일 이름에 사용
                    executor.submit(extract_frame, video_path, frame_idx, output_folder, video_idx)

folder_path = "C:/Users/user/Desktop/손정우/sync/d"
output_folder = "C:/Users/user/Desktop/손정우/sync/output3"

if os.path.exists(folder_path):
    extract_frames_from_folder(folder_path, output_folder)
else:
    print(f"지정된 경로를 찾을 수 없습니다: {folder_path}")
