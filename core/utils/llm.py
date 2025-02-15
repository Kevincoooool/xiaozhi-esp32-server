import os
import sys
import json
import logging
import openai
import requests
import importlib
from datetime import datetime
from core.utils.util import is_segment
from core.utils.util import get_string_no_punctuation_or_emoji
from core.utils.util import read_config, get_project_dir
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


def create_instance(class_name, *args, **kwargs):
    # 获取所有支持的LLM类型列表
    supported_llm_types = []
    llm_dir = os.path.join('core', 'providers', 'llm')
    if os.path.exists(llm_dir):
        for item in os.listdir(llm_dir):
            item_path = os.path.join(llm_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, f'{item}.py')):
                supported_llm_types.append(item)

    # 打印所有支持的LLM类型列表
    logger.info(f"所有支持的LLM类型列表: {supported_llm_types}")
    logger.info(f"您设置的llm: {class_name}")

    # 创建LLM实例
    if class_name in supported_llm_types:
        lib_name = f'core.providers.llm.{class_name}.{class_name}'
        if lib_name not in sys.modules:
            sys.modules[lib_name] = importlib.import_module(f'{lib_name}')
        # 打印实际用到的LLM类型
        logger.info(f"实际用到的LLM类型: {class_name}")
        return sys.modules[lib_name].LLMProvider(*args, **kwargs)

    raise ValueError(f"不支持的LLM类型: {class_name}，请检查该配置的type是否设置正确")



if __name__ == "__main__":
    """
      响应速度测试
    """
    config = read_config(get_project_dir() + "config.yaml")
    llm = create_instance(
        config["selected_module"]["LLM"]
        if not "type" in config["LLM"][config["selected_module"]["LLM"]]
        else
        config["LLM"][config["selected_module"]["LLM"]]["type"],
        config["LLM"][config["selected_module"]["LLM"]]
    )

    start_time = datetime.now()

    dialogue = []
    dialogue.append({"role": "system", "content": config.get("prompt")})
    dialogue.append({"role": "user", "content": "你好小智"})
    llm_responses = llm.response("test", dialogue)
    response_message = []
    first_text = None
    start = 0

    for content in llm_responses:
        response_message.append(content)

        if is_segment(response_message):
            segment_text = "".join(response_message[start:])
            segment_text = get_string_no_punctuation_or_emoji(segment_text)
            if len(segment_text) > 0:
                if first_text is None:
                    first_text = segment_text
                    print("大模型首次返回耗时：" + str(datetime.now() - start_time))
                start = len(response_message)

    print("大模型返回总耗时：" + str(datetime.now() - start_time))
