# Definindo a imagem base do Python (versão 3.10.9)
FROM python:3.10.9


# Usando o usuário root para realizar a instalação de pacotes e configurações no sistema
USER root


# Configuração de proxy para acesso à internet através do proxy corporativo
ENV http_proxy=http://proxy01.bndes.net:8080
ENV https_proxy=http://proxy01.bndes.net:8080


# Atualizando pacotes, instalando dependências essenciais e limpando 
# cache para reduzir o tamanho da imagem
RUN apt-get update -y && \
    apt-get -y upgrade && \
    apt-get install -y build-essential curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Definindo o diretório de trabalho dentro do container
WORKDIR /usr/src/app
 

# Instalando o Poetry, ferramenta de gerenciamento de dependências do Python, 
# via um script remoto
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3
 

# Copiando os arquivos do código-fonte da aplicação para dentro do container
COPY ./app .


# Cria arquivo README.md e copia os arquivos de configuração do Poetry para o container
RUN touch README.md .
COPY pyproject.toml poetry.lock ./


# Configuração do Poetry para não criar um ambiente virtual, 
# instalando as dependências diretamente no sistema
# Instalando as dependências especificadas no poetry.lock com a flag '--no-root' 
# para evitar instalação como root
# RUN /root/.local/bin/poetry lock --no-update
RUN /root/.local/bin/poetry config virtualenvs.create false && \
    /root/.local/bin/poetry install -v --no-root --only main


# Criando um usuário não-root para rodar a aplicação de maneira mais segura
RUN addgroup --system exec && \
    useradd --system --gid exec --create-home --home-dir /home/executorContrato360 executorContrato360 && \
    mkdir -p /home/executorContrato360 && \
    chown -R executorContrato360:exec ./app1.py


# Mudando para o usuário não-root para maior segurança na execução da aplicação
USER executorContrato360


# Definindo o comando que será executado quando o container for iniciado
ENTRYPOINT ["python", "-u", "-m", "streamlit", "run", "app1.py"]