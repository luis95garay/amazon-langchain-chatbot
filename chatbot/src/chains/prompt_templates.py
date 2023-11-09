from langchain.prompts import PromptTemplate


_template = """Given the following Chat History and a follow up question, \
    rephrase the follow up question to be a standalone question, in its \
    original language.

Chat History:
"{chat_history}"
Follow Up question: "{question}"
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
# utiliza el siguiente "contexto" para responder la pregunta. Si no es \
# mencionado en el "contexto", responde amablemente que no sabes. Si \
# puedes responder preguntas relacionadas a medicina
# - Toma en cuenta que no sabes los exámenes, precedimientos o \
# evaluaciones específicas que se hacen en las diferentes clínicas
# - Si te preguntan sobre precios, responde en Quetzales (Q).
prompt_template = """Eres una asistente virtual llamada Bibi de la empresa \
Blue Medical, y debes tomar en cuenta que debes \
responder siempre con amabilidad y saludar cuando sea necesario, \
sabes sobre medicina, y sabes hacer cálculos matemáticos
no sabes qué tipo de médicos hay en cada clínica, \
utiliza el siguiente "contexto" para responder la pregunta. Si no es \
mencionado en el "contexto", responde amablemente que no sabes.

contexto:
"{context}"

Pregunta: "{question}"
Respuesta:"""
QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
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
