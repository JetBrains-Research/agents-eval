from planning_library.action_executors import LangchainActionExecutor
from planning_library.strategies import TreeOfThoughtsDFSStrategy, BaseCustomStrategy
from planning_library.strategies.tot_dfs.components import ThoughtEvaluator, ThoughtGenerator

from src.eval.agents.langchain_strategic_agent import LangchainStrategicAgent
from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.tree_of_thoughts_prompt import TreeOfThoughtsPrompt


class TreeOfThoughtsAgent(LangchainStrategicAgent):
    name = "thee_of_thoughts"

    def __init__(self,
                 name: str,
                 model_name: str,
                 temperature: int,
                 model_kwargs: dict,
                 value_threshold: float,
                 max_num_thoughts: int,
                 max_num_steps: int,
                 prompt: TreeOfThoughtsPrompt):
        super().__init__(name)
        self._model_name = model_name
        self._temperature = temperature
        self._model_kwargs = model_kwargs
        self._value_threshold = value_threshold
        self._max_num_thoughts = max_num_thoughts
        self._max_num_steps = max_num_steps
        self._prompt = prompt

    async def _create_strategy(self) -> BaseCustomStrategy:
        action_executor = LangchainActionExecutor(tools=self.tools, meta_tools=self.meta_tools)

        thought_evaluator = ThoughtEvaluator.create(
            llm=create_chat(self._model_name, self._temperature, self._model_kwargs),
            user_message=self._prompt.thought_evaluator_prompt(),
            threshold=self._value_threshold,
            parser_name="openai-tools",
        )

        thought_generator = ThoughtGenerator.create(
            llm=create_chat(self._model_name, self._temperature, self._model_kwargs),
            tools=self.tools,
            user_message=self._prompt.thought_generator_prompt(),
            max_num_thoughts=self._max_num_thoughts,
            parser_name="openai-tools",
        )

        strategy_executor = TreeOfThoughtsDFSStrategy(
            action_executor=action_executor,
            max_iterations=self._max_num_steps,
            return_intermediate_steps=True,
            thought_generator=thought_generator,
            thought_evaluator=thought_evaluator,
            do_sorting=False,
        )

        return strategy_executor
