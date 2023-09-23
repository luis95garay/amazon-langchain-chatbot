"""Create a ChatVectorDBChain for question/answering."""
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import (
    ConversationalRetrievalChain, RetrievalQA
)
# from langchain.chains.chat_vector_db.prompts import (
# CONDENSE_QUESTION_PROMPT, QA_PROMPT)
from src.generators.prompt_templates import (
    QA_PROMPT, CONDENSE_QUESTION_PROMPT
    )
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.base import VectorStore
from langchain.memory import ConversationBufferWindowMemory


def get_chain(
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


def get_chainM(
    vectorstore: VectorStore,
    question_handler=None,
    stream_handler=None
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for
    # combine docs and a separate, non-streaming llm for
    # question generation
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([])
    stream_manager = AsyncCallbackManager([])
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


def get_chain_RetrievalQA(
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


def get_chainM1(
    vectorstore: VectorStore
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", return_messages=True, k=2
        )

    question_gen_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        verbose=True,
        max_retries=2,
        temperature=0
    )
    streaming_llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
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
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        memory=memory,
        verbose=True,
    )
    return qa