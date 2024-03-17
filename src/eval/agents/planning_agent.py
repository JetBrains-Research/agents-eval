import asyncio

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable, RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_tool

from src.eval.agents.langchain_agent import LangchainAgent
from src.eval.envs.env import Env
from src.eval.envs.http_env import HttpEnv
from template_generation.template_generation_prompts import get_planning_system_prompt, get_execution_system_prompt


class PlanningAgent(LangchainAgent):

    def __init__(self, env: Env):
        super().__init__(env)

    async def _create_agent_executor(self, user_prompt: str) -> AgentExecutor:
        planning_prompt = [
            SystemMessage(content=get_planning_system_prompt()),
            HumanMessage(content=user_prompt),
        ]

        plan = await self.chat.ainvoke(planning_prompt)
        print(f"Received plan:\n{plan.content}")

        execution_messages = [
            ("system", get_execution_system_prompt()),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            ("user", "{input}"),
            ("system", plan.content),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]

        execution_prompt = ChatPromptTemplate.from_messages(
            execution_messages
        )

        agent: RunnableSerializable = (
                RunnablePassthrough.assign(
                    agent_scratchpad=lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    )
                )
                | execution_prompt
                | self.chat.bind(tools=[convert_to_openai_tool(tool) for tool in self.tools])
                | OpenAIToolsAgentOutputParser()
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            return_intermediate_steps=True,
            max_iterations=50,
            early_stopping_method="force",
        )

        return agent_executor


async def main():
    env = HttpEnv('127.0.0.1', 5050)
    await env.init({'content_root_path': "/Users/Maria.Tigina/PycharmProjects/agents-eval-data/example"})
    agent = PlanningAgent(env)
    await agent.init(**{'model_name': 'gpt-3.5-turbo-1106', 'temperature': 0, 'model_kwargs': {'seed': 45}})
    print(await agent.run("Generate template for weather forcast python app with MIT License"))


if __name__ == '__main__':
    asyncio.run(main())
