import pandas as pd

from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import (
    ConversationalRetrievalChain, RetrievalQA,
    RetrievalQAWithSourcesChain
)
from langchain.chains.llm import LLMChain
from langchain.chains.base import Chain
from langchain.chains.question_answering import load_qa_chain
from langchain_community.chat_models import ChatOpenAI
from langchain.vectorstores.base import VectorStore
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import (
    LLMRouterChain, RouterOutputParser
)
# from langchain.agents.agent_toolkits import create_python_agent
# from langchain.tools.python.tool import PythonREPLTool
from langchain.chains.combine_documents.stuff import StuffDocumentsChain


from .custom_chains import (
    CustomConversationalRetrievalChain, MyMultiPromptChain
)
from .prompt_templates import (
    QA_PROMPT, CONDENSE_QUESTION_PROMPT,
    MULTI_PROMPT_ROUTER_TEMPLATE
    )


def get_chain_stream_v0(
    vectorstore: VectorStore,
    question_handler,
    stream_handler,
    tracing: bool = False
) -> ConversationalRetrievalChain:
    """
    Create a ConversationalRetrievalChain instance for question-answering.
    with memory up to two previous questions. Considering streaming

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        question_handler (AsyncCallbackHandler)
        stream_handler (AsyncCallbackHandler)

    Returns:
        ConversationalRetrievalChain: A ConversationalRetrievalChain
    """
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])
    if tracing:
        tracer = LangChainTracer()
        tracer.load_default_session()
        manager.add_handler(tracer)
        question_manager.add_handler(tracer)
        stream_manager.add_handler(tracer)

    question_gen_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=question_manager,
        verbose=True,
        max_retries=1
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        max_retries=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        callback_manager=manager
    )

    doc_chain = load_qa_chain(
        streaming_llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
        callback_manager=manager
    )

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        combine_docs_chain=doc_chain,
        callback_manager=manager,
        question_generator=question_generator,
    )
    return qa


def get_chain_v0(
    vectorstore: VectorStore,
    question_handler,
    stream_handler
) -> ConversationalRetrievalChain:
    """
    Create a ConversationalRetrievalChain instance for question-answering.
    with memory up to two previous questions. Considering streaming

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        question_handler (AsyncCallbackHandler)
        stream_handler (AsyncCallbackHandler)

    Returns:
        ConversationalRetrievalChain: A ConversationalRetrievalChain
    """
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True, k=2
        )

    question_gen_llm = ChatOpenAI(
        temperature=0,
        streaming=True,
        model_name="gpt-3.5-turbo-0613",
        verbose=False,
        request_timeout=45,
        callback_manager=question_manager,
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        request_timeout=45,
        max_retries=2,
        temperature=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        callback_manager=manager,
        verbose=True,
        output_key="question"
    )

    doc_chain = load_qa_chain(
        streaming_llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
        callback_manager=manager,
        verbose=True
    )

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={'score_threshold': 0.7, "k": 3}
            ),
        combine_docs_chain=doc_chain,
        callback_manager=manager,
        question_generator=question_generator,
        memory=memory,
        verbose=True
    )
    return qa


def get_chain_wth_memory(
    vectorstore: VectorStore,
    question_handler,
    stream_handler
) -> ConversationalRetrievalChain:
    """
    Create a ConversationalRetrievalChain instance for question-answering.
    with memory up to two previous questions. Considering streaming

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        question_handler (AsyncCallbackHandler)
        stream_handler (AsyncCallbackHandler)

    Returns:
        ConversationalRetrievalChain: A ConversationalRetrievalChain
    """
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])

    question_gen_llm = ChatOpenAI(
        temperature=0,
        streaming=True,
        model_name="gpt-3.5-turbo-0613",
        verbose=False,
        request_timeout=45,
        callback_manager=question_manager,
    )

    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        request_timeout=45,
        max_retries=2,
        temperature=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        callback_manager=manager,
        verbose=True,
    )

    llm_chain = LLMChain(
        llm=streaming_llm,
        prompt=QA_PROMPT,
        verbose=False,
        callback_manager=manager,
    )

    doc_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name='context',
        verbose=False,
        callback_manager=manager
    )

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={'score_threshold': 0.7, "k": 3}
            ),
        combine_docs_chain=doc_chain,
        callback_manager=manager,
        question_generator=question_generator,
        verbose=False,
        return_generated_question=True
    )
    return qa


