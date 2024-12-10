import re
import os
import logging
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

import streamlit as st

from langchain_openai.llms import OpenAI 

from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
import sqlalchemy
import utils

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationSummaryMemory

# Plotly Agent
from data_visualization.plotly_agent import create_plotly_agent
from data_visualization.evaluate.judge_text import judge
from data_visualization.extract import extrai_codigo_python
from plotly.graph_objs._figure import Figure

if "id" not in st.session_state:
    from random import randint
    st.session_state.id = str(randint(1, 999999)).zfill(6)

logging.basicConfig(format="%(asctime)s [%(filename)s]:%(lineno)d %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S",
                    level=logging.INFO,
                    handlers=[logging.StreamHandler()]
                   )
logger = logging.getLogger(__name__)

#load_dotenv(find_dotenv()) 

load_dotenv()

llm = OpenAI(temperature = 0.0)

# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
#AZURE_OPENAI_API_KEY = os.getenv('APP_SECRET_VALUE_KEY')
#AZURE_OPENAI_ENDPOINT = os.getenv('APP_SECRET_VALUE_ENDPOINT')
#AZURE_OPENAI_API_VERSION = "2024-02-01"
#AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv('APP_SECRET_VALUE_DEPLOYMENT_KEY')

#def cria_chat_OpenAI():
#    llm = AzureChatOpenAI(
#        azure_endpoint=AZURE_OPENAI_ENDPOINT,
#        api_version=AZURE_OPENAI_API_VERSION,
#        api_key=AZURE_OPENAI_API_KEY,
#        azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
#    )
#    return llm

def cria_chat_OpenAI():
    llm = OpenAI(temperature = 0.5)
    return llm

# Inicializa informações da sessão.
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_history = []

if "path" not in st.session_state:
    st.session_state.path = "./data/database.db"

if "graficos" not in st.session_state:
    st.session_state.graficos = []

if "memory" not in st.session_state:
    llm = cria_chat_OpenAI()
    st.session_state.memory = ConversationSummaryMemory(
        llm=llm,
        memory_key="chat_history_summary",
        input_key="input",
        output_key="output",
        prompt=utils.prompt
    )


def recepcionista(texto: str, llm) -> str:
    system_prompt_job = '''
    Você receberá um texto como entrada e sua tarefa \
    será determinar se esse texto representa um cumprimento, \
    um agradecimento ou se ele não se enquadra em nenhuma \
    dessas duas categorias. Tenha em mente que você deve ser educado,
    ou seja, demostre querer ajudar.
    - Se o texto for identificado como um cumprimento \
    retorne um texto de cumprimento educado.
    - Se o texto for identificado como um agradecimento \
    retorne um texto de agradecimento educado.
    - Caso o texto não se encaixe em nenhuma dessas categorias, \
    ou seja, não seja nem um cumprimento nem um agradecimento, \
    você deve simplesmente retornar 0.
    Observação: Respeite **SEMPRE** esses comandos com absoluta \
    prioridade, ou seja, responda **APENAS** com um cumprimento, \
    ou com um agradecimento ou com 0.
    '''

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_job),
            ("human", "{prompt}")
        ]
    )

    chain = prompt | llm | StrOutputParser()
    resposta = chain.invoke({'prompt': texto})

    if resposta == '0':
        return bool(int(resposta))
    else:
        return resposta


def cria_agent(llm):
    db = SQLDatabase(
        engine=sqlalchemy.create_engine(f'sqlite:///{st.session_state.path}'),
        max_string_length=6000)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    df_agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        top_k=30,
        max_iterations=11,
        verbose=True,
        agent_executor_kwargs={
            "handle_parsing_errors": True,
            "return_intermediate_steps": True,
            "memory": st.session_state.memory
        }
    )
    return df_agent


resposta_final = ""
# Streamlit
st.set_page_config(page_title='Contrato360',
                   page_icon='./img/logo.png',
                   layout='wide',
                   initial_sidebar_state='expanded')


def reset_conversation():
    del st.session_state['messages']
    del st.session_state['chat_history']


sugestoes = ['Qual é o objeto do contrato ',
             'Temos algum contrato cujo objeto é ',
             'Temos algum contrato com o fornecedor ']

st.logo('./img/logo_bndes.png', icon_image='./img/logo.png')

with st.sidebar:
    with st.expander(label='Perguntas Frequentes', expanded=False):
        for opcao in sugestoes:
            st.code("{}".format(opcao))

    if "messages" in st.session_state:
        st.download_button(label='Exportar Conversa', data=str(st.session_state.messages))
        st.button('Reiniciar Conversa', on_click=reset_conversation)

    ativa_plotly_agent = st.checkbox(
        'Mostrar Gráficos',
        value=True,
        help='Habilita possibilidade de criação de gráficos por meio da resposta do assistente.'
    )

    st.markdown('''
        ## Sobre
        Esse aplicativo foi criado com o intuito de tornar mais prático encontrar informações relevantes sobre os contratos do BNDES. Nessa aplicação contém dados referentes a contratos cujo gestor pertence a lotação da ATI e outros contratos referentes àqueles que temos suas Cláusulas.

        ---
        **Contrato360 pode cometer erros.** Considere verificar informações importantes.
        Unidade Gestora: ATI/DEGAT/GPLAT
        ''')

