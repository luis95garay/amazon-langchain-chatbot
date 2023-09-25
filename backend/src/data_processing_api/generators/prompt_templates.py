from langchain.prompts import PromptTemplate


question_template = PromptTemplate(
            input_variables=["document", "context"],
            template="""
                      Teniendo en consideración el siguiente contexto, puedes generar preguntas a partir del siguiente texto de entrada y generarlas con el siguiente formato diccionario de python?, intenta hacer preguntas que engloben varias puntos

                      Contexto:
                      "{context}"

                      Texto de entrada:
                      "{document}"

                      Formato de salida:
                      "una única llave ""question"" y las preguntas dentro de una lista python"
                      """
        )

answer_template = PromptTemplate(
            input_variables=["row", "document"],
            template="""
                      Bajo el siguiente contexto, puedes responder la siguiente pregunta:
                      "{row}"
                      Contexto:
                      "{document}"
                      """
        )

_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
"{chat_history}"
Follow Up Input: "{input}"
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# - Toma en cuenta que no sabes los exámenes, precedimientos o evaluaciones específicas que se hacen en las diferentes clínicas
# - Si te preguntan sobre precios, responde en Quetzales (Q).
prompt_template = """Imagina que eres un asistente virtual de la empresa X, y debes tomar en cuenta que debes \
responder siempre con amabilidad y saludar cuando sea necesario, \
utiliza el siguiente "contexto" para responder la pregunta. Si no es mencionado en el "contexto", responde amablemente que no sabes, no respondas preguntas que no tengan que ver con el "contexto".

contexto:
"{context}"

Pregunta: "{input}"
Respuesta:"""
QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "input"]
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
        "next_inputs": string \ a potentially modified version of the original input
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
