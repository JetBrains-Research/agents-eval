from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI

from src.eval.agents.base_agent import BaseAgent
from src.eval.agents.utils.tokenization_utils import TokenizationUtils
from src.eval.envs.base_env import BaseEnv
from src.eval.prompts.few_shot_prompt import FewShotPrompt


class FewShotAgent(BaseAgent):

    def __init__(self, name: str, model_name: str, temperature: int, model_kwargs: dict, prompt: FewShotPrompt):
        super().__init__(name)
        self._model_name = model_name
        self._temperature = temperature
        self._model_kwargs = model_kwargs
        self._prompt = prompt

    async def run(self, env: BaseEnv, user_prompt: str, **kwargs):
        execution_prompt = await self._prompt.execution_prompt()
        input_messages = [
            {
                "role": "system",
                "content": execution_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        #
        # tokenization_utils = TokenizationUtils(self._model_name)
        #
        # client = AsyncOpenAI()
        # chat_response = await client.chat.completions.create(
        #     model=self._model_name,
        #     messages=tokenization_utils.truncate(input_messages),
        #     temperature=self._temperature,
        #     **self._model_kwargs
        # )

        # description = chat_response.choices[0].message.content

        model = ChatOpenAI(model_name=self._model_name, temperature=self._temperature, model_kwargs=self._model_kwargs)

        description = model.invoke(execution_prompt + user_prompt).content

        await env.run_command('create_template', {'description': description})

        return {
            "input": input_messages,
            "output": description,
            "intermediate_steps": []
        }
