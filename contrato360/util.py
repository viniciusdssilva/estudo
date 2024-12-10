import os
import shutil
import re


rede = '/mnt/bndes_grupos_contratos_ati_e_agir_ati'


GERENCIAS = ['DEGAT',
             'DESET_GEAT',
             'DESET_GINF',
             'DESET_GMAIS',
             'DESET_GPRO',
             'DESIS1',
             'DESIS2',
             'DESIS3',
             'DESIS4']


def verifica_destino_pdf():
    if not os.path.exists('contratos/pdf'):
        os.makedirs('contratos/pdf')
    else:
        print('Pasta já existe!')


def verifica_destino_txt():
    if not os.path.exists('contratos/txt'):
        os.makedirs('contratos/txt')
    else:
        print('Pasta já existe!')


def verifica_destino_json():
    if not os.path.exists('contratos/json'):
        os.makedirs('contratos/json')
    else:
        print('Pasta já existe!')
    

def padroniza_nome_contrato(nome_contrato: str):
    partes = nome_contrato.split(' - ')
    if '-' in partes[0]:
        limpa_hifen = partes[0].replace('-',' ')
        numero_contrato = limpa_hifen.split(' ')[2]
        ano_contrato = limpa_hifen.split(' ')[-1]
        empresa_servico = partes[-1].split('.')[0]
        novo_nome = f"Contrato OCS {numero_contrato}_{ano_contrato} - {empresa_servico}.pdf"

    elif len(partes) > 2:
        numero_contrato = partes[0].split(' ')[2]
        ano_contrato = partes[0].split(' ')[-1]
        empresa_servico_pdf = partes[-2] + ' ' + partes[-1]
        empresa_servico = empresa_servico_pdf.split('.')[0]
        novo_nome = f"Contrato OCS {numero_contrato}_{ano_contrato} - {empresa_servico}.pdf"

    else:
        numero_contrato = partes[0].split(' ')[2]
        ano_contrato = partes[0].split(' ')[-1]
        empresa_servico = partes[-1].split('.')[0]
        novo_nome = f"Contrato OCS {numero_contrato}_{ano_contrato} - {empresa_servico}.pdf"
    return novo_nome


anos_quero = ['2021',
              '2022',
              '2023',
              '2024']

palavras_quero = ['contrato',
                  'ocs']

palavras_nao_quero = ['aditivo',
                      'dif',
                      'apostilamento',
                      'apólice',
                      'apolice',
                      'anexo',
                      'relatorio',
                      'início',
                      'social',
                      'alteração',
                      'termo',
                      'treinamento',
                      'formalização',
                      'extrato',
                      'bndes - contrato 1.pdf',
                      'email',
                      'sc',
                      '244_2023',
                      'informação',
                      '_ res_ res_ res_ res_ [bndes]',
                      'ajustes',
                      'proposta',
                      'carta']


def copia_e_move(caminho_contratos, arquivo, pasta_ocs):
    shutil.copy(os.path.join(caminho_contratos, arquivo), 'contratos/pdf')
    novo_nome = padroniza_nome_contrato(f'Contrato {pasta_ocs}.pdf')
    shutil.move(os.path.join('contratos/pdf', arquivo), os.path.join('contratos/pdf', novo_nome))


