from planning_library.action_executors import LangchainActionExecutor
from planning_library.strategies import BaseCustomStrategy, ReflexionStrategy
from planning_library.strategies.reflexion.components import ReflexionActor, ReflexionEvaluator, ReflexionSelfReflection

from src.eval.agents.langchain_stategic_agent import LangchainStrategicAgent
from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.reflexion_prompt import ReflexionPrompt


class ReflexionAgent(LangchainStrategicAgent):

    def __init__(self,
                 prompt: ReflexionPrompt,
                 model_name: str,
                 temperature: int,
                 model_kwargs: dict,
                 value_threshold: float,
                 max_num_iterations: int):
        super().__init__()
        self.prompt = prompt
        self.model_name = model_name
        self.temperature = temperature
        self.model_kwargs = model_kwargs
        self.value_threshold = value_threshold
        self.max_num_iterations = max_num_iterations

    async def _create_strategy(self) -> BaseCustomStrategy:
        action_executor = LangchainActionExecutor(self.tools, meta_tools=self.meta_tools)

        actor = ReflexionActor.create(
            llm=create_chat(self.model_name, self.temperature, self.model_kwargs),
            tools=self.tools,
            user_message=self.prompt.action_prompt(),
            parser_name="openai-tools",
        )

        evaluator = ReflexionEvaluator.create(
            llm=create_chat(self.model_name, self.temperature, self.model_kwargs),
            user_message=self.prompt.evaluator_prompt(),
            threshold=self.value_threshold,
            parser_name="openai-tools")

        self_reflection = ReflexionSelfReflection.create(
            llm=create_chat(self.model_name, self.temperature, self.model_kwargs),
            user_message=self.prompt.self_reflexion_prompt(),
            parser_name="openai-tools")

        strategy_executor = ReflexionStrategy.create_from_components(
            action_executor=action_executor,
            actor=actor,
            evaluator=evaluator,
            self_reflection=self_reflection,
            # TODO: Discuss what to do with reset here?
            reset_environment=self.meta_tools.reset,
            max_iterations=self.max_num_iterations,
        )

        return strategy_executor
