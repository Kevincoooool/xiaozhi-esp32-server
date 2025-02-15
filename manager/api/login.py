import logging
from aiohttp import web
import datetime

logger = logging.getLogger(__name__)

class LoginHandler:
    def __init__(self, config):
        self.config = config

    async def handle_login(self, request):
        """处理登录请求"""
        try:
            data = await request.json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                logger.warning(f"Login attempt with empty credentials from {request.remote}")
                return web.json_response({
                    'success': False, 
                    'message': '用户名和密码不能为空'
                })

            stored_user = self.config['get_user'](username)
            if not stored_user or stored_user['password'] != self.config['hash_password'](password):
                logger.warning(f"Failed login attempt for user {username} from {request.remote}")
                return web.json_response({
                    'success': False, 
                    'message': '用户名或密码错误'
                })

            # 更新最后登录时间
            self.config['update_user'](username, {
                'last_login': datetime.datetime.now().isoformat()
            })

            logger.info(f"Successful login for user {username} from {request.remote}")
            return web.json_response({
                'success': True, 
                'message': '登录成功'
            })

        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return web.json_response({
                'success': False, 
                'message': '登录失败，请稍后重试'
            })