def get_chain_from_scratch_stream(
    stream_handler
) -> LLMChain:
    """
    Create a LLMChain instance for question-answering
    and other for memory handling

    Args:
        stream_handler (AsyncCallbackHandler)

    Returns:
        LLMChain: memory_chain
        LLMChain: question_chain (Streaming)
    """
    stream_manager = AsyncCallbackManager([stream_handler])
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        temperature=1,
        request_timeout=45
    )

    llm_stream = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        streaming=True,
        temperature=1,
        request_timeout=45,
        callback_manager=stream_manager,
    )

    memory_chain = LLMChain(
        llm=llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        output_key="new_question",
        verbose=False
    )

    question_chain = LLMChain(
        llm=llm_stream,
        prompt=QA_PROMPT,
        output_key="answer",
        verbose=True
    )

    return memory_chain, question_chain


def get_chain_from_scratch() -> LLMChain:
    """
    Create a LLMChain instance for question-answering
    and other for memory handling

    Args:
        stream_handler (AsyncCallbackHandler)

    Returns:
        LLMChain: memory_chain
        LLMChain: question_chain (Streaming)
    """

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        temperature=1,
        request_timeout=45
    )

    llm_stream = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        temperature=1,
        request_timeout=45,
    )

    memory_chain = LLMChain(
        llm=llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        output_key="new_question",
        verbose=True
    )

    question_chain = LLMChain(
        llm=llm_stream,
        prompt=QA_PROMPT,
        output_key="answer",
        verbose=True
    )

    return memory_chain, question_chain


def get_chain_stream(
    vectorstore: VectorStore,
    callback,
) -> ConversationalRetrievalChain:
    """
    Create a ConversationalRetrievalChain instance for question-answering.
    with memory up to two previous questions. Considering streaming

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        question_handler (AsyncCallbackHandler)
        stream_handler (AsyncCallbackHandler)

    Returns:
        ConversationalRetrievalChain: A ConversationalRetrievalChain
    """
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True, k=2
        )

    question_gen_llm = ChatOpenAI(
        temperature=0,
        streaming=True,
        model_name="gpt-3.5-turbo-0613",
        verbose=False,
        callbacks=[callback]
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        streaming=True,
        callbacks=[callback],
        verbose=True,
        max_retries=2,
        temperature=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        verbose=True,
        output_key="question"
    )

    doc_chain = load_qa_chain(
        streaming_llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
        verbose=True
    )

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={'score_threshold': 0.7, "k": 3}
            ),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        memory=memory,
        verbose=True
    )
    return qa


def get_chain_v0_simple(
    vectorstore: VectorStore
) -> ConversationalRetrievalChain:
    """
    Create a ConversationalRetrievalChain instance for question-answering.
    with memory up to two previous questions. Considering streaming

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        question_handler (AsyncCallbackHandler)
        stream_handler (AsyncCallbackHandler)

    Returns:
        ConversationalRetrievalChain: A ConversationalRetrievalChain
    """
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True, k=2
        )

    question_gen_llm = ChatOpenAI(
        temperature=0,
        streaming=False,
        model_name="gpt-3.5-turbo-0613",
        verbose=False
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-0613",
        streaming=False,
        verbose=True,
        max_retries=2,
        temperature=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        verbose=False,
        output_key="question"
    )

    doc_chain = load_qa_chain(
        streaming_llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
        verbose=False
    )

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={'score_threshold': 0.7, "k": 3}
            ),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        memory=memory,
        verbose=False
    )
    return qa


