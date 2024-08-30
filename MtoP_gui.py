import cv2
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import time

def extract_frame(video_path, frame_idx, output_folder, video_idx, options, pause_event, stop_event):
    if stop_event.is_set():
        return

    frame_folder = os.path.join(output_folder, f"{str(frame_idx + 1)}", "images")
    os.makedirs(frame_folder, exist_ok=True)
    
    # 선택한 출력 이미지 포맷을 반영하도록 수정
    frame_output = os.path.join(frame_folder, f"{str(video_idx).zfill(5)}.{options['img_format'].lower()}")
    
    if os.path.exists(frame_output):
        print(f"이미 존재하는 파일: {frame_output}, 건너뜁니다.")
        return
    
    command = [
        'ffmpeg', '-i', video_path,
        '-vf', f"select=eq(n\\,{frame_idx})",
        '-frames:v', '1',
        '-pix_fmt', options['pix_fmt'],
        frame_output
    ]
    
    while not stop_event.is_set():
        if pause_event.is_set():
            time.sleep(0.1)
        else:
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"ffmpeg 명령어 오류: {e}")
            break 

    if stop_event.is_set():
        return

def extract_frames_from_folder(folder_path, output_folder, options, pause_event, stop_event):
    video_extensions = tuple(ext.lower() for ext in options['video_exts'])
    video_paths = [
        os.path.join(folder_path, filename)
        for filename in sorted(os.listdir(folder_path))
        if filename.lower().endswith(video_extensions)
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
        futures = []
        for frame_idx in range(max_frames):
            if stop_event.is_set():
                break  # stop_event가 설정되면 추가 작업을 생성하지 않음
            for video_idx, video_path in enumerate(video_paths):
                if frame_idx < frame_counts[video_idx]:
                    futures.append(executor.submit(extract_frame, video_path, frame_idx, output_folder, video_idx, options, pause_event, stop_event))
        for future in futures:
            if stop_event.is_set():
                break
            future.result()

def on_run_button_click(pause_event, stop_event):
    folder_path = folder_path_entry.get()
    output_folder = output_folder_entry.get()
    
    options = {
        'pix_fmt': pix_fmt_var.get(),
        'video_exts': [ext.strip() for ext in video_exts_var.get().split(',')],
        'img_format': img_format_var.get()  # 선택한 이미지 포맷 추가
    }
    
    if os.path.exists(folder_path):
        threading.Thread(target=extract_frames_from_folder, args=(folder_path, output_folder, options, pause_event, stop_event)).start()
    else:
        print(f"지정된 경로를 찾을 수 없습니다: {folder_path}")

def select_input_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_path)

def select_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, folder_path)

def pause_extraction(pause_event):
    pause_event.set()

def resume_extraction(pause_event):
    pause_event.clear()

def close_program(pause_event, stop_event):
    stop_event.set()  # 종료 
    pause_event.set()  # 일시정지 
    root.quit()  # GUI 종료
    root.destroy()  # GUI 자원 해제
    print("프로그램이 종료되었습니다.")

# GUI 설정
root = tk.Tk()
root.title("FFmpeg 옵션 설정")

# 비디오 폴더 경로 입력
tk.Label(root, text="비디오 폴더 경로:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
folder_path_entry = tk.Entry(root, width=50)
folder_path_entry.grid(row=0, column=1, padx=10, pady=5)
folder_path_button = tk.Button(root, text="폴더 선택", command=select_input_folder)
folder_path_button.grid(row=0, column=2, padx=10, pady=5)

# 출력 폴더 경로 입력
tk.Label(root, text="출력 폴더 경로:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.grid(row=1, column=1, padx=10, pady=5)
output_folder_button = tk.Button(root, text="폴더 선택", command=select_output_folder)
output_folder_button.grid(row=1, column=2, padx=10, pady=5)

# pix_fmt 옵션 선택
tk.Label(root, text="pix_fmt (픽셀 포맷):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
pix_fmt_var = tk.StringVar(value='rgb24')
pix_fmt_menu = ttk.Combobox(root, textvariable=pix_fmt_var, values=['rgb24', 'yuv420p', 'gray', 'rgb32', 'rgb48', 'rgba64'])
pix_fmt_menu.grid(row=2, column=1, padx=10, pady=5)

# 비디오 확장자 선택
tk.Label(root, text="비디오 확장자 (쉼표로 구분, 예: MP4,avi):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
video_exts_var = tk.StringVar(value='확장자를 선택하세요')
video_exts_menu = ttk.Combobox(root, textvariable=video_exts_var, values=['.MP4', '.avi', '.mov', '.mkv'])
video_exts_menu.grid(row=3, column=1, padx=10, pady=5)

# 출력 이미지 포맷 선택
tk.Label(root, text="출력 이미지 포맷:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
img_format_var = tk.StringVar(value='PNG')
img_format_menu = ttk.Combobox(root, textvariable=img_format_var, values=['PNG', 'JPEG', 'BMP', 'TIFF'])
img_format_menu.grid(row=4, column=1, padx=10, pady=5)

# 실행 버튼
run_button = tk.Button(root, text="실행", command=lambda: on_run_button_click(pause_event, stop_event))
run_button.grid(row=6, column=0, columnspan=3, pady=10)

# 일시정지 버튼
pause_button = tk.Button(root, text="일시정지", command=lambda: pause_extraction(pause_event))
pause_button.grid(row=7, column=0, columnspan=3, pady=10)

# 재개 버튼
resume_button = tk.Button(root, text="재개", command=lambda: resume_extraction(pause_event))
resume_button.grid(row=8, column=0, columnspan=3, pady=10)

# 종료 버튼
exit_button = tk.Button(root, text="종료", command=lambda: close_program(pause_event, stop_event))
exit_button.grid(row=9, column=0, columnspan=3, pady=10)

# Pause flag 및 Stop event 초기화
pause_event = threading.Event()  # 일시정지 이벤트
stop_event = threading.Event()   # 종료 이벤트

root.mainloop()
