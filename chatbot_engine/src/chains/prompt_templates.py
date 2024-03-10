from langchain.prompts import PromptTemplate


_template = """Given the following Chat History and a follow up question, \
    rephrase the follow up question to be a standalone question, in its \
    original language.

Chat History:
"{chat_history}"
Follow Up question: "{question}"
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

prompt_template = """You are a virtual assistant for LOKA company, \
always respond with kindness and say hello when necessary,\
use the following "context" to answer the question. If it's not \
mentioned in the "context", politely respond that you don't know.

context:
"{context}"

question: "{new_question}"
answer:"""
QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "new_question"]
    )


MULTI_PROMPT_ROUTER_TEMPLATE = """Given a raw text input to a \
    language model select the model prompt best suited for the input. \
    You will be given the names of the available prompts and a \
    description of what the prompt is best suited for. \
    You may also revise the original input if you think that revising\
    it will ultimately lead to a better response from the language model.

    << FORMATTING >>
    Return a markdown code snippet with a JSON object formatted to look like:
    ```json
    {{{{
        "destination": string \ name of the prompt to use or "DEFAULT"
        "next_inputs": string \ a potentially modified version of the \
            original input
    }}}}
    ```

    REMEMBER: "destination" MUST be one of the candidate prompt \
    names specified below OR it can be "DEFAULT" if the input is not\
    well suited for any of the candidate prompts.
    REMEMBER: "next_inputs" can just be the original input \
    if you don't think any modifications are needed.

    << CANDIDATE PROMPTS >>
    {destinations}

    << INPUT >>
    {{input}}

    << OUTPUT (remember to include the ```json)>>"""
