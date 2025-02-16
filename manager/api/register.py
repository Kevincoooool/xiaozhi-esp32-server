import logging
from aiohttp import web
import datetime
from core.utils.util import check_password

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

            if not check_password(password):
                return web.json_response({
                    'success': False,
                    'message': '密码必须包含大小写字母、数字且长度至少8位'
                })

            if not username or not password:
                logger.warning(f"Registration attempt with empty credentials from {request.remote}")
                return web.json_response({
                    'success': False,
                    'message': '用户名和密码不能为空'
                })

            users = self.config.get('users', {})
            # 由于现在所有用户都能看到所有设备，从安全角度上考虑，只允许注册一个用户
            # 未来绑定设备功能完成后，再放开任意注册
            if len(users) >= 1:
                return web.json_response({
                    'success': False,
                    'message': '系统已经初始化过了，如果忘记了密码，请直接删除“.secrets.yaml”文件，删除后重启本服务'
                })

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