def download():
    for gerencia in GERENCIAS:
        caminho_gerencia = os.path.join(rede, gerencia)
        if os.path.exists(caminho_gerencia):
            for pasta_ocs in os.listdir(caminho_gerencia):
                if pasta_ocs.startswith("OCS") and any(ocs_quero in pasta_ocs for ocs_quero in anos_quero) and pasta_ocs != 'OCS 053 2023 - Fast Help (SEP) - Atalho.lnk':
                    caminho_ocs = os.path.join(caminho_gerencia, pasta_ocs)
                    nome_contrato = pasta_ocs
                    if "Contratos e aditivos digitalizados" in os.listdir(caminho_ocs):
                        caminho_contratos = os.path.join(caminho_ocs, "Contratos e aditivos digitalizados")
                        if os.path.exists(caminho_contratos):
                            for arquivo in os.listdir(caminho_contratos):
                                if os.path.isfile(os.path.join(caminho_contratos, arquivo)) and arquivo.lower().endswith('.pdf') and any(pq in arquivo.lower() for pq in palavras_quero) and not any(pnq in arquivo.lower() for pnq in palavras_nao_quero):
                                    print(f'Processando o arquivo: {arquivo}')
                                    print(pasta_ocs)
                                    try:
                                        copia_e_move(caminho_contratos, arquivo, pasta_ocs)
                                    except Exception as e:
                                        print("Erro! Foi no arquivo {} e erro {}".format(arquivo, e))

                                    # i += 1

                    elif "Contrato e aditivos digitalizados" in os.listdir(caminho_ocs):
                        caminho_contratos = os.path.join(caminho_ocs, "Contrato e aditivos digitalizados")
                        if os.path.exists(caminho_contratos):
                            for arquivo in os.listdir(caminho_contratos):
                                if os.path.isfile(os.path.join(caminho_contratos, arquivo)) and arquivo.lower().endswith('.pdf') and any(pq in arquivo.lower() for pq in palavras_quero) and not any(pnq in arquivo.lower() for pnq in palavras_nao_quero):
                                    print(f'Processando o arquivo: {arquivo}')
                                    print(pasta_ocs)
                                    try:
                                        copia_e_move(caminho_contratos, arquivo, pasta_ocs)
                                    except Exception as e:
                                        print("Erro! Foi no arquivo {} e erro {}".format(arquivo, e))                                   
                    else:
                        caminho_contratos = caminho_ocs  # Este caminho é redundante aqui
                        for arquivo in os.listdir(caminho_contratos):
                            if os.path.isfile(os.path.join(caminho_contratos, arquivo)) and arquivo.lower().endswith('.pdf') and any(pq in arquivo.lower() for pq in palavras_quero) and not any(pnq in arquivo.lower() for pnq in palavras_nao_quero):
                                print(f'Processando o arquivo: {arquivo}')
                                print(pasta_ocs)
                                try:
                                    copia_e_move(caminho_contratos, arquivo, pasta_ocs)
                                except Exception as e:
                                    print("Erro! Foi no arquivo {} e erro {}".format(arquivo, e))


def download_contratos():
    verifica_destino_pdf()
    download()



    
    
# ===================================PROCESSAMENTO DE PDF===================================================

