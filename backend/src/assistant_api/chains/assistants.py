import pandas as pd

from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import (
    ConversationalRetrievalChain, RetrievalQA,
    RetrievalQAWithSourcesChain
)
from langchain.chains.chat_vector_db.prompts import (
    CONDENSE_QUESTION_PROMPT, QA_PROMPT
)
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.base import VectorStore
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import (
    LLMRouterChain, RouterOutputParser
)

from .prompt_templates import (
    MULTI_PROMPT_ROUTER_TEMPLATE
)
from .custom_chains import (
    CustomConversationalRetrievalChain, MyMultiPromptChain,
    custom_create_pandas_dataframe_agent
)


def get_chain_stream_v0(
    vectorstore: VectorStore,
    question_handler,
    stream_handler,
    tracing: bool = False
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for
    # combine docs and a separate, non-streaming llm for
    # question generation
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
        retriever=vectorstore.as_retriever(k=4),
        combine_docs_chain=doc_chain,
        callback_manager=manager,
        question_generator=question_generator,
    )
    return qa


def get_chain_v0(
    vectorstore: VectorStore,
    question_handler=None,
    stream_handler=None
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for
    # combine docs and a separate, non-streaming llm for
    # question generation
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True
        )

    question_gen_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=question_manager,
        verbose=False,
        max_retries=2
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=stream_manager,
        verbose=False,
        max_retries=2,
        temperature=0
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

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        combine_docs_chain=doc_chain,
        callback_manager=manager,
        question_generator=question_generator,
        memory=memory,
        verbose=False
    )
    return qa


def get_chain_RetrievalQA_stream_v0(
    vectorstore: VectorStore, stream_handler, tracing: bool = False
) -> RetrievalQA:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for combine docs
    # and a separate, non-streaming llm for question generation
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


def get_agentcsv(
        csv_path: str,
        stream_handler
) -> AgentExecutor:
    manager = AsyncCallbackManager([])
    stream_manager = AsyncCallbackManager([stream_handler])
    # Create agent
    llm = ChatOpenAI(
        streaming=True,
        temperature=0,
        model="gpt-3.5-turbo-0613",
        callback_manager=stream_manager,
        )
    df = pd.read_csv(csv_path)

    agent = custom_create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        callback_manager=manager
    )

    return agent


def get_chainCustom(
    vectorstore: VectorStore,
    question_handler,
    stream_handler
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for
    # combine docs and a separate, non-streaming llm for
    # question generation
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
        verbose=True,
        max_retries=2,
        temperature=0
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        max_retries=2,
        temperature=1
    )

    question_generator = LLMChain(
        llm=question_gen_llm,
        prompt=CONDENSE_QUESTION_PROMPT,
        callback_manager=manager,
        verbose=True
    )

    doc_chain = load_qa_chain(
        streaming_llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
        callback_manager=manager,
        verbose=True
    )

    qa = CustomConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        combine_docs_chain=doc_chain,
        callback_manager=manager,
        question_generator=question_generator,
        memory=memory,
        verbose=True
    )
    qa.output_key = "output"

    return qa


def get_router_assistant(
        vectorstore,
        csv_path,
        csv_path1,
        question_handler,
        stream_handler
        ):
    manager = AsyncCallbackManager([])
    stream_manager = AsyncCallbackManager([stream_handler])

    chains_agents_infos = [
        {
            "name": "archivoexcel1",
            "description": "Descripción uno",
            "func": get_agentcsv(csv_path, stream_handler)
        },
        {
            "name": "vectorstore1",
            "description": "Descripción dos",
            "func": get_chainCustom(
                vectorstore, question_handler, stream_handler
                )
        },
        {
            "name": "archivoexcel2",
            "description": "Descripción tres",
            "func": get_agentcsv(csv_path1, stream_handler)
        }
    ]

    destination_chains = {p['name']: p['func'] for p in chains_agents_infos}
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
        verbose=True,
        callback_manager=manager
        )

    return chain


def get_chain_v1(
    vectorstore: VectorStore
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""

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
