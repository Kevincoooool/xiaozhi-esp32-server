import logging
import sys
import os


def setup_logging(log_dir='tmp', data_dir='data'):
    """配置全局日志"""
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(log_dir, "server.log"), encoding='utf-8')
        ],
        force=True
    )
    return logging.getLogger(__name__)