dicionario = {
    # 'Contrato OCS 005_2024 - Optimus System.pdf': (6, None, 6), # Não contém cláusulas
    'Contrato OCS 008_2022 - Hitachi Vantara Storage.pdf': (7, None, 22),
    'Contrato OCS 011_2022 - Zoom (Storage Huawei).pdf': (7, None, 22),
    'Contrato OCS 011_2023 - Multiplus (BIG-IP).pdf': (3, None, 17),
    'Contrato OCS 012_2022 - VS Data Storages de backup.pdf': (7, None, 22),
    'Contrato OCS 018_2023 - Asper.pdf': (5, None, 22),
    'Contrato OCS 023_2024 - Soluti (e-CPF).pdf': (5, -5, 18),
    'Contrato OCS 026_2024 - Certificados INFOCONV, eSocial e e-CNPJ (Soluti).pdf': (4, -6, 17),
    'Contrato OCS 027_2024 - SOLUTI Certificados digitais SPB e OpF.pdf': (4, None, 17),
    'Contrato OCS 028_2022 - Telsinc.pdf': (7, None, 20),
    'Contrato OCS 028_2024 - G4F SOLUCOES CORPORATIVAS LTDA.pdf': (4, None, 27),
    'Contrato OCS 032_2024 - VSDATA Suporte MQ.pdf': (8, -6, 21),
    'Contrato OCS 035_2022 - Claro.pdf': (5, None, 23),
    # 'Contrato OCS 035_2024 - PCaaS (K2A).pdf': (6, -5, 20), #Não contém cláusulas
    'Contrato OCS 042_2021 - TIVIT (Data Center Alternativo).pdf': (17, None, 19),
    'Contrato OCS 043_2021 - Rational.pdf': (14, None, 19),
    'Contrato OCS 044_2022 - SAP IDM Conectores.pdf': (7, -2, 19),
    'Contrato OCS 046_2021 - Ingram (Suporte Notes).pdf': (12, None, 18),
    'Contrato OCS 046_2024 - SENSEDIA S.pdf': (8, None, 21),
    'Contrato OCS 048_2022 - TGV (ETL).pdf': (5, None, 20),
    'Contrato OCS 050_2021 - IBM Connect Direct Ortec.pdf': (21, -3, 17),
    'Contrato OCS 051_2024 - Certificados Wildcard e servidor específico (Certisign).pdf': (4, None, 22),
    # 'Contrato OCS 060_2020 - RTM (FinanceNET).pdf': (None, None, None), # Contrato é uma imagem.
    'Contrato OCS 065_2021 - SOFTON.pdf': (21, -3, 20),
    # 'Contrato OCS 076_2023 - Plataforma de Integração (IBM).pdf': (3,-4), # Muitas quebras de linha, e paginação não identificada na primeira página.
    'Contrato OCS 077_2021 - Murah.pdf': (37, -2, 21),
    # 'Contrato OCS 085_2020 - Mainframe z14.pdf': (,), : () Imagem de contrato do Santander.
    'Contrato OCS 099_2021 - Heiliger Open Banking.pdf': (13, None, 20), 
    'Contrato OCS 105_2022 - SAP Active Attention.pdf': (7, -2, 18),
    'Contrato OCS 112_2021 - Oi (Link Bloomberg DC principal).pdf': (12, None, 21), 
    'Contrato OCS 113_2021 - Algar (Link Bloomberg DC alternativo).pdf': (12, None, 21),
    'Contrato OCS 115_2021 - Decision (Suporte Switches SAN).pdf': (13, None, 20),
    'Contrato OCS 118_2022 - Algar (0800).pdf': (8, None, 20),
    'Contrato OCS 120_2020 - Art Stars.pdf': (11, None, 12),
    # 'Contrato OCS 124_2021 - Sai do Papel.pdf': (8, -2, None),  # Formatação discrepante
    'Contrato OCS 132_2023 - AboutNet Gateway WEB.pdf': (4, -1, 23),
    'Contrato OCS 134_2023 - Daten.pdf': (5, -2, 18),
    'Contrato OCS 136_2020 - Zoom Tecnologia (Service Desk).pdf': (16, -1, 27),
    'Contrato OCS 147_2022 - ALCTEL.pdf': (8, None, 23),
    'Contrato OCS 150_2020 - BRQ RedHat.pdf': (12, None, 17),
    'Contrato OCS 150_2022 - Zoom SW Core.pdf': (8, None, 24),
    'Contrato OCS 159_2021 - IBM AVP.pdf': (8, None, 19),
    'Contrato OCS 159_2021 - IBM Content Manager.pdf': (8, None, 19),
    'Contrato OCS 159_2022 - Hardlink (Suporte DAS).pdf': (8, None, 24),
    'Contrato OCS 160_2022 - Suporte servidores (Unitech).pdf': (8, None, 20),
    'Contrato OCS 167_2023 - BTV notebooks Positivo.pdf': (4, None, 18),
    'Contrato OCS 173_2022 - Ingram (Windows Server).pdf': (9, None, 21),
    'Contrato OCS 174_2022 - Algar (Central de Atendimento).pdf': (8, None, 20),
    'Contrato OCS 179_2021 - ZIVA (Solução unificada LAN e WLAN).pdf': (8, None, 21),
    'Contrato OCS 185_2020 - Tecno-IT (CFTV).pdf': (13, None, 16), 
    'Contrato OCS 189_2022 - Algar STFC Unificado.pdf': (7, None, 20),
    'Contrato OCS 190_2020 - DB3 (links Internet).pdf': (15, None, 17),
    'Contrato OCS 195_2022 - Brasoftware (SQL Server).pdf': (7, None, 21),
    'Contrato OCS 200_2020 - ESEC.pdf': (11, None, 16),
    # 'Contrato OCS 205_2020 - Suporte SAP BO.pdf': (, , ),
    'Contrato OCS 206_2020 - BRy.pdf': (19, None, 18),
    'Contrato OCS 218_2023 - Lotus ICT.pdf': (4, None, 25),
    'Contrato OCS 221_2021 - Intersoft (Suporte e licenças VMware).pdf': (7, None, 19),
    # 'Contrato OCS 226_2021 - Telmex.pdf': (, , ),
    'Contrato OCS 231_2020 - Microstrategy.pdf': (7, None, 17),
    'Contrato OCS 259_2020 - Mundivox (links Internet).pdf': (12, None, 18),
    'Contrato OCS 261_2020 - Teletex (Websphere).pdf': (16, None, 19),
    'Contrato OCS 278_2023 - ORACLE.pdf': (8, None, 21),
    # 'Contrato OCS 294_2023 - CPqD.pdf': (, , ),
    'Contrato OCS 319_2022 - Suporte NAS (Celerit).pdf': (8, None, 19),
    'Contrato OCS 321_2023 - Software AG.pdf': (4, None, 26),
    'Contrato OCS 338_2022 - RTM (SISBACEN).pdf': (5, None, 18),
    'Contrato OCS 342_2022 - VS Data (Suporte TSM).pdf': (7, None, 20),
    'Contrato OCS 343_2022 - HD Solucoes (WEBCAMs).pdf': (4, None, 21),
    'Contrato OCS 344_2022 - DADB (fones).pdf': (5, None, 20)
}