# Título
st.title(':blue[Contrato 360]')

# Mostra as mensagens da conversa de acordo com o histórico
chart_index = 0
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Mostra os gráficos gerados no histórico de mensagens
        if ativa_plotly_agent:
            if message["role"] == "assistant":
                if chart_index < len(st.session_state.graficos):
                    if st.session_state.graficos[chart_index]:
                        st.plotly_chart(st.session_state.graficos[chart_index], use_container_width=True)
                    chart_index += 1

if prompt := st.chat_input("Pergunta"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    buffer = st.session_state.memory.buffer or ''
    with st.chat_message("user"):
        st.markdown(prompt)

    logger.info(f"{'='*20} NOVA PERGUNTA {'='*20}")
    logger.info(f"Pergunta do usuário: {prompt}\n")

    recepcao = recepcionista(prompt, cria_chat_OpenAI())

    if recepcao:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(recepcao)
        st.session_state.messages.append({"role": "assistant", "content": recepcao})
        st.session_state.graficos.append('')

        logger.info(f"Resposta do recepcionista: {recepcao}")
    else:
        with st.spinner("Formulando resposta..."):
            df_table_name = utils.df_table_name
            df2_table_name = utils.df2_table_name
            df_cols = utils.df_cols
            df2_cols = utils.df2_cols
            prefix = utils.MSSQL_AGENT_PREFIX
            sufix = utils.MSSQL_AGENT_FORMAT_INSTRUCTIONS

            llm = cria_chat_OpenAI()
            agent = cria_agent(llm)

            buffer = st.session_state.memory.buffer or ''
            chat_history = f'Histórico de Mensagens: {buffer}' if buffer else ''
            response = agent.invoke({'input': f'{prefix} + <{prompt}> + {sufix} + {chat_history}'})
            buffer = st.session_state.memory.buffer

            response_output = response['output']
            response_thought = response['intermediate_steps']
            logger.info(f"Raciocínio do Agente: \n{response_thought if response_thought != [] else 'Não foi necessário Raciocínio.'}\n")
            logger.info(f"{'='*50}\n")

        # Atualiza a interface do usuário
        resposta_final = response_output.replace("$", "\$")
        if "Agent stopped due to iteration limit or time limit." in resposta_final:
            resposta_final = "Desculpe, um erro aconteceu e me impediu de fornecer uma resposta. Por favor, reiniciar a conversa."
            logger.error("Erro: Limite de iteração ou tempo atingido.\n")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(resposta_final)

        logger.info(f"Resposta do agente: {resposta_final}\n")

        if ativa_plotly_agent:
            llm = cria_chat_OpenAI()
            julgamento = judge(texto=response_output, llm=llm)

            if julgamento:
                with st.spinner('Criando Gráfico...'):
                    llm = cria_chat_OpenAI()
                    plotly_agent = create_plotly_agent(
                        llm=llm,
                        max_interations=8,
                        verbose=True
                    )
                    try:
                        plotly_response = plotly_agent.invoke({'input': response_output})

                        plotly_response_output = plotly_response['output']
                        fig_dict = {"fig": Figure}

                        fig_code = extrai_codigo_python(plotly_response_output)
                        exec(fig_code, fig_dict)

                        fig = fig_dict.get("fig", None)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            st.session_state.graficos.append(fig)
                            logger.info("Gráfico gerado com sucesso.\n")
                        else:
                            logger.warning("Nenhum gráfico foi gerado.\n")

                    except (SyntaxError, ValueError) as e:
                        st.markdown('Desculpe, ocorreu algum erro na geração do gráfico. \
                                    Gostaria de fazer uma nova pergunta referente aos contratos do BNDES?')
                        logger.error(f"Erro ao gerar o gráfico: {e}\n")
                    except Exception as e:
                        st.markdown('Ocorreu um erro inesperado. Por favor, tente novamente.')
                        logger.error(f"Erro inesperado ao gerar o gráfico: {e}\n")
            else:
                st.session_state.graficos.append('')
                logger.info("Não houve necessidade de gerar gráfico.\n")

        st.session_state.messages.append({"role": "assistant", "content": resposta_final})

    logger.info(f"Histórico de mensagens: {buffer or 'Não passou do recepcionista'}")
    logger.info(f"ID da conversa: chat{str(st.session_state.id)}")
    logger.info(f"{'='*20} FIM DA INTERAÇÃO {'='*20}\n\n")

    st.rerun()  # Apaga gráfico fantasma 👻
