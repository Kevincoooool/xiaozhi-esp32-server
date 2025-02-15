import asyncio
from config.logger import setup_logging
from config.settings import load_config
from core.server import WebSocketServer
from core.http_server import ConfigServer

async def main():
    setup_logging()  # 最先初始化日志
    config = load_config()
    
    # 启动 WebSocket 服务器
    ws_server = WebSocketServer(config)
    ws_task = asyncio.create_task(ws_server.start())
    
    # 启动 HTTP 配置服务器
    http_runner = None
    if config['manager'].get('enabled', False):
        config_server = ConfigServer(config)
        try:
            http_runner = await config_server.start()
        except Exception as e:
            print(f"Failed to start HTTP server: {e}")
    
    try:
        # 等待 WebSocket 服务器运行
        await ws_task
    finally:
        # 清理 HTTP 服务器
        if http_runner:
            await http_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