clausulas_regex = [
    r"CL(?:Á|A)USULA\s*PRIMEIR(?:O|A)\s*(?:-|–)\s*OBJETO",
    r"CL(?:Á|A)USULA\s*SEGUND(?:O|A)\s*(?:-|–)\s*VIG(?:E|Ê)NCIA",
    r"CL(?:Á|A)USULA\s*TERCEIR(?:O|A)\s*(?:-|–)\s*LOCAL,\s*PRAZO\s*E\s*CONDI(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*DE\s*EXECU(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DO\s*OBJETO",
    r"CL(?:Á|A)USULA\s*QUART(?:O|A)\s*(?:-|–)\s*(?:N(?:Í|I)VEIS\s*DE\s*SERVIÇO|RECEBIMENTO\s*DO\s*OBJETO|AJUSTES\s*DE\s*PAGAMENTOS)",
    r"CL(?:Á|A)USULA\s*QUINT(?:O|A)\s*(?:-|–)\s*(?:RECEBIMENTO\s*DO\s*OBJETO|PRE(?:C|Ç)O|GARANTIA\s*DOS\s*BENS\s*FORNECIDOS)",
    r"CL(?:Á|A)USULA\s*SEXT(?:O|A)\s*(?:-|–)\s*(?:PRE(?:Ç|C)O|PAGAMENTO|GARANTIA\s*DOS\s*BENS\s*FORNECIDOS)",
    r"CL(?:Á|A)USULA\s*S(?:É|E)TIM(?:O|A)\s*(?:-|–)\s*(?:PAGAMENTO|PRE(?:Ç|C)O|EQUIL(?:Í|I)BRIO\s*ECON(?:Ô|O)MICO(?:-|–)FINANC.?.?.?.?.?\s*DO\s*CONTRATO)",
    r"CL(?:Á|A)USULA\s*OITAV(?:O|A)\s*(?:-|–)\s*(?:PAGAMENTO|MATRIZ\s*DE\s*RISCOS|EQUIL(?:Í|I)BRIO\s*ECON(?:Ô|O)MICO(?:-|–)FINANCE.?.?.?.?.?\s*DO\s*CONTRATO)",
    r"CL(?:Á|A)USULA\s*NON(?:O|A)\s*(?:-|–)\s*(?:OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*D(?:O|A)\s*CONTRATAD(?:O|A)|MATRIZ\s*DE\s*RISCOS|EQUIL(?:Í|I)BRIO\s*ECON(?:Ô|O)MICO(?:-|–)FINANC.?.?.?.?.?\s*DO\s*CONTRATO|GARANTIA\s*CONTRATUAL)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*(?:-|–)\s*(?:GARANTIA\s*CONTRATUAL|MATRIZ\s*DE\s*RISCOS|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*D(?:O|A)\s*CONTRATAD(?:O|A)|CONDUTA\s*(?:É|E)TICA\s*D(?:O|A)\s*CONTRATAD(?:O|A)\s*E\s*DO\s*BNDES)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*PRIMEIR(?:O|A)\s*(?:-|–)\s*(?:SIGILO\s*DAS\s*INFORMA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES|GARANTIA\s*CONTRATUAL|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*D(?:O|A)\s*CONTR.?ATAD(?:O|A)|CONDUTA\s*(?:É|E)TICA\s*D(?:O|A)\s*CONTRATAD(?:O|A)\s*E\s*DO\s*BNDES)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*SEGUND(?:O|A)\s*(?:-|–)\s*(?:OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*TRABALHISTAS\sE\sPREVIDENCI(?:Á|A)RIAS\sD(?:O|A)\sCONTRATAD(?:O|A)|SIGILO\s*DAS\s*INFORMA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*DO\s*BNDES|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*D(?:O|A)\s*CONTR.?ATAD(?:O|A)|CONDUTA\s*(?:É|E)TICA\s*D(?:O|A)\s*CONTRATAD(?:O|A)\s*E\s*DO\s*BNDES)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*TERCEIR(?:O|A)\s*(?:-|–)\s*(?:CESS(?:Ã|A)O\s*DE\s*CONTRATO\s*OU\s*DE\s*CR(?:É|E)DITO,\s*SUCESS(?:Ã|A)O\s*CONTRATUAL\s*E\s*SUBCONTRATA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O|ACESSO\s*E\s*PROTE(?:ÇÃ|ÇA|CÃ|CA)O\s*DE\s*DADOS\s*PESSOAIS|SIGILO\s*DAS\s*INFORMA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*DO\s*BNDES|CONDUTA\s*(?:É|E)TICA\s*D(?:O|A)\s*CONTRATAD(?:O|A)\s*E\s*DO\s*BNDES)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*QUART(?:O|A)\s*(?:-|–)\s*(?:PENALIDADES|CESS(?:Ã|A)O\s*DE\s*CONTRATO\s*OU\s*DE\s*CR(?:É|E)DITO,\s*SUCESS(?:Ã|A)O\s*CONTRATUAL\s*E\s*SUBCONTRATA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O|ACESSO\s*E\s*PROTE(?:ÇÃ|ÇA|CÃ|CA)O\s*DE\s*DADOS\s*PESSOAIS|SIGILO\s*DAS\s*INFORMA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*DO\s*BNDES)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*QUINT(?:O|A)\s*(?:-|–)\s*(?:PENALIDADES|CESS(?:Ã|A)O\s*DE\s*CONTRATO\s*OU\s*DE\s*CR(?:É|E)DITO,\s*SUCESS(?:Ã|A)O\s*CONTRATUAL\s*E\s*SUBCONTRATA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O|ACESSO\s*E\s*PROTE(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DE\s*DADOS\s*PESSOAIS|ALTERA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*CONTRATUAIS|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*DO\s*BNDES|EQUIDADE\s*DE\s*G(?:Ê|E)NERO\s*E\s*VALORIZA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DA\s*DIVERSIDADE)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*SEXT(?:O|A)\s*(?:-|–)\s*(?:PENALIDADES|CESS(?:Ã|A)O\s*DE\s*CONTRATO\s*OU\s*DE\s*CR(?:É|E)DITO,\s*SUCESS(?:Ã|A)O\s*CONTRATUAL\s*E\s*SUBCONTRATA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O|CESS(?:Ã|A)O\s*DE\s*CONTRATO\s*OU\s*DE\s*CR(?:É|E)DITO,\s*SUCESS(?:Ã|A)O\s*CONTRATUAL|ALTERA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*CONTRATUAIS|OBRIGA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*DO\s*BNDES|EQUIDADE\s*DE\s*G(?:Ê|E)NERO\s*.*E\s*VALORIZA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DA\s*DIVERSIDADE|EXTIN(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DO\s*CONTRATO)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*S(?:E|É)TIM(?:O|A)\s*(?:-|–)\s*(?:PENALIDADES|CESS(?:Ã|A)O\s*DE\s*CONTRATO\s*OU\s*DE\s*CR(?:É|E)DITO,\s*SUCESS(?:Ã|A)O\s*CONTRATUAL\s*E\s*SUBCONTRATA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O|ALTERA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*CONTRATUAIS|EQUIDADE\s*DE\s*G(?:Ê|E)NERO\s*.*E\s*VALORIZA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DA\s*DIVERSIDADE|EXTIN(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DO\s*CONTRATO|DISPOSI(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*FINAIS)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*OITAV(?:O|A)\s*(?:-|–)\s*(?:PENALIDADES|CESS(?:Ã|A)O\s*DE\s*CONTRATO\s*OU\s*DE\s*CR(?:É|E)DITO,\s*SUCESS(?:Ã|A)O\s*CONTRATUAL\s*E\s*SUBCONTRATA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O|ALTERA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*CONTRATUAIS|EXTIN(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DO\s*CONTRATO|DISPOSI(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*FINAIS|FORO)",
    r"CL(?:Á|A)USULA\s*D(?:E|É)CIM(?:O|A)\s*NON(?:O|A)\s*(?:-|–)\s*(?:PENALIDADES|ALTERA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*CONTRATUAIS|EXTIN(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DO\s*CONTRATO|DISPOSI(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*FINAIS|FORO|ACESSO\s*E\s*PROTE(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DE\s*DADOS\s*PESSOAIS)",
    r"CL(?:Á|A)USULA\s*VIG(?:É|E)SIM(?:O|A)\s*(?:-|–)\s*(?:ALTERA(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*CONTRATUAIS|EXTIN(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DO\s*CONTRATO|DISPOSI(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*FINAIS|FORO|DIVULGA(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DE\s*DADOS\s*PESSOAIS)",
    r"CL(?:Á|A)USULA\s*VIG(?:É|E)SIM(?:O|A)\s*PRIMEIR(?:O|A)\s*(?:-|–)\s*(?:EXTIN(?:ÇÃ|ÇA|ÇÂ|CÃ|CA|CÂ)O\s*DO\s*CONTRATO|DISPOSI(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*FINAIS|FORO)",
    r"CL(?:Á|A)USULA\s*VIG(?:É|E)SIM(?:O|A)\s*SEGUND(?:O|A)\s*(?:-|–)\s*(?:DISPOSI(?:ÇÕ|ÇO|ÇÔ|CÕ|CO|CÔ)ES\s*FINAIS|FORO)",
    r"CL(?:Á|A)USULA\s*VIG(?:É|E)SIM(?:O|A)\s*TERCEIR(?:O|A)\s*(?:-|–)\s*FORO"
]


