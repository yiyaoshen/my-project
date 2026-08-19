import os
import json
import binascii
import requests

# ==========================================
# 1. 基础配置
# ==========================================
# 替换为你的真实 API Key 
# 注意：国内主机一般使用 api.minimax.chat，海外使用 api.minimax.io
API_KEY = "sk-api-Fr5s1KJMTRtrOpWpz8xamo4yVh0sIIaa64NUXrsTplmAsQ-YbxHxc9rlwI6BWhC2Kdxp16ILdiWr3hRm_SnPMtYf1yibciuAdDJXiTqkrq1qkVTBxTdGB7A"  
BASE_URL = "https://api.minimax.chat/v1" 

# ==========================================
# 2. 核心参数设置
# ==========================================
# 你的源音频文件路径（建议10秒-5分钟，无背景噪音的纯人声，小于20MB，支持mp3, m4a, wav）
SOURCE_AUDIO_PATH = "/Users/yiyaoshen/Downloads/彼得·蒂尔.MP3"     

# 你的自定义音色ID（需由字母开头，长度8-256字符，支持字母、数字、下划线、中划线）
CUSTOM_VOICE_ID = "my_custom_voice_001"  

# 需要生成的文本内容
TEXT_TO_SPEAK = "这一句话，可能会让你感到愤怒。 因为从小到大，学校教你要竞争。你要考第一名，你要在体育比赛中赢，你要在职场上打败同事。 你们被训练成了竞争机器。 但今天，我要拆掉你们脑子里的这个程序。 我要告诉你们，为什么那些陷入红海厮杀的人最终都一无所有，而那些建立垄断的人，才是推动世界进步的唯一力量。" 

# 最终生成的语音文件保存路径
OUTPUT_AUDIO_PATH = "output_generated.mp3"  


def upload_audio_for_clone(file_path):
    """
    第一步：上传音频文件，获取 file_id
    """
    url = f"{BASE_URL}/files/upload"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    print(f"[{'上传阶段'}] 正在上传音频文件: {file_path}...")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'purpose': 'voice_clone'}
        response = requests.post(url, headers=headers, data=data, files=files)
    
    response.raise_for_status()
    result = response.json()
    
    # 校验上传结果
    if result.get("base_resp", {}).get("status_code") == 0 or "file" in result:
        file_id = result.get("file", {}).get("file_id")
        print(f"✅ 上传成功！获取到 File ID: {file_id}")
        return file_id
    else:
        raise Exception(f"❌ 上传失败: {result}")

def clone_voice(file_id, voice_id):
    """
    第二步：利用 file_id 克隆出自定义的音色 voice_id
    """
    url = f"{BASE_URL}/voice_clone"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "file_id": file_id,
        "voice_id": voice_id
    }
    print(f"\n[{'克隆阶段'}] 正在注册音色 (Voice ID: {voice_id})...")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    
    if result.get("base_resp", {}).get("status_code") == 0:
        print("✅ 音色克隆注册成功！")
        return True
    else:
        raise Exception(f"❌ 克隆失败: {result}")

def text_to_speech(voice_id, text, output_path):
    """
    第三步：使用刚才克隆生成的 voice_id，进行文本转语音 (T2A)
    """
    url = f"{BASE_URL}/t2a_v2"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 使用官方推荐的高保真模型 speech-02-hd
    payload = {
        "model": "speech-02-hd",
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": 1.0,  # 语速
            "vol": 1.0,    # 音量
            "pitch": 0     # 语调
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }
    }
    print(f"\n[{'合成阶段'}] 正在使用克隆音色生成语音...")
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    # MiniMax T2A_V2 非流式通常返回 JSON，其中包含 Hex 编码的音频数据
    if "application/json" in response.headers.get("Content-Type", ""):
        res_data = response.json()
        if res_data.get("base_resp", {}).get("status_code") != 0:
            raise Exception(f"❌ 语音生成失败: {res_data}")
            
        audio_hex = res_data.get("data", {}).get("audio", "")
        if not audio_hex:
            raise Exception("❌ 未在返回结果中找到音频数据。")
            
        # 将 Hex 字符串解码成二进制文件
        with open(output_path, "wb") as f:
            f.write(binascii.unhexlify(audio_hex))
            
    else:
        # 兼容处理直接返回二进制流的情况
        with open(output_path, "wb") as f:
            f.write(response.content)
            
    print(f"✅ 语音生成成功！已保存至: {output_path}")

if __name__ == "__main__":
    try:
        # 1. 传文件
        file_id = upload_audio_for_clone(SOURCE_AUDIO_PATH)
        
        # 2. 建音色
        clone_voice(file_id, CUSTOM_VOICE_ID)
        
        # 3. 产语音
        text_to_speech(CUSTOM_VOICE_ID, TEXT_TO_SPEAK, OUTPUT_AUDIO_PATH)
        
    except Exception as e:
        print(f"\n发生错误: {e}")