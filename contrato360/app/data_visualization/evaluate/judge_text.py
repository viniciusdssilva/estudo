from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser


def judge(texto: str, llm, info: str = '') -> bool:

    system_prompt_job_raw = '''
    Dado um texto você deve julgar a necessidade ou não de \
    um gráfico para visualizar o seu conteúdo. Sua resposta \
    deve ser '0' para quando não precisar de gráfico e '1' para \
    quando precisar.
    '''

    system_prompt_job = system_prompt_job_raw + info if info else system_prompt_job_raw

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_job),
            ("human", "{prompt}")
        ]
    )

    chain = prompt | llm | StrOutputParser()

    '''
    - Verificamos a necessidade de gráfico
    - A partir do resultado do invoke devemos transformar o valor de str para int e depois para bool.

    resposta <- 0 ou 1
    resposta_final <- True ou False
    '''
    resposta = chain.invoke({"prompt": texto})
    resposta_final = bool(int(resposta))

    return resposta_final