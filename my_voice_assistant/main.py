import pyaudio      # PyAudio库，用于录制和播放音频流
import numpy as np  # 数组及数值处理库，处理音频帧数据
from funasr_onnx import SenseVoiceSmall  # FunASR ONNX 模型类，用于ASR识别
from funasr_onnx.utils.postprocess_utils import rich_transcription_postprocess  # ASR结果后处理，清洗文本
import sounddevice as sd  # SoundDevice库，用于录制麦克风音频并播放提示音
import time  # 时间模块，用于计时
import webrtcvad  # WebRTC VAD库，用于检测语音活动（VAD）
import os  # 操作系统接口，用于路径和文件操作
import requests  # HTTP请求库，用于调用LLM和TTS服务
import json  # JSON编解码库，用于保存对话历史
from datetime import datetime  # 获取当前时间，用于日志和文件名生成
from gpt_sovits_api import SoVITS  # 封装的GPT-SoVITS TTS模块
import soundfile as sf  # SoundFile库，用于读取WAV文件
from vad_recorder import VADRecorder  # 自定义VADRecorder模块，用于VAD录音
from openai import OpenAI
import config

# === LLM接口配置 ===
# DeepSeek接口地址和API Key（可通过环境变量配置）
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", config.deepseek_api_key)
# 在模块顶端初始化
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

# 实例化TTS引擎，base_url为本地TTS服务地址，speaker_name可做个性化扩展
tts_engine = SoVITS(base_url="http://localhost:9880")


def transcribe_audio(wav_file, model):
    """
    使用FunASR模型进行语音识别。
    :param wav_file: 待识别的WAV文件路径
    :param model: SenseVoiceSmall模型实例
    :return: 转写后的文本字符串
    """
    t1 = time.time()
    # 调用模型，返回原始转写结果列表
    res = model([wav_file], language="zh", use_itn=True)
    # 后处理清洗文本
    transcription = [rich_transcription_postprocess(i) for i in res]
    print(f"ASR耗时: {time.time() - t1:.2f} 秒")
    return transcription[0]


def dp_chat_ollama(message: str):
    """
    调用本地Ollama LLM生成回复。
    :param message: 用户输入文本
    :return: LLM生成的回复文本
    """
    global conversation_history
    t1 = time.time()
    # 将用户消息加入对话历史
    conversation_history.append({"role": "user", "content": message})
    # 构造请求负载
    payload = {"model": "qwen2.5", "messages": conversation_history}
    # 发送HTTP请求到本地Ollama服务
    response = requests.post("http://localhost:11434/api/chat", json=payload)
    resp_json = response.json()
    # 提取回复文本
    assistant_response = resp_json.get("message", {}).get("content", "")
    print(f"Ollama响应时间: {time.time() - t1:.2f} 秒")
    # 保存助手回复到对话历史
    conversation_history.append({"role": "assistant", "content": assistant_response})
    return assistant_response

# 废弃版本
# def dp_chat_deepseek(message: str):
#     """
#     调用DeepSeek LLM接口生成回复。
#     :param message: 用户输入文本
#     :return: LLM生成的回复文本
#     """
#     global conversation_history
#     t1 = time.time()
#     conversation_history.append({"role": "user", "content": message})
#     headers = {"Authorization": f"Bearer {deepseek_api_key}", "Content-Type": "application/json"}
#     payload = {"messages": conversation_history}
#     # 发送请求到DeepSeek服务
#     response = requests.post(deepseek_api_url, headers=headers, json=payload)
#     if response.status_code == 200:
#         resp_json = response.json()
#         assistant_response = resp_json.get("choices", [])[0].get("message", {}).get("content", "")
#     else:
#         print(f"DeepSeek API 错误: {response.status_code}")
#         assistant_response = "对不起，DeepSeek 服务暂不可用。"
#     print(f"DeepSeek响应时间: {time.time() - t1:.2f} 秒")
#     conversation_history.append({"role": "assistant", "content": assistant_response})
#     return assistant_response


