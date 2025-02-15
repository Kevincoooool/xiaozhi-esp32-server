import logging
from aiohttp import web
from manager.api.auth import verify_token
from manager.api.response import response_unauthorized, response_success, response_error

logger = logging.getLogger(__name__)


class PromptApi:
    def __init__(self, config):
        self.config = config

    async def get_prompt(self, request):
        if not await verify_token(self.config, request):
            return response_unauthorized()

        return web.json_response({
            'prompt': self.config['prompt'],
            'Access-Control-Allow-Origin': '*'
        })

    async def update_prompt(self, request):
        if not await verify_token(self.config, request):
            return response_unauthorized()

        try:
            data = await request.json()
            if 'prompt' not in data:
                return response_success()

            self.config['prompt'] = data['prompt']
            return response_success()

        except Exception as e:
            logger.error(f"Failed to update prompt: {e}")
            return response_error(str(e))
