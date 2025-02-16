import os
import yaml
import hashlib
import logging
from core.utils.util import get_project_dir

logger = logging.getLogger(__name__)


class UserManager:
    def __init__(self):
        self.secrets_path = get_project_dir() + 'data/.secrets.yaml'
        self.users = {}
        self.ensure_secrets_file()
        self.load_user_data()

    def ensure_secrets_file(self):
        """确保 .secrets.yaml 文件存在"""
        if not os.path.exists(self.secrets_path):
            default_config = {
                'users': {}
            }
            try:
                with open(self.secrets_path, 'w', encoding='utf-8') as f:
                    yaml.dump(default_config, f)
                os.chmod(self.secrets_path, 0o600)
                logger.info("Created new .secrets.yaml file")
            except Exception as e:
                logger.error(f"Failed to create .secrets.yaml: {e}")
                raise

    def load_user_data(self):
        """加载用户数据"""
        try:
            with open(self.secrets_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {'users': {}}
                self.users = data['users']
                logger.info("Successfully loaded user data")
        except Exception as e:
            logger.error(f"Failed to load user data: {e}")
            self.users = {}

    def save_user_data(self):
        """保存用户数据"""
        try:
            with open(self.secrets_path, 'w', encoding='utf-8') as f:
                yaml.dump({'users': self.users}, f)
            logger.info("Successfully saved user data")
        except Exception as e:
            logger.error(f"Failed to save user data: {e}")
            raise

    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_users(self):
        """获取所有用户"""
        return self.users

    def get_user(self, username):
        """获取指定用户"""
        return self.users.get(username)

    def update_user(self, username, data):
        """更新用户数据"""
        if username in self.users:
            self.users[username].update(data)
            self.save_user_data()
