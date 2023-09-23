from langchain.prompts import PromptTemplate


question_template = PromptTemplate(
            input_variables=["document","context"],
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
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

prompt_template = """Imagina que eres un asistente virtual, y debes responder siempre con amabilidad.
Utiliza el siguiente contexto para responder la pregunta. Si no es mencionado en el contexto, responde amablemente que no sabes, no trates de inventar.

{context}

Pregunta: {question}
Respuesta:"""
QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
    )
