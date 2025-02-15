import os
import sys
import logging
from aiohttp import web
from aiohttp_cors import setup as cors_setup, ResourceOptions
from core.utils.util import get_local_ip

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from manager.api.login import LoginHandler
from manager.api.register import RegisterHandler
from manager.user_manager import UserManager
from manager.api.config import ConfigHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebUI:
    def __init__(self):
        self.app = web.Application()
        self.user_manager = UserManager()
        
        # 添加静态文件路径
        self.static_path = os.path.join(root_dir, 'manager', 'static', 'webui')
        
        # 创建配置字典
        self.config = {
            'users': self.user_manager.get_users(),
            'hash_password': self.user_manager.hash_password,
            'save_user_data': self.user_manager.save_user_data,
            'get_user': self.user_manager.get_user,
            'update_user': self.user_manager.update_user
        }
        
        self.setup_routes()
        self.setup_cors()

    def setup_cors(self):
        """设置CORS"""
        cors = cors_setup(self.app, defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)

    def setup_routes(self):
        """设置路由"""
        login_handler = LoginHandler(self.config)
        register_handler = RegisterHandler(self.config)
        config_handler = ConfigHandler()
        
        # API 路由
        self.app.router.add_post('/api/login', login_handler.handle_login)
        self.app.router.add_post('/api/register', register_handler.handle_register)
        self.app.router.add_get('/api/config/devices', config_handler.get_private_configs)
        self.app.router.add_post('/api/config/device', config_handler.save_device_config)
        self.app.router.add_get('/api/config/module-options', config_handler.get_module_options)
        self.app.router.add_post('/api/config/save_device_config', config_handler.save_device_config)
        self.app.router.add_post('/api/config/delete_device', config_handler.delete_device_config)

        # 添加静态文件服务
        self.app.router.add_static('/assets/', path=os.path.join(self.static_path, 'assets'))
        # 所有未匹配的路由都返回 index.html
        self.app.router.add_get('/{tail:.*}', self.handle_static_files)

    async def handle_static_files(self, request):
        """处理静态文件请求，支持SPA前端路由"""
        index_file = os.path.join(self.static_path, 'index.html')
        if os.path.exists(index_file):
            return web.FileResponse(index_file)
        return web.Response(status=404, text='Not found')

    def run(self, host='0.0.0.0', port=8002):
        """运行服务器"""
        local_ip = get_local_ip()
        logger.info(f"WebUI server is running at http://{local_ip}:{port}")
        web.run_app(self.app, host=host, port=port)

if __name__ == '__main__':
    webui = WebUI()
    webui.run()
