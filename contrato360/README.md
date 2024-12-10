# Configuração do JupyterHub 

Esse arquivo é dedicado a configuração do jupyterhub para conseguir executar os notebooks e o arquivos sem problema de dependência ou de versão. De forma resumida, inicialmente atualizamos o python para a versão 3.10.9, e em seguida criamos o ambiente com os pacotes necessários.  Atualmente é utilizado o Poetry para fazer o gerenciamento de pacotes. Caso em seu Jupyter não tenha o poetry instalado, é sugerido resetar a imagem do jupyter para poder ter acesso ao gerenciador. Por fim, também mostramos como rodar a aplicação streamlit. 

O que estamos fazendo aqui (pelo menos a primeira parte) pode ser encontrado de forma semelhante no [Colabore](https://colabore.bndes.net/wikis/home?lang=pt-br#!/wiki/W4447880f6d58_437d_b95a_c73d04a3510c/page/Python%20mais%20novo%20no%20JupyterHub), com algumas linhas de código no terminal diferente, porém no fundo é a mesma ideia.

## Instalação Python 3.10.9

**1.** Abra um terminal no jupyterhub;
**2.** Obtenha acesso a permissão de superusuário e depois vá para o seu diretório pessoal:

```bash
sudo su -

cd ~
```

E crie as seguintes as seguintes variáveis para o proxy alterando os termos USER e PASS para o seu ID de usuário e sua senha respectivamente:

```bash
export http_proxy=http://<USER>:<PASS>@proxy.inf.bndes.net:8080
export https_proxy=$http_proxy
```

Observação: Caracteres especiais na senha precisam ser alterados para o encoding correto, caso necessário verifique no seguinte link do [W3Schools](https://www.w3schools.com/tags/ref_urlencode.ASP)

**Tabela para referência rápida**

| Caracter    | Referência |
| -------- | ------- |
| !  | %21    |
| #  | %23    |
| $  | %24    |
| %  | %25    |
| &  | %26    |
| @  | %40    |


**3.** Atualize os pacotes do sistema:

```bash
yum update
```

Caso o yum update não esteja funcionando, esteja dando erro com o repo 'appstream', rode os seguinte código como root:
```bash
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
yum update -y
```



O tempo de espera pode variar de máquina para a máquina, assim, dependendo da máquina, pode demorar alguns minutos.

**4.** Instalação do Python:
Rode a seguinte linha de código:

```bash
wget https://www.python.org/ftp/python/3.10.9/Python-3.10.9.tgz
```

Irá baixar um arquivo .tgz, precisaremos descompactá-lo.  

```bash
tar -xvzf Python-3.10.9.tgz
```

Concluido a descompactação, entre no diretório e rode as seguintes linhas de comando:

```bash 
cd Python-3.10.9

./configure --enable-optimizations

make altinstall
```

Por fim, saia do super usuário.

```bash
exit
```

---

## Criação do Kernel (Poetry)

Para conseguir fazer o pré-processamento dos arquivos, utilizamos um notebook para fazer as operações, então para isso, criamos um kernel. A seguir tem um passo a passo de como criar um kernel, dado o sistema já preparado com o python instalado e com o poetry.

**1.** Caso não esteja, vá para o seu diretório no qual foi clonado o projeto:

```bash
cd ~/work/contrato360
```

**2.** Com o Poetry, basta verificar se os arquivos pyproject.toml e o poetry.lock estão no diretório e executar o seguinte comando:

```bash
poetry install
```

Para entrar no ambiente virtual basta fazer `poetry shell` e caso seja necessário sair `exit`. Com o `poetry install` já instalamos os pacotes necessários para criar um novo kernel.


**4.** Crie o Kernel, com o ambiente virtual do projeto ativado, é sugerido o nome 'Python-3-10-9':

```bash
python -m ipykernel install --name "Python-3-10-9" --user
```

Por mais que quando tentar executar um `!pip show openai` e nada aparecera, pois o python padrão não é o 3.10 que instalamos, caso faça o import não terá problema.


**5.** Montar uma pasta de rede para executar o programa que copiará os arquivos .pdf dos contratos para o jupyterhub. Ainda no terminal rode a seguinte linha de código:

```bash
montar_rede criar --diretorio_rede '\\bndes.net\bndes\Grupos\Contratos ATI e AGIR\ATI'
```

Após isso é possível executar o notebook, selecionando o kernel que foi criado.

## Execução do Streamlit (Poetry)

Após a execução do notebook que gera a database com os dados do banco de dados e dos pdfs, esses próximos passos mostrarão como executar a aplicação em streamlit.

**1.** Entre na pasta app do repositório, e  crie o ambiente virtual que será utilizado para executar a aplicação Streamlit.

```bash
poetry install
```


**2.** Entre em um terminal e vire usuário administrativo e execute os seguintes comandos export, lembrando novamente de alterar USER para o seu usuário e PASS para a sua senha:

```bash
sudo su -
export http_proxy=http://<USER>:<PASS>@proxy.inf.bndes.net:8080
export https_proxy=$http_proxy

# Observação, troque '<USER>' pelo seu usuário e '<PASS>' pela sua senha, porém cuidado com caracteres especiais
```


Além disso, na versão atual está sendo utilizado a **chave da Azure**, então será necessário delas, ou a sua própria. Para fazer uma execução tem duas formas, ou utilizamos a biblioteca python-dotenv que pelo próprio programa cria as variáveis de ambiente, sem precisar fazer o export pelo terminal, ou fazemos pelo terminal mesmo.

```bash
# Caso: OpenAI
export APP_SECRET_VALUE="sk-..."

# Caso: Azure OpenAI
export APP_SECRET_VALUE_KEY="..."
export APP_SECRET_VALUE_ENDPOINT="..."
export APP_SECRET_VALUE_DEPLOYMENT_KEY="..."

# Para verificar se o valor foi corretamente:
echo $APP_SECRET_VALUE
```

Caso venha usar sua chave da OpenAI tenha em mente que terá que alterar os módulos _AzureChatOpenIA_ e o _AzureOpenIAEmbeddings_, para a versão que não tenha _Azure_.


**3.** Entre no diretório do arquivo app.py pelo root que será executado com o streamlit e execute a seguinte linha de código:

```bash
/home/<USER>/.cache/pypoetry/virtualenvs/app<Complete com a tecla Tab>/bin/streamlit run app1.py --server.port 80
```

Será disponibilizado uma URL de rede que abrindo em uma nova guia, será possível já ver o streamlit em execução.

Caso já tenha alguém na porta 80, a porta 443 é uma opção alternativa.

---


**Links de passagem para Desenvolvimento**

[Pipeline Passagem DSV](https://jenkins.bndes.net/job/DTL-contrato360-DockerPipeline/build?delay=0sec)


