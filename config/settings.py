import os
import argparse
from ruamel.yaml import YAML
from core.utils.util import read_config, get_project_dir


def get_config_file():
    default_config_file = "config.yaml"
    # 判断是否存在私有的配置文件
    if os.path.exists(get_project_dir() + "data/." + default_config_file):
        default_config_file = "data/." + default_config_file
    return default_config_file


def load_config():
    """加载配置文件"""
    parser = argparse.ArgumentParser(description="Server configuration")
    default_config_file = get_config_file()
    parser.add_argument("--config_path", type=str, default=default_config_file)
    args = parser.parse_args()
    return read_config(args.config_path)


def update_config(config):
    yaml = YAML()
    yaml.preserve_quotes = True
    """将配置保存到YAML文件"""
    with open(get_config_file(), 'w') as f:
        yaml.dump(config, f)
