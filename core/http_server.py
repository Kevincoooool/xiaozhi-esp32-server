import logging
import os
from aiohttp import web
from core.utils.util import get_local_ip, get_project_dir, check_password
from manager.api.prompt import PromptApi
from manager.api.auth import AuthApi
from aiohttp.web_middlewares import middleware

logger = logging.getLogger(__name__)


@middleware
async def cors_middleware(request, handler):
    # 预检请求处理
    if request.method == 'OPTIONS':
        return web.Response(
            status=204,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Token',
                'Access-Control-Max-Age': '86400',
            }
        )

    try:
        response = await handler(request)
    except web.HTTPException as ex:
        response = ex

    # 添加CORS头到所有响应
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Expose-Headers': 'Content-Type, Authorization, Token',
        'Vary': 'Origin'  # 避免缓存问题
    }
    response.headers.update(cors_headers)

    return response


class ConfigServer:
    def __init__(self, config: dict):
        self.config = config
        self.app = web.Application(middlewares=[cors_middleware])  # 注册中间件

        # 初始化接口处理器
        self.prompt_handler = PromptApi(config)
        self.auth_handler = AuthApi(config)
        self.setup_routes()

    def setup_routes(self):
        # 注册prompt接口
        self.app.router.add_get('/api/prompt', self.prompt_handler.get_prompt)
        self.app.router.add_post('/api/prompt', self.prompt_handler.update_prompt)

        # 注册auth接口
        self.app.router.add_post('/api/login', self.auth_handler.login)

        # 注册静态文件路由
        static_dir = os.path.join(get_project_dir(), 'manager/static')  # 获取static目录绝对路径
        self.app.router.add_static(
            prefix='/manager/',  # 匹配前缀
            path=static_dir,  # 静态文件目录
            name='static'
        )
        self.app.router.add_get('/manager', self.redirect_to_index)

    async def redirect_to_index(self, _):
        raise web.HTTPFound('/manager/')

    async def start(self):
        try:
            http_config = self.config['manager']
            if not http_config.get('enabled', False):
                logger.info("HTTP server is disabled")
                return
            token = self.config['manager']['token']
            if not check_password(token):
                logger.info("您设置的后台密码太弱了，启动后台管理失败！")
                return

            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, http_config['ip'], http_config['port'])
            await site.start()
            logger.info(
                f"Config HTTP server is running at http://{get_local_ip()}:{http_config['port']}/manager/login.html")
            return runner  # 返回runner以便后续清理
        except Exception as e:
            logger.error(f"Failed to start HTTP server: {e}")
            raise
