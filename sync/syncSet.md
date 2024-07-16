import subprocess
from datetime import datetime, timedelta
import os

def extract_timecode(video_path):
    # FFmpeg 명령어를 사용하여 메타데이터 추출
    command = [
        'ffmpeg',
        '-i', video_path,
        '-f', 'ffmetadata',
        '-'
    ]

    # FFmpeg 명령 실행
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='ignore')

    # FFmpeg 출력에서 타임코드 추출
    metadata = result.stderr  # FFmpeg는 메타데이터를 stderr에 출력합니다
    timecode = None
    for line in metadata.split('\n'):
        if 'timecode' in line:
            timecode = line.split(': ')[1].strip()
            break

    return timecode

def timecode_to_timedelta(timecode):
    # 타임코드를 시간 델타로 변환 (HH:MM:SS:FF 형식)
    hours, minutes, seconds, frames = map(int, timecode.split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=frames * (1000 / 30))  # Assuming 30 FPS

def trim_video(video_path, start_time, output_path):
    # FFmpeg 명령어를 사용하여 비디오 자르기
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(start_time),
        '-c', 'copy',
        output_path
    ]
    subprocess.run(command)

# 비디오 파일 경로 목록
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

# 출력 경로 지정
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

    # 각 비디오 파일에서 기준 타임코드를 뺀 값만큼 자르고 추가로 5초 더 자르기
    additional_trim = timedelta(seconds=5)
    for video_path, timecode in timecodes:
        if timecode:
            tc_timedelta = timecode_to_timedelta(timecode)
            start_time = latest_timecode_timedelta - tc_timedelta + additional_trim
            output_path = os.path.join(output_dir, os.path.basename(video_path).replace('.MP4', '_output.MP4'))
            trim_video(video_path, start_time, output_path)
            print(f'Trimmed {video_path} by {start_time}, saved as {output_path}')
else:
    print('No valid timecodes found')