def dp_chat_deepseek(message: str, stream=True):
    """
    使用 DeepSeek 接口进行聊天，支持流式输出。
    :param message: 用户输入文本
    :param stream: 是否启用流式模式
    :return: 回复文本
    """
    global conversation_history
    conversation_history.append({"role": "user", "content": message})

    if stream:
        # 流式模式
        reply = ""
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=conversation_history,
            stream=True
        )
        print("AI:")
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                reply += delta.content
        print()  # 输出换行
    else:
        # 非流式
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=conversation_history,
            stream=False
        )
        reply = response.choices[0].message.content
        print(reply)

    conversation_history.append({"role": "assistant", "content": reply})
    return reply

def dp_chat(message: str, use_deepseek=False, stream=True):
    """
    根据use_deepseek标志选择LLM，然后调用TTS播放回复。
    :param message: 用户输入文本
    :param use_deepseek: True使用DeepSeek，否则使用Ollama
    :param stream: 流式输出LLM响应默认流式
    :return: 回复文本
    """
    if use_deepseek:
         # DeepSeek支持流式和非流式
        reply = dp_chat_deepseek(message, stream=stream)
    else:
        # Ollama默认非流式，可扩展为流式
        reply = dp_chat_ollama(message)
    # 调用TTS引擎朗读回复
    tts_engine.speak(reply)
    return reply


def play_audio(file_path):
    """
    播放本地WAV音频。
    :param file_path: 音频文件路径
    """
    data, samplerate = sf.read(file_path, dtype='float32')
    sd.play(data, samplerate)
    sd.wait()


def continuous_conversation(model, recorder, use_deepseek=False, sleep_time=30):
    """
    连续对话主循环：
      1. VAD录音 -> 2. ASR转写 -> 3. LLM对话 -> 4. TTS播报
    :param model: ASR模型实例
    :param recorder: VADRecorder实例，用于录音
    :param use_deepseek: 是否使用DeepSeek
    :param sleep_time: 超时未检测到语音时结束对话（秒）
    """
    while True:
        audio_file = "input.wav"
        start = time.time()
        # 录制并获取音频文件路径
        recorded = recorder.record(output_file=audio_file)
        if not recorded:
            print("未检测到有效语音，重试...")
            continue
        # 超时退出检查
        if time.time() - start > sleep_time:
            play_audio("E:/vscode_project/py_stu_code/my_voice_assistant/睡眠音频/sleep.wav")
            break
        # 语音识别
        text = transcribe_audio(f"E:/vscode_project/py_stu_code/{recorded}", model)
        # 用户退出指令检测
        if text.lower() in ['退出', '结束对话', 'exit', 'quit']:
            print("对话结束")
            break
        print("User:", text)
        # LLM对话并TTS播放
        response = dp_chat(text, use_deepseek)
        # print("Assistant:", response)


def save_conversation_history():
    """
    将对话历史保存为JSON文件。
    """
    os.makedirs("conversation_logs", exist_ok=True)
    fname = datetime.now().strftime("conversation_%Y%m%d_%H%M%S.json")
    with open(os.path.join("conversation_logs", fname), 'w', encoding='utf-8') as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=2)
    print(f"对话记录已保存: {fname}")


def start_service(use_deepseek=False):
    """
    初始化ASR模型和VADRecorder，取消唤醒词检测，直接进入对话。
    :param use_deepseek: 启用DeepSeek LLM
    """
    print("Initializing ASR model...")
    # 加载ASR模型，quantize可加速但略有精度损失
    model = SenseVoiceSmall(model_dir, batch_size=10, quantize=False)
    # 初始化VAD Recorder
    recorder = VADRecorder(sample_rate=sample_rate, frame_duration=frame_duration,
                           max_silence=1.5, min_speech=0.5)
    print("开始对话，可直接说话...")
    try:
        continuous_conversation(model, recorder, use_deepseek)
    except KeyboardInterrupt:
        print("服务手动停止")
    finally:
        save_conversation_history()


if __name__ == "__main__":
    # 全局配置

    # ASR模型目录
    model_dir = config.model_dir
    sample_rate = 16000  # 音频采样率，需与ASR模型一致
    frame_duration = 30  # 单帧时长（毫秒）

    # 初始对话历史，用于系统角色指令
    settings = config.settings
    conversation_history = [{"role": "system", "content": f"你是...{settings}"}]

    # 启动语音助手，use_deepseek=True则使用DeepSeek LLM
    start_service(use_deepseek=True)