def pdf_to_text():
    from langchain_community.document_loaders import PyMuPDFLoader
    verifica_destino_txt()
    # indice_inicial, indice_final, num_de_pags_de_clausulas -> Valores dos índices pegos manualmente
    
    diretorio = 'contratos/pdf/'
    for documento, valor in dicionario.items():
        indice_inicial, indice_final, num_pags = valor
        loader = PyMuPDFLoader(diretorio + documento)
        print(documento[:-4])
        print('==========================================')
        data = loader.load()

        with open('contratos/txt/{}.txt'.format(documento[:-4]), 'w') as f:
            n = 0
            for page in data:
                if n <= num_pags:
                    pagina_formatada = ''.join(page.page_content.split('\n')[indice_inicial:indice_final])
                    f.write(pagina_formatada)
                else:
                    continue
                n += 1


def text_to_json():
    import json
    verifica_destino_json()
    contratos = [f for f in os.listdir('contratos/txt') if f.endswith('.txt')]
    
    for documento in contratos:
        print('=========================================================')
        print(documento)
        fim = False
        #  print('=========================================================')
        with open('contratos/txt'+'/'+documento, 'r') as f:
            conteudo = f.readlines()
        texto = conteudo[0]
        
        for padrao in clausulas_regex:
            correspondencia = re.findall(padrao, texto)
            # print(correspondencia)
            if len(correspondencia) == 1:
                # print(correspondencia)
                texto = f"\n\n{correspondencia[0]}\n\n".join(texto.split(correspondencia[0]))
                if "FORO" in correspondencia[0]:
                    fim = True
            if len(correspondencia) != 1 and not fim:
                print("Algo de errado com as clausulas do documento {}".format(documento))
                continue

        texto = texto.split('CLÁUSULA')
        for ind in range(len(texto)):
            if ind > 0:
                texto[ind] = 'CLÁUSULA{}'.format(texto[ind])

        dicionario = {}
        for ind in range(len(texto)):
            if ind == 0:
                dicionario["INTRODUÇÃO"] = texto[ind]
            else:
                # print(elem.split('\n\n'))
                chave, valor = texto[ind].split('\n\n')[:2]
                # print(chave +'<--> '+ valor)
                dicionario[chave] = valor
            # print('---------------------------------------------')
        # print(dicionario)

        with open('contratos/json'+'/'+documento[:-4]+'.json', 'w') as file:
            json.dump(dicionario, file, indent=4, ensure_ascii=False)


def processa_pdf_para_json():
    pdf_to_text()
    text_to_json()