def get_chain_RetrievalQA(
    vectorstore: VectorStore,
    stream_handler,
    tracing: bool = False
) -> RetrievalQA:
    """
    Create a RetrievalQA instance for question-answering.

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        stream_handler (AsyncCallbackHandler)

    Returns:
        RetrievalQA: A RetrievalQA
    """
    manager = AsyncCallbackManager([])
    stream_manager = AsyncCallbackManager([stream_handler])
    if tracing:
        tracer = LangChainTracer()
        tracer.load_default_session()
        manager.add_handler(tracer)
        stream_manager.add_handler(tracer)

    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        max_retries=1
    )

    qa = RetrievalQA.from_llm(
        streaming_llm,
        retriever=vectorstore.as_retriever(k=2),
        callback_manager=manager,
        prompt=QA_PROMPT
    )
    return qa


# def get_agentcsv(
#         df: pd.DataFrame,
#         stream_handler
# ) -> AgentExecutor:
#     """
#     Create a AgentExecutor instance for question-answering from a csv file
#     and considering streaming

#     Args:
#         df (pd.DataFrame): the dataframe to use for the agent
#         stream_handler (AsyncCallbackHandler)

#     Returns:
#         AgentExecutor: A AgentExecutor
#     """
#     manager = AsyncCallbackManager([])
#     stream_manager = AsyncCallbackManager([stream_handler])
#     # Create agent
#     llm = ChatOpenAI(
#         streaming=True,
#         temperature=0,
#         model="gpt-3.5-turbo-0613",
#         callback_manager=stream_manager,
#         )

#     agent = custom_create_pandas_dataframe_agent(
#         llm,
#         df,
#         verbose=False,
#         agent_type=AgentType.OPENAI_FUNCTIONS,
#         callback_manager=manager
#     )

#     return agent


# def get_agentpython(
#         stream_handler
# ) -> AgentExecutor:
#     """
#     Create a AgentExecutor instance for math question answering

#     Args:
#         stream_handler (AsyncCallbackHandler)

#     Returns:
#         AgentExecutor: A AgentExecutor
#     """
#     manager = AsyncCallbackManager([])
#     stream_manager = AsyncCallbackManager([stream_handler])

#     llm = ChatOpenAI(
#         streaming=True,
#         temperature=0,
#         model="gpt-3.5-turbo-0613",
#         callback_manager=stream_manager,
#         )
#     agent = create_python_agent(
#         llm=llm,
#         tool=PythonREPLTool(),
#         verbose=False,
#         agent_type=AgentType.OPENAI_FUNCTIONS,
#         agent_executor_kwargs={"handle_parsing_errors": True},
#         callback_manager=manager
#     )
#     return agent


def get_simple_math(
        stream_handler
) -> Chain:
    """
    Create a Chain instance for math question answering

    Args:
        stream_handler (AsyncCallbackHandler)

    Returns:
        Chain: A Chain
    """
    manager = AsyncCallbackManager([])
    stream_manager = AsyncCallbackManager([stream_handler])
    template = """Pregunta: {question}

    Respuesta: Piensa paso por paso"""

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm = ChatOpenAI(
        streaming=True,
        temperature=0,
        model="gpt-3.5-turbo-0613",
        callback_manager=stream_manager,
        )
    chain = LLMChain(
        prompt=prompt,
        llm=llm,
        callback_manager=manager
        )

    return chain


def get_chainCustom(
    vectorstore: VectorStore,
    question_handler,
    stream_handler
) -> ConversationalRetrievalChain:
    """
    Create a ConversationalRetrievalChain instance for question-answering.
    with memory up to two previous questions. Considering streaming

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        question_handler (AsyncCallbackHandler)
        stream_handler (AsyncCallbackHandler)

    Returns:
        ConversationalRetrievalChain: A ConversationalRetrievalChain
    """
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True, k=2
        )

    question_gen_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=question_manager,
        verbose=False,
        max_retries=2,
        temperature=0
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=stream_manager,
        verbose=False,
        max_retries=2,
        temperature=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        callback_manager=manager,
        verbose=False
    )

    doc_chain = load_qa_chain(
        streaming_llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
        callback_manager=manager,
        verbose=False
    )

    qa = CustomConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        combine_docs_chain=doc_chain,
        callback_manager=manager,
        question_generator=question_generator,
        memory=memory,
        verbose=False
    )
    qa.output_key = "output"

    return qa


