from planning_library.action_executors import LangchainActionExecutor
from planning_library.strategies import BaseCustomStrategy, ADaPTStrategy
from planning_library.strategies.adapt.components import ADaPTPlanner, ADaPTExecutor

from src.eval.agents.langchain_strategic_agent import LangchainStrategicAgent
from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.adapt_prompt import ADaPTPrompt


class ADaPTAgent(LangchainStrategicAgent):
    name = "ADaPT"

    def __init__(self,
                 model_name: str,
                 temperature: int,
                 model_kwargs: dict,
                 max_depth: int,
                 executor_max_iterations: int,
                 prompt: ADaPTPrompt):
        super().__init__()
        self._prompt = prompt
        self._model_name = model_name
        self._temperature = temperature
        self._model_kwargs = model_kwargs
        self._max_depth = max_depth
        self._executor_max_iterations = executor_max_iterations

    async def _create_strategy(self) -> BaseCustomStrategy:
        action_executor = LangchainActionExecutor(tools=self.tools, meta_tools=self.meta_tools)

        executor = ADaPTExecutor.create_simple_strategy(
            llm=create_chat(self._model_name, self._temperature, self._model_kwargs),
            parser_name="openai-tools",
            user_message=self._prompt.executor_prompt(), max_iterations=self._executor_max_iterations,
            return_intermediate_steps=True,
            return_finish_log=True,
            action_executor=action_executor)

        # simple_planner = ADaPTPlanner.create_simple_planner(
        #     llm=create_chat(self.model_name, self.temperature, self.model_kwargs),
        #     user_message=self.prompt.simple_planner_prompt(),
        #     executor_parser_name="openai-tools"
        # )

        agent_planner = ADaPTPlanner.create_agent_planner(
            llm=create_chat(self._model_name, self._temperature, self._model_kwargs),
            parser_name="openai-tools",
            user_message=self._prompt.agent_planner_prompt(),
            executor_parser_name="openai-tools"
        )

        strategy_executor = ADaPTStrategy(
            executor=executor,
            planner=agent_planner,
            max_depth=self._max_depth,
            return_intermediate_steps=True,
            return_finish_log=True,
        )

        return strategy_executor
