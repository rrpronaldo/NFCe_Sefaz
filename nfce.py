import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

regex_NCM = "NCM</label><span>(\\d{1,20})</span>"
regex_vlr_unit = "comercialização</label><span>(\\d{1,5},\\d{1,2})"

url = "https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-COM_2.asp?chaveNFe=43200702797437000123650210002356371109581040&HML=false&NFFCBA06010"
page = requests.post(url)
page

if page.status_code == 200:
    print("Achou")

    produtos = []

    soup = BeautifulSoup(page.content, 'html.parser')

    div_emitente = soup.find('div', id='Emitente')
    nfce_estabelecimento = re.findall('Social</label><span>([^>]*)</span>', div_emitente.decode_contents())
    nfce_estabelecimento_CNPJ = re.findall('CNPJ</label><span>([^>]*)</span>', div_emitente.decode_contents())

    div_nfe = soup.find('div', id='NFe').find('fieldset')
    nfce_data_emissao = re.findall('Emissão</label><span>(\\d{2}/\\d{2}/\\d{2,4})', div_nfe.decode_contents())
    nfce_valor_total = re.findall('Fiscal\s\s</label><span>(\d{1,5},\d{1,2})</span>', div_nfe.decode_contents())

    div_prod = soup.find('div', id='Prod')
    table_toggle_prod = div_prod.find_all('table', class_='toggle box')

    for prod_serv in table_toggle_prod:
        numero = prod_serv.find(class_="fixo-prod-serv-numero").get_text()
        descricao = prod_serv.find(class_="fixo-prod-serv-descricao").get_text()
        qtd = prod_serv.find(class_="fixo-prod-serv-qtd").get_text()
        unid_med = prod_serv.find(class_="fixo-prod-serv-uc").get_text()
        valor_total_prod = prod_serv.find(class_="fixo-prod-serv-vb").get_text()

        produtos.append([numero, descricao, qtd, unid_med, valor_total_prod])
    
    table_prod = div_prod.find_all('table', class_='toggable box')



    nfce_valores_unit = re.findall(regex_vlr_unit, div_prod.decode_contents())
    nfce_codigos_NCM = re.findall(regex_NCM, div_prod.decode_contents())

    retorno = pd.DataFrame(produtos, columns=['Numero_Item', 'Descricao', 'Qtd', 'Unid_med', 'Valor_Total_Prod'])
    retorno['Valores_Unit'] = nfce_valores_unit
    retorno['Codigo_NCM'] = nfce_codigos_NCM


    print(retorno)