def get_router_assistant(
    vectorstore,
    df_prices,
    question_handler,
    stream_handler
) -> Chain:
    """
    Create a MyMultiPromptChain instance for question-answering.
    using routing logic between different chains

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.
        df_prices (pd.DataFrame): the data of prices
        question_handler (AsyncCallbackHandler)
        stream_handler (AsyncCallbackHandler)

    Returns:
        MyMultiPromptChain: A MyMultiPromptChain
    """
    manager = AsyncCallbackManager([])
    stream_manager = AsyncCallbackManager([stream_handler])

    chains_agents_infos = [
        {
            "name": "Precios_Procedimientos_Examen_Estudios",
            "description": "Util para preguntas sobre precios, tiempos y \
                muestras de examenes, procedimientos y estudios",
            "func": get_agentcsv(df_prices, stream_handler)
        },
        {
            "name": "bluemedical",
            "description": "Util para preguntas sobre bluemeds, \
                recomendaciones, planes vivolife, horarios de clínicas, \
                administración de medicamentos",
            "func": get_chainCustom(
                vectorstore, question_handler, stream_handler
            )
        },
        {
            "name": "Calculadora",
            "description": "Util para resolver problemas numéricos, de \
                matemáticas",
            "func": get_agentpython(stream_handler)
        }
    ]

    destination_chains = {
        p['name']: p['func'] for p in chains_agents_infos
    }
    destinations = [
        f"{p['name']}: {p['description']}" for p in chains_agents_infos
    ]
    destinations_str = "\n".join(destinations)

    llm = ChatOpenAI(
            temperature=0,
            streaming=False,
            model="gpt-3.5-turbo-0613",
            callback_manager=stream_manager,
            )

    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
        destinations=destinations_str
    )

    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=RouterOutputParser(),
    )

    router_chain = LLMRouterChain.from_llm(
        llm,
        router_prompt,
        callback_manager=manager
        )

    chain = MyMultiPromptChain(
        router_chain=router_chain,
        destination_chains=destination_chains,
        default_chain=get_chainCustom(
            vectorstore, question_handler, stream_handler
        ),
        verbose=False,
        callback_manager=manager
        )

    return chain


def get_chain_v1(
    vectorstore: VectorStore
) -> Chain:
    """
    Create a ConversationalRetrievalChain instance for question-answering.
    with memory up to two previous questions

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.

    Returns:
        ConversationalRetrievalChain: A ConversationalRetrievalChain
    """
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True, k=2
        )

    question_gen_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        verbose=True,
        max_retries=2,
        temperature=1
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        verbose=True,
        max_retries=2,
        temperature=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        verbose=True
    )

    doc_chain = load_qa_chain(
        streaming_llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
        verbose=True
    )

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        memory=memory,
        verbose=True,
    )
    return qa


def get_chain_RetrievalQASources_v0(
    vectorstore: VectorStore
) -> RetrievalQA:
    """
    Create a RetrievalQASources instance for question-answering.

    Args:
        vectorstore (VectorStore): A vector store used for document retrieval.

    Returns:
        RetrievalQA: A RetrievalQASources
    """
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        verbose=True,
        max_retries=1
    )

    qa = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type="stuff",
        return_source_documents=True,
    )
    return qa


def get_simple_assistant(
        stream_handler
):
    chat = ChatOpenAI(
        temperature=1,
        streaming=False,
        model="gpt-3.5-turbo-0613",
    )
    return chat
