import os
import yaml
import logging
from aiohttp import web
from core.utils.util import get_project_dir
from config.private_config import PrivateConfig

logger = logging.getLogger(__name__)

class ConfigHandler:
    def __init__(self):
        self.private_config_path = get_project_dir() + 'data/.private_config.yaml'
        self.config_path = get_project_dir() + 'config.yaml'
        # 如果存在.config.yaml文件，则使用该文件
        if os.path.exists(get_project_dir() + "data/.config.yaml"):
            self.config_path = get_project_dir() + "data/.config.yaml"
        with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

    async def get_module_options(self, request):
        """Get all available module options from config.yaml"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Extract available modules
            modules = {
                'LLM': list(config.get('LLM', {}).keys()),
                'TTS': list(config.get('TTS', {}).keys()),
                'VAD': list(config.get('VAD', {}).keys()),
                'ASR': list(config.get('ASR', {}).keys())
            }
            
            return web.json_response({
                'success': True,
                'data': modules,
                'message': '获取成功'
            })

        except Exception as e:
            logger.error(f"Error getting module options: {str(e)}", exc_info=True)
            return web.json_response({
                'success': False,
                'message': '获取配置选项失败'
            })

    async def get_private_configs(self, request):
        """获取所有私有配置设备列表及其配置"""
        try:
            if os.path.exists(self.private_config_path):
                with open(self.private_config_path, 'r', encoding='utf-8') as f:
                    all_configs = yaml.safe_load(f) or {}
            else:
                all_configs = {}

            # 转换配置为前端友好的格式
            devices = []
            for device_id, config in all_configs.items():
                device_info = {
                    'id': device_id,
                    'config': {
                        'selected_module': config.get('selected_module', {}),
                        'prompt': config.get('prompt', ''),
                        'last_chat_time': config.get('last_chat_time', ''),
                        'nickname': config.get('nickname', '小智'),
                        'modules': {
                            'LLM': config.get('LLM', {}),
                            'TTS': config.get('TTS', {}),
                            'ASR': config.get('ASR', {}),
                            'VAD': config.get('VAD', {})
                        }
                    }
                }
                devices.append(device_info)

            return web.json_response({
                'success': True,
                'data': devices,
                'message': '获取成功'
            })

        except Exception as e:
            logger.error(f"Error getting private configs: {str(e)}", exc_info=True)
            return web.json_response({
                'success': False,
                'message': '获取配置失败'
            })

    async def save_device_config(self, request):
        """保存单个设备的配置"""
        try:
            data = await request.json()
            device_id = data.get('id')
            config = data.get('config')
            logger.info(f"Device config updated: {device_id} :\n{config}")
            if not device_id or not config:
                return web.json_response({
                    'success': False,
                    'message': '设备ID和配置不能为空'
                })

            # 使用PrivateConfig处理配置保存
            private_config = PrivateConfig(device_id, self.config)
            await private_config.load_or_create()
            
            success = await private_config.update_config(
                config.get('selected_module'),
                config.get('prompt'),
                config.get('nickname', '小智')
            )
            

            if not success:
                raise Exception("Failed to update device config")

            return web.json_response({
                'success': True,
                'message': '保存成功'
            })

        except Exception as e:
            logger.error(f"Error saving device config: {str(e)}", exc_info=True)
            return web.json_response({
                'success': False,
                'message': f'保存配置失败: {str(e)}'
            })

    async def delete_device_config(self, request):
        """删除设备配置"""
        try:
            data = await request.json()
            device_id = data.get('device_id')
            
            # 使用PrivateConfig处理配置删除
            private_config = PrivateConfig(device_id, self.config)
            success = await private_config.delete_config()

            if not success:
                raise Exception("Failed to delete device config")

            return web.json_response({
                'success': True,
                'message': '删除成功'
            })

        except Exception as e:
            logger.error(f"Error deleting device config: {str(e)}", exc_info=True)
            return web.json_response({
                'success': False,
                'message': f'删除配置失败: {str(e)}'
            })
