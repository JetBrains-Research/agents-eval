from openai import AsyncOpenAI

from src.eval.agents.agent import AgentResult, AgentRequest
from src.eval.agents.openai_agent import OpenAIAgent
from src.eval.agents.utils.openai_utils import DEFAULT_MODEL, DEFAULT_PROFILE_NAME, DEFAULT_MAX_TOKENS


class PlanningOpenAIAgent(OpenAIAgent):
    def __init__(self, model: str = DEFAULT_MODEL,
                 profile_name: str = DEFAULT_PROFILE_NAME,
                 max_tokens: int = DEFAULT_MAX_TOKENS):
        super().__init__(model, profile_name, max_tokens)

    async def run(self, agent_request: AgentRequest) -> AgentResult:
        plan = await self._run_request([
            {
                "role": "system",
                "content": agent_request.planning_system_prompt
            },
            {
                "role": "user",
                "content": agent_request.user_prompt
            }
        ])

        tool_calls = await self._run_tool_calls_loop(agent_request.env, [
            {
                "role": "system",
                "content": agent_request.execution_system_prompt
            },
            {
                "role": "user",
                "content": agent_request.user_prompt
            },
            {
                "role": "system",
                "content": plan,
            }
        ])

        return AgentResult(plan, tool_calls)
