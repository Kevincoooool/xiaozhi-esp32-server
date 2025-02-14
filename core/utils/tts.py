import asyncio
import logging
import os
import json
import uuid
import base64
from datetime import datetime
import edge_tts
import numpy as np
import opuslib
import requests
from core.utils.util import read_config, get_project_dir
from pydub import AudioSegment
from abc import ABC, abstractmethod
from pydub.utils import which
AudioSegment.ffmpeg = which("ffmpeg")
logger = logging.getLogger(__name__)


class TTS(ABC):
    def __init__(self, config, delete_audio_file):
        self.delete_audio_file = delete_audio_file
        self.output_file = config.get("output_file")

    @abstractmethod
    def generate_filename(self):
        pass

    def to_tts(self, text):
        logger.info(f"语音生成: {text}")
        tmp_file = self.generate_filename()
        try:
            # max_repeat_time = 5
            # while not os.path.exists(tmp_file) and max_repeat_time > 0:
            #     asyncio.run(self.text_to_speak(text, tmp_file))
            #     if not os.path.exists(tmp_file):
            #         max_repeat_time = max_repeat_time - 1
            #         logger.error(f"语音生成失败: {text}:{tmp_file}，再试{max_repeat_time}次")
            asyncio.run(self.text_to_speak(text, tmp_file))
            return tmp_file
        except Exception as e:
            logger.info(f"Failed to generate TTS file: {e}")
            return None

    @abstractmethod
    async def text_to_speak(self, text, output_file):
        pass

    def wav_to_opus_data(self, wav_file_path):
        # 使用pydub加载PCM文件
        # 获取文件后缀名
        file_type = os.path.splitext(wav_file_path)[1]
        if file_type:
            file_type = file_type.lstrip('.')
        audio = AudioSegment.from_file(wav_file_path, format=file_type)

        duration = len(audio) / 1000.0

        # 转换为单声道和16kHz采样率（确保与编码器匹配）
        audio = audio.set_channels(1).set_frame_rate(16000)

        # 获取原始PCM数据（16位小端）
        raw_data = audio.raw_data

        # 初始化Opus编码器
        encoder = opuslib.Encoder(16000, 1, opuslib.APPLICATION_AUDIO)

        # 编码参数
        frame_duration = 60  # 60ms per frame
        frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

        opus_datas = []
        # 按帧处理所有音频数据（包括最后一帧可能补零）
        for i in range(0, len(raw_data), frame_size * 2):  # 16bit=2bytes/sample
            # 获取当前帧的二进制数据
            chunk = raw_data[i:i + frame_size * 2]

            # 如果最后一帧不足，补零
            if len(chunk) < frame_size * 2:
                chunk += b'\x00' * (frame_size * 2 - len(chunk))

            # 转换为numpy数组处理
            np_frame = np.frombuffer(chunk, dtype=np.int16)

            # 编码Opus数据
            opus_data = encoder.encode(np_frame.tobytes(), frame_size)
            opus_datas.append(opus_data)

        return opus_datas, duration


class EdgeTTS(TTS):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.voice = config.get("voice")

    def generate_filename(self, extension=".mp3"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, text, output_file):
        communicate = edge_tts.Communicate(text, voice=self.voice)  # Use your preferred voice
        await communicate.save(output_file)


class DoubaoTTS(TTS):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.appid = config.get("appid")
        self.access_token = config.get("access_token")
        self.cluster = config.get("cluster")
        self.voice = config.get("voice")

        self.host = "openspeech.bytedance.com"
        self.api_url = f"https://{self.host}/api/v1/tts"
        self.header = {"Authorization": f"Bearer;{self.access_token}"}

    def generate_filename(self, extension=".wav"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, text, output_file):
        request_json = {
            "app": {
                "appid": self.appid,
                "token": "access_token",
                "cluster": self.cluster
            },
            "user": {
                "uid": "1"
            },
            "audio": {
                "voice_type": self.voice,
                "encoding": "wav",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson"
            }
        }

        resp = requests.post(self.api_url, json.dumps(request_json), headers=self.header)
        if "data" in resp.json():
            data = resp.json()["data"]
            file_to_save = open(output_file, "wb")
            file_to_save.write(base64.b64decode(data))


class GPT_SoVITS_V2(TTS):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.url = config.get("url", "http://127.0.0.1:9880/tts")
        self.text_lang = config.get("text_lang", "zh")
        self.ref_audio_path = config.get("ref_audio_path")
        self.prompt_text = config.get("prompt_text")
        self.prompt_lang = config.get("prompt_lang", "zh")
        self.top_k = config.get("top_k", 5)
        self.top_p = config.get("top_p", 1)
        self.temperature = config.get("temperature", 1)
        self.text_split_method = config.get("text_split_method", "cut0")
        self.batch_size = config.get("batch_size", 1)
        self.batch_threshold = config.get("batch_threshold", 0.75)
        self.split_bucket = config.get("split_bucket", True)
        self.return_fragment = config.get("return_fragment", False)
        self.speed_factor = config.get("speed_factor", 1.0)
        self.streaming_mode = config.get("streaming_mode", False)
        self.seed = config.get("seed", -1)
        self.parallel_infer = config.get("parallel_infer", True)
        self.repetition_penalty = config.get("repetition_penalty", 1.35)
        self.aux_ref_audio_paths = config.get("aux_ref_audio_paths", [])

    def generate_filename(self, extension=".wav"):
        return os.path.join(self.output_file, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}{extension}")

    async def text_to_speak(self, text, output_file):
        request_json = {
            "text": text,
            "text_lang": self.text_lang,
            "ref_audio_path": self.ref_audio_path,
            "aux_ref_audio_paths": self.aux_ref_audio_paths,
            "prompt_text": self.prompt_text,
            "prompt_lang": self.prompt_lang,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "text_split_method": self.text_split_method,
            "batch_size": self.batch_size,
            "batch_threshold": self.batch_threshold,
            "split_bucket": self.split_bucket,
            "return_fragment": self.return_fragment,
            "speed_factor": self.speed_factor,
            "streaming_mode": self.streaming_mode,
            "seed": self.seed,
            "parallel_infer": self.parallel_infer,
            "repetition_penalty": self.repetition_penalty
        }

        resp = requests.post(self.url, json=request_json)
        if resp.status_code == 200:
            with open(output_file, "wb") as file:
                file.write(resp.content)
        else:
            logger.error(f"GPT_SoVITS_V2 TTS请求失败: {resp.status_code} - {resp.text}")


def create_instance(class_name, *args, **kwargs):
    cls_map = {
        "DoubaoTTS": DoubaoTTS,
        "EdgeTTS": EdgeTTS,
        "GPT_SoVITS_V2": GPT_SoVITS_V2,
        # 可扩展其他TTS实现
    }

    if cls := cls_map.get(class_name):
        return cls(*args, **kwargs)
    raise ValueError(f"不支持的TTS类型: {class_name}")


if __name__ == "__main__":
    """
      响应速度测试
    """
    config = read_config(get_project_dir() + "config.yaml")
    tts = create_instance(
        config["selected_module"]["TTS"],
        config["TTS"][config["selected_module"]["TTS"]],
        config["delete_audio"]
    )
    tts.output_file = get_project_dir() + tts.output_file
    start = datetime.now()
    file_path = tts.to_tts("你好，测试,我是人工智能小智")
    print("语音合成耗时：" + str(datetime.now() - start))
    start = datetime.now()
    tts.wav_to_opus_data(file_path)
    print("语音opus耗时：" + str(datetime.now() - start))
