
# 目前没什么用

import os
import soundfile as sf
import sounddevice as sd
import gpt_sovits_api  # 你自己的 GPT-SoVITS 推理模块

class TTS:
    def __init__(self, speaker_name="白子", emotion="正常", tts_engine="gpt_sovits"):
        """
        初始化TTS配置
        :param speaker_name: 说话人名称（用于区分不同音色或情感模型）
        :param emotion: 情绪标签（根据你的模型支持的情绪，如“正常”“抑郁”）
        :param tts_engine: 当前使用的TTS后端（这里只实现gpt_sovits）
        """
        self.speaker = speaker_name
        self.emotion = emotion
        self.engine = tts_engine

    def synthesize(self, text, output_file="output.wav"):
        """
        调用后端TTS模型合成语音
        :param text: 要朗读的文本内容
        :param output_file: 合成结果保存路径
        :return: 输出文件路径
        """
        if self.engine == "gpt_sovits":
            gpt_sovits_api.gpt_sovits(text, self.emotion, output_file)
            return output_file
        else:
            raise NotImplementedError("暂不支持的 TTS 引擎")

    def play(self, wav_path):
        """
        播放语音文件
        :param wav_path: 要播放的音频文件路径
        """
        if not os.path.exists(wav_path):
            print(f"音频文件不存在：{wav_path}")
            return

        data, samplerate = sf.read(wav_path, dtype='float32')
        sd.play(data, samplerate)
        sd.wait()

    def speak(self, text, output_file="output.wav"):
        """
        合成 + 播放 = 一句话说完
        """
        self.synthesize(text, output_file)
        self.play(output_file)

if __name__ == "__main__":
    tts = TTS(emotion="抑郁")  # 设置情绪和说话人
    tts.speak("博士，今天要做什么任务呢？")


