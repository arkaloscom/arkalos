from typing import Any, Literal
from abc import ABC, abstractmethod

from ollama import AsyncClient

from arkalos import config

from arkalos.core.logger import log as Log


from openai import OpenAI


class AIAction(ABC):

    NAME: str
    DESCRIPTION: str
    
    @abstractmethod
    async def run(self, message: str) -> Any:
        pass

    async def generateTextResponse(self, prompt: str, ai_conf_name: str|None = None) -> str:

        if ai_conf_name is None:
            ai_conf_name = config('ai.use', 'ollama/qwen2.5-coder')

        ai_conf = config('ai.configurations')[ai_conf_name]
        use_ai_provider = ai_conf['provider']
        use_ai_model = ai_conf['model']
        Log.debug(f'Using AI configuration "{ai_conf_name}"')
        if use_ai_provider == 'deepseek':
            oai_client = OpenAI(api_key=ai_conf['api_key'], base_url="https://api.deepseek.com")
            response = oai_client.chat.completions.create(
                model=use_ai_model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            if response.choices[0].message.content:
                return response.choices[0].message.content
            raise Exception('AIAction.generateTextResponse: response content not found')
        else:
            ollama_client = AsyncClient(host='http://127.0.0.1:11434', timeout=25)
            ollama_response = await ollama_client.generate(model=use_ai_model, prompt=prompt)
            return ollama_response["response"].strip()

