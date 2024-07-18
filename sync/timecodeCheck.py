```python
import subprocess

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

# 비디오 파일 경로
video_path = 'C:/Users/user/Desktop/손정우/G1V4L9J.MP4'

# 타임코드 추출
timecode = extract_timecode(video_path)

# 결과 출력
if timecode:
    print(f'Timecode: {timecode}')
else:
    print('Timecode not found')

```
