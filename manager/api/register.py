import logging
from aiohttp import web
import datetime

logger = logging.getLogger(__name__)

class RegisterHandler:
    def __init__(self, config):
        self.config = config

    async def handle_register(self, request):
        """处理注册请求"""
        try:
            data = await request.json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                logger.warning(f"Registration attempt with empty credentials from {request.remote}")
                return web.json_response({
                    'success': False, 
                    'message': '用户名和密码不能为空'
                })

            users = self.config.get('users', {})
            if username in users:
                logger.warning(f"Registration attempt with existing username {username} from {request.remote}")
                return web.json_response({
                    'success': False, 
                    'message': '用户名已存在'
                })

            # 存储新用户
            self.config['users'][username] = {
                'password': self.config['hash_password'](password),
                'created_at': datetime.datetime.now().isoformat()
            }
            self.config['save_user_data']()

            logger.info(f"Successfully registered new user {username} from {request.remote}")
            return web.json_response({
                'success': True, 
                'message': '注册成功'
            })

        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            return web.json_response({
                'success': False, 
                'message': '注册失败，请稍后重试'
            })
