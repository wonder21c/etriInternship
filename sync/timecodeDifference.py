```python
import subprocess
from datetime import timedelta

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
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=frames * (1000 / 30))  # Assuming 30 FPS

# 비디오 파일 경로 목록
video_paths = [
    'C:/Users/user/Desktop/손정우/sync/gopro03_240503.MP4',
    'C:/Users/user/Desktop/손정우/sync/gopro04_240503.MP4'
]

# 각 비디오 파일에서 타임코드 추출
timecodes = []
for video_path in video_paths:
    timecode = extract_timecode(video_path)
    if timecode:
        timecodes.append((video_path, timecode))
    else:
        print(f'Timecode not found for {video_path}')
        timecodes.append((video_path, None))

# 타임코드와 차이 계산
if all(tc[1] is not None for tc in timecodes) and len(timecodes) == 2:
    tc1_path, tc1_str = timecodes[0]
    tc2_path, tc2_str = timecodes[1]
    tc1 = timecode_to_timedelta(tc1_str)
    tc2 = timecode_to_timedelta(tc2_str)
    time_difference = abs(tc2 - tc1)

    print(f'Timecode for {tc1_path}: {tc1_str}')
    print(f'Timecode for {tc2_path}: {tc2_str}')
    print(f'Time difference: {time_difference}')
else:
    print('Could not calculate time difference due to missing timecode')


```
