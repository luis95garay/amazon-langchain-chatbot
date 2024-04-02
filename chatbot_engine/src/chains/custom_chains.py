from typing import Mapping, List, Union, Dict, Any, Optional, Tuple
import inspect

from langchain.chains import (
    ConversationalRetrievalChain, MultiRouteChain
)
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun
)
from langchain.schema.messages import BaseMessage
from langchain.agents.agent import AgentExecutor



CHAT_TURN_TYPE = Union[Tuple[str, str], BaseMessage]
_ROLE_MAP = {"human": "Human: ", "ai": "Assistant: "}


def _get_chat_history(chat_history: List[CHAT_TURN_TYPE]) -> str:
    buffer = ""
    for dialogue_turn in chat_history:
        if isinstance(dialogue_turn, BaseMessage):
            role_prefix = _ROLE_MAP.get(
                dialogue_turn.type, f"{dialogue_turn.type}: "
            )
            buffer += f"\n{role_prefix}{dialogue_turn.content}"
        elif isinstance(dialogue_turn, tuple):
            human = "Human: " + dialogue_turn[0]
            ai = "Assistant: " + dialogue_turn[1]
            buffer += "\n" + "\n".join([human, ai])
        else:
            raise ValueError(
                f"Unsupported chat history format: \
                    {type(dialogue_turn)}."
                f" Full chat history: {chat_history} "
            )
    return buffer


class CustomConversationalRetrievalChain(
    ConversationalRetrievalChain
):
    """
    Create a custom ConversationalRetrievalChain for handling \
        customize inputs and outputs values
    """
    @property
    def input_keys(self) -> List[str]:
        """Input keys."""
        return ["input", "chat_history"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        _run_manager = run_manager or \
            CallbackManagerForChainRun.get_noop_manager()
        question = inputs["input"]
        get_chat_history = self.get_chat_history or _get_chat_history
        chat_history_str = get_chat_history(inputs["chat_history"])

        if chat_history_str:
            callbacks = _run_manager.get_child()
            new_question = self.question_generator.run(
                input=question,
                chat_history=chat_history_str,
                callbacks=callbacks
            )

        else:
            new_question = question

        accepts_run_manager = (
            "run_manager" in inspect.signature(self._get_docs).parameters
        )
        if accepts_run_manager:
            docs = self._get_docs(
                new_question, inputs, run_manager=_run_manager
            )
        else:
            docs = self._get_docs(new_question, inputs)
        new_inputs = inputs.copy()
        if self.rephrase_question:
            new_inputs["input"] = new_question
        new_inputs["chat_history"] = chat_history_str
        answer = self.combine_docs_chain.run(
            input_documents=docs,
            callbacks=_run_manager.get_child(),
            **new_inputs
        )
        output: Dict[str, Any] = {self.output_key: answer}
        if self.return_source_documents:
            output["source_documents"] = docs
        if self.return_generated_question:
            output["generated_question"] = new_question
        return output

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        _run_manager = run_manager or \
            AsyncCallbackManagerForChainRun.get_noop_manager()
        question = inputs["input"]
        get_chat_history = self.get_chat_history or _get_chat_history
        chat_history_str = get_chat_history(inputs["chat_history"])
        if chat_history_str:
            callbacks = _run_manager.get_child()
            new_question = await self.question_generator.arun(
                input=question,
                chat_history=chat_history_str,
                callbacks=callbacks
            )
        else:
            new_question = question
        accepts_run_manager = (
            "run_manager" in inspect.signature(self._aget_docs).parameters
        )
        if accepts_run_manager:
            docs = await self._aget_docs(
                new_question, inputs, run_manager=_run_manager
            )
        else:
            docs = await self._aget_docs(new_question, inputs)

        new_inputs = inputs.copy()
        if self.rephrase_question:
            new_inputs["input"] = new_question
        new_inputs["chat_history"] = chat_history_str
        answer = await self.combine_docs_chain.arun(
            input_documents=docs,
            callbacks=_run_manager.get_child(),
            **new_inputs
        )
        output: Dict[str, Any] = {self.output_key: answer}
        if self.return_source_documents:
            output["source_documents"] = docs
        if self.return_generated_question:
            output["generated_question"] = new_question
        return output


class MyMultiPromptChain(MultiRouteChain):
    """
    Create a custom MultiRouteChain that uses an LLM router chain
    to choose amongst prompts, for handling customize outputs values
    """
    destination_chains: Mapping[
        str, Union[ConversationalRetrievalChain, AgentExecutor]
    ]
    """Map of name to candidate chains that inputs can be routed to."""
    default_chain: ConversationalRetrievalChain
    """Default chain to use when router doesn't map input to one of the \
        destinations."""

    @property
    def output_keys(self) -> List[str]:
        return ['output']


# def custom_create_pandas_dataframe_agent(
#     llm: BaseLanguageModel,
#     df: Any,
#     agent_type: AgentType = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     callback_manager: Optional[BaseCallbackManager] = None,
#     prefix: Optional[str] = None,
#     suffix: Optional[str] = None,
#     input_variables: Optional[List[str]] = None,
#     verbose: bool = False,
#     return_intermediate_steps: bool = False,
#     max_iterations: Optional[int] = 15,
#     max_execution_time: Optional[float] = None,
#     early_stopping_method: str = "force",
#     agent_executor_kwargs: Optional[Dict[str, Any]] = None,
#     include_df_in_prompt: Optional[bool] = True,
#     number_of_head_rows: int = 5,
#     **kwargs: Dict[str, Any],
# ) -> AgentExecutor:
#     """Create a custom improved pandas dataframe AgentExecutor"""
#     agent: BaseSingleActionAgent
#     if agent_type == AgentType.ZERO_SHOT_REACT_DESCRIPTION:
#         prompt, tools = _get_prompt_and_tools(
#             df,
#             prefix=prefix,
#             suffix=suffix,
#             input_variables=input_variables,
#             include_df_in_prompt=include_df_in_prompt,
#             number_of_head_rows=number_of_head_rows,
#         )
#         llm_chain = LLMChain(
#             llm=llm,
#             prompt=prompt,
#             callback_manager=callback_manager,
#         )
#         tool_names = [tool.name for tool in tools]
#         agent = ZeroShotAgent(
#             llm_chain=llm_chain,
#             allowed_tools=tool_names,
#             callback_manager=callback_manager,
#             **kwargs,
#         )
#     elif agent_type == AgentType.OPENAI_FUNCTIONS:
#         _prompt, tools = _get_functions_prompt_and_tools(
#             df,
#             prefix=prefix,
#             suffix=suffix,
#             input_variables=input_variables,
#             include_df_in_prompt=include_df_in_prompt,
#             number_of_head_rows=number_of_head_rows,
#         )
#         _prompt.messages[0].content += "\nIf they ask for prices, answer \
#             always in Quetzales (Q)\nAlways run the python code\nAlways \
#             run the python code\nDo not explain the python code"
#         agent = OpenAIFunctionsAgent(
#             llm=llm,
#             prompt=_prompt,
#             tools=tools,
#             callback_manager=callback_manager,
#             **kwargs,
#         )
#     else:
#         raise ValueError(
#             f"Agent type {agent_type} not supported at the moment."
#         )
#     return AgentExecutor.from_agent_and_tools(
#         agent=agent,
#         tools=tools,
#         callback_manager=callback_manager,
#         verbose=verbose,
#         return_intermediate_steps=return_intermediate_steps,
#         max_iterations=max_iterations,
#         max_execution_time=max_execution_time,
#         early_stopping_method=early_stopping_method,
#         **(agent_executor_kwargs or {}),
#     )
