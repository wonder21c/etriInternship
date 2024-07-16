```python
import subprocess
from datetime import datetime, timedelta

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

# 비디오 파일 경로 목록
video_paths = [
    'C:/Users/user/Desktop/손정우/G1V4L9J.MP4',
    'C:/Users/user/Desktop/손정우/output1.mp4'
]

# 각 비디오 파일에서 타임코드 추출
timecodes = []
for video_path in video_paths:
    timecode = extract_timecode(video_path)
    if timecode:
        timecodes.append(timecode)
    else:
        print(f'Timecode not found for {video_path}')
        timecodes.append(None)

# 타임코드 차이 계산
if None not in timecodes and len(timecodes) == 2:
    tc1 = timecode_to_timedelta(timecodes[0])
    tc2 = timecode_to_timedelta(timecodes[1])
    time_difference = abs(tc2 - tc1)
    print(f'Time difference: {time_difference}')
else:
    print('Could not calculate time difference due to missing timecode')

```
