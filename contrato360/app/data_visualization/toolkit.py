from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import pandas as pd
import plotly.express as px

from data_visualization.detect import check_malicious_code


@tool
def create_plotly_chart(df, plotly_code):
    '''
    Ferramenta para criar gráfico com plotly

    Parâmetros:
    df: pd.DataFrame
    plotly_code: str

    Retorno:
    fig: plotly.graph_objs._figure.Figure

    **Exemplo**
    ```python
    fig = create_plotly_chart(
        df = pd.DataFrame(df),
        plotly_code = 'fig = px.line(df, x="A", y="B")'
    )
    fig.show()
    ```
    '''
    plotly_dict = {"df": pd.DataFrame(df), "px": px}

    try:
        is_malicious = check_malicious_code(f'''{plotly_code}''')

        if is_malicious:
            return 'Malicious code detected!'

        exec(plotly_code, globals(), plotly_dict)
        fig = plotly_dict.get("fig", None)

        if fig is None:
            raise ValueError("O código Plotly não criou um gráfico 'fig'. Verifique o código.")

        return fig

    except Exception as e:
        repaired_fig = repair_plotly_code(df, plotly_code, str(e))

        if repaired_fig is None:
            raise ValueError("Falha ao reparar o código Plotly.")

        return repaired_fig


@tool
def repair_plotly_code(df, plotly_code, error_message):
    '''
    Ferramenta para tratar possíveis erros de código plotly

    Parâmetros:
    df: pd.DataFrame
    plotly_code: str
    error_message: str

    Retorno:
    fig: plotly.graph_objs._figure.Figure

    **Exemplo de Erro**
    ```python
    fig = repair_plotly_code(
        df = pd.DataFrame(df),
        plotly_code = 'px.bar(df, x="A", y="C")',
        e = "AttributeError: Value of 'y' is not the name of a column in 'data_frame'"
    )
    fig.show()
    ```

    **Exemplo de Correção**
    ```python
    fig = repair_plotly_code(
        df = pd.DataFrame(df),
        plotly_code = 'px.bar(df, x=df["A"], y=["B"])',
    )
    fig.show()
    ```
    '''
    repair_dict = {"df": pd.DataFrame(df), "plotly_code": plotly_code, "error_message": error_message, "px": px}

    try:
        is_malicious = check_malicious_code(f'''{plotly_code}''')

        if is_malicious:
            return 'Malicious code detected'

        exec(plotly_code, globals(), repair_dict)
        fig = repair_dict.get("fig", None)

        if fig is None:
            raise ValueError("O código Plotly reparado não criou um gráfico 'fig'. Verifique o código.")

        return fig

    except Exception as e:
        print(f"Falha ao reparar o código Plotly: {e}")
        return None


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """Você é um assistente de visualização de dados com Plotly.
        INSTRUÇÕES GERAIS:
        Visualize o texto de entrada e tente formular uma visualização para ele.
        Considere fazer um tratamento em relação aos nomes das colunas do dataframe, \
        ou seja, retire acentuações e quaisquer outros detalhes que possam dificultar a \
        criação do gráfico (Exemplo: Número -> Numero).
        Sempre utilize a ferramenta [create_plotly_chart] para criar sua visualização com plotly.
        Utilize a ferramenta [repair_plotly_code] caso ocorra algum erro durante a execução do código \
        criado pela ferramenta [create_plotly_chart].
        A etapa Resposta Final deve receber o código python do gráfico criado, não chame uma ferramenta na resposta final.

        INSTRUÇÕES DE ETAPAS:
        Formato -> nome da etapa: conteúdo
        Você deve executar respeitando as seguintes etapas:
        - Pensamento: Raciocínio para entender o texto de entrada e qual deve ser o seu próximo passo;
        - Ferramenta: Ferramenta que você irá usar;
        - Ação: Resultado do código da Ferramenta usada;
        - Resposta Final: Código python com bibliotecas, df, ...

        INTRUÇÕES PARA GRÁFICOS:
        Sempre dê um título e **SEMPRE** utilize tag html para deixá-lo em negrito.
        Adicione anotações aos valores do eixo x.
        Sempre exiba números muito grandes em formato aproximado com 2 casas decimais.
        Sempre estilize o gráfico, para deixá-lo interessante e de fácil entendimento
        Se a variável for uma porcentagem, mostre com 2 casas decimais e o sinal de '%'.
        Exiba os valores de data no formato Dia/Mês/Ano.
        Em um gráfico de linha, coloque um ponto nos eixos
        Certifique-se de que todas as matrizes ou vetores que você está utilizando para elaborar o gráfico tenham \
        o mesmo tamanho.
        Se tanto o eixo x quanto o eixo y forem variáveis categóricas, considere usar um gráfico de dispersão.
        Se um dos eixos for uma variável categórica e o outro for uma data, considere também usar um gráfico de dispersão.
        Considere fazer uma linha temporal apenas quando a data de início e data de fim forem diferentes entre si.
        Caso considere interessante, extraia o máximo de informação do dataframe original para \
        a confecção do gráfico para ser preenchido no tooltip.
        """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)
