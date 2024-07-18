import cv2
import subprocess
from datetime import timedelta
import os

def extract_frame_at_time(video_path, timecode, output_image_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'select=\'gte(t,{timecode.total_seconds()})\'',
        '-vframes', '1',
        output_image_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_video_duration_and_frames(video_path):
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=duration,nb_frames',
        '-of', 'csv=p=0',
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        duration, frames = result.stdout.strip().split(',')
        return float(duration), int(frames)
    except ValueError:
        print(f"Could not get duration and frame count for {video_path}: {result.stderr}")
        return 0.0, 0

def trim_video(video_path, start_time, duration, output_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', f"{start_time.total_seconds():.3f}",
        '-t', f"{duration.total_seconds():.3f}",
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-preset', 'fast',
        '-crf', '23',
        output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def extract_timecode(video_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-f', 'ffmetadata',
        '-'
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='ignore')
    metadata = result.stderr
    timecode = None
    for line in metadata.split('\n'):
        if 'timecode' in line:
            timecode = line.split(': ')[1].strip()
            break
    return timecode

def timecode_to_timedelta(timecode):
    hours, minutes, seconds, frames = map(int, timecode.split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=frames * (1000 / 60))

video_paths = [
    'C:/Users/user/Desktop/손정우/sync/gopro01_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro02_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro03_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro04_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro05_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro06_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro07_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro08_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro09_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro10_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro11_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro12_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro13_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro14_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro15_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro16_240503.MP4'
]

output_dir = 'C:/Users/user/Desktop/손정우/sync/output/'
os.makedirs(output_dir, exist_ok=True)

# 각 비디오 파일에서 타임코드 추출
timecodes = []
for video_path in video_paths:
    timecode = extract_timecode(video_path)
    if timecode:
        timecodes.append((video_path, timecode))
    else:
        print(f'Timecode not found for {video_path}')
        timecodes.append((video_path, None))

# 가장 늦은 타임코드 찾기
max_timecode = None
max_timedelta = timedelta(0)
for video_path, timecode in timecodes:
    if timecode:
        tc_timedelta = timecode_to_timedelta(timecode)
        if tc_timedelta > max_timedelta:
            max_timedelta = tc_timedelta
            max_timecode = (video_path, timecode)

if max_timecode:
    print(f'Latest timecode is {max_timecode[1]} from {max_timecode[0]}')
    latest_timecode_timedelta = max_timedelta

    # 기준 타임코드에서 첫 번째 프레임 추출
    reference_frame_path = os.path.join(output_dir, 'reference_frame.jpg')
    extract_frame_at_time(max_timecode[0], latest_timecode_timedelta, reference_frame_path)
    reference_image = cv2.imread(reference_frame_path, cv2.IMREAD_GRAYSCALE)

    # 각 비디오 파일에서 기준 타임코드의 프레임으로 잘라내기
    trimmed_durations = []
    for video_path, timecode in timecodes:
        if timecode:
            tc_timedelta = timecode_to_timedelta(timecode)
            start_time = latest_timecode_timedelta - tc_timedelta
            video_duration, total_frames = get_video_duration_and_frames(video_path)
            trim_duration = timedelta(seconds=video_duration) - start_time
            trimmed_durations.append(trim_duration)

    # 가장 짧은 영상 길이에 맞춰 다른 영상 자르기
    min_duration = min(trimmed_durations)
    for video_path, timecode in timecodes:
        if timecode:
            tc_timedelta = timecode_to_timedelta(timecode)
            start_time = latest_timecode_timedelta - tc_timedelta
            output_path = os.path.join(output_dir, os.path.basename(video_path).replace('.MP4', '_final.MP4'))
            trim_video(video_path, start_time, min_duration, output_path)
            print(f'Trimmed {video_path} to minimum duration {min_duration}, saved as {output_path}')
else:
    print('No valid timecodes found')
