from planning_library.action_executors import LangchainActionExecutor
from planning_library.strategies import TreeOfThoughtsDFSStrategy, BaseCustomStrategy
from planning_library.strategies.tot_dfs.components import ThoughtEvaluator, ThoughtGenerator

from src.eval.agents.langchain_stategic_agent import LangchainStrategicAgent
from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.tree_of_thoughts_prompt import TreeOfThoughtsPrompt


class TreeOfThoughtsAgent(LangchainStrategicAgent):

    def __init__(self,
                 prompt: TreeOfThoughtsPrompt,
                 model_name: str,
                 temperature: int,
                 model_kwargs: dict,
                 value_threshold: float,
                 max_num_thoughts: int,
                 max_num_steps: int):
        super().__init__()
        self.prompt = prompt
        self.model_name = model_name
        self.temperature = temperature
        self.model_kwargs = model_kwargs
        self.value_threshold = value_threshold
        self.max_num_thoughts = max_num_thoughts
        self.max_num_steps = max_num_steps

    async def _create_strategy(self) -> BaseCustomStrategy:
        action_executor = LangchainActionExecutor(tools=self.tools,
                                                  meta_tools=self.meta_tools)

        thought_evaluator = ThoughtEvaluator.create(
            llm=create_chat(self.model_name, self.temperature, self.model_kwargs),
            user_message=self.prompt.thought_evaluator_message(),
            threshold=self.value_threshold,
            parser_name="openai-tools",
        )

        thought_generator = ThoughtGenerator.create(
            llm=create_chat(self.model_name, self.temperature, self.model_kwargs),
            tools=self.tools,
            parser_name="openai-tools",
            user_message=self.prompt.thought_generator_message(),
            max_num_thoughts=self.max_num_thoughts)

        strategy_executor = TreeOfThoughtsDFSStrategy(
            action_executor=action_executor,
            max_iterations=self.max_num_steps,
            return_intermediate_steps=True,
            thought_generator=thought_generator,
            thought_evaluator=thought_evaluator,
            do_sorting=False,
        )

        return strategy_executor
