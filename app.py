import asyncio
from config.logger import setup_logging
from config.settings import load_config
from core.websocket_server import WebSocketServer
from manager.http_server import ConfigServer
from core.webui import WebUI
from aiohttp import web
from core.utils.util import get_local_ip

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
    
    # 启动 WebUI 服务器
    webui_runner = None
    try:
        webui = WebUI()
        runner = web.AppRunner(webui.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8002)
        await site.start()
        webui_runner = runner
        local_ip = get_local_ip()
        print(f"WebUI server is running at http://{local_ip}:8002")
    except Exception as e:
        print(f"Failed to start WebUI server: {e}")
    
    try:
        # 等待 WebSocket 服务器运行
        await ws_task
    finally:
        # 清理 HTTP 服务器
        if http_runner:
            await http_runner.cleanup()
        # 清理 WebUI 服务器
        if webui_runner:
            await webui_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
