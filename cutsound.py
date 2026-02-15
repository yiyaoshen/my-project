# 您需要先安装 pydub 库: pip install pydub
# 并确保您的系统已安装 ffmpeg (用于处理 mp3)

from pydub import AudioSegment
import math
import os


def split_audio(file_path, segment_length_sec=25):
    # 加载音频文件
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        print(f"无法加载音频文件: {e}")
        return

    # 计算分段时长 (毫秒)
    segment_length_ms = segment_length_sec * 1000
    total_length_ms = len(audio)

    # 计算分段数量
    num_segments = math.ceil(total_length_ms / segment_length_ms)

    print(f"音频总时长: {total_length_ms / 1000:.2f}秒")
    print(f"正在分割为 {num_segments} 个片段...")

    # 分割并导出
    filename_base = os.path.splitext(os.path.basename(file_path))[0]

    for i in range(num_segments):
        start_time = i * segment_length_ms
        end_time = min((i + 1) * segment_length_ms, total_length_ms)

        segment = audio[start_time:end_time]

        output_filename = f"{filename_base}_part{i + 1}.mp3"
        segment.export(output_filename, format="mp3")
        print(f"已生成: {output_filename}")


# 运行分割
split_audio("/Users/yiyaoshen/Downloads/伞翻在风里.mp3")
