from openai import AsyncOpenAI

from src.eval.agents.agent import AgentResult, AgentRequest
from src.eval.agents.openai_agent import OpenAIAgent


class VanillaOpenAIAgent(OpenAIAgent):
    def __init__(self):
        super().__init__("gpt-4-1106-preview", "openai-gpt-4", 128000)
        self.client = AsyncOpenAI()
        self.name = 'vanilla'

    async def run(self, agent_request: AgentRequest) -> AgentResult:
        tool_calls = await self._run_tool_calls_loop(agent_request.env, [
            {
                "role": "user",
                "content": agent_request.user_prompt
            }
        ])

        return AgentResult(None, tool_calls)
