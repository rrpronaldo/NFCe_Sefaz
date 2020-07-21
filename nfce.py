import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


def get_data(page):
    produtos = []
    regex_NCM = "NCM</label><span>(\\d{1,20})</span>"
    regex_vlr_unit = "comercialização</label><span>(\\d{1,5},\\d{1,2})"
    regex_estab = 'Social</label><span>([^>]*)</span>'
    regex_CNPJ = 'CNPJ</label><span>([^>]*)</span>'
    regex_data_emissao = 'Emissão</label><span>(\\d{2}/\\d{2}/\\d{2,4})'
    regex_valor_total = 'Fiscal\s\s</label><span>(\d{1,5},\d{1,2})</span>'

    soup = BeautifulSoup(page.content, 'html.parser')

    div_emitente = soup.find('div', id='Emitente')
    nfce_estabelecimento = re.findall(regex_estab, div_emitente.decode_contents())[0]
    nfce_estabelecimento_CNPJ = re.findall(regex_CNPJ, div_emitente.decode_contents())[0]

    div_nfe = soup.find('div', id='NFe').find('fieldset')
    nfce_data_emissao = re.findall(regex_data_emissao, div_nfe.decode_contents())[0]
    nfce_valor_total = re.findall(regex_valor_total, div_nfe.decode_contents())[0]

    div_prod = soup.find('div', id='Prod')
    table_toggle_prod = div_prod.find_all('table', class_='toggle box')

    for prod_serv in table_toggle_prod:
        #numero = prod_serv.find(class_="fixo-prod-serv-numero").get_text()
        descricao = prod_serv.find(class_="fixo-prod-serv-descricao").get_text()
        qtd = prod_serv.find(class_="fixo-prod-serv-qtd").get_text()
        unid_med = prod_serv.find(class_="fixo-prod-serv-uc").get_text()
        valor_total_prod = prod_serv.find(class_="fixo-prod-serv-vb").get_text()

        produtos.append([nfce_data_emissao,
                        nfce_valor_total,
                        nfce_estabelecimento_CNPJ,
                        nfce_estabelecimento,
                        descricao, 
                          qtd, 
                          unid_med, 
                          valor_total_prod])

    table_prod = div_prod.find_all('table', class_='toggable box')



    nfce_valores_unit = re.findall(regex_vlr_unit, div_prod.decode_contents())
    nfce_codigos_NCM = re.findall(regex_NCM, div_prod.decode_contents())

    retorno = pd.DataFrame(produtos, columns=['Data_Emissao',
                                              'Valor_Total_NF',
                                              'Estabelecimento_CNPJ',
                                              'Estabelecimento',
                                              'Descricao', 
                                              'Qtd', 
                                              'Unid_med', 
                                              'Valor_Total_Prod'])

    retorno['Valores_Unit'] = nfce_valores_unit
    retorno['Codigo_NCM'] = nfce_codigos_NCM

    return retorno




def main():
    cod_nfce = "43200794786456000172650040001632191501632194"
    cod_nfce2 = "43200702797437000123650210002356371109581040"
    url = "https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-COM_2.asp?chaveNFe="+ cod_nfce +"&HML=false&NFFCBA06010"
    
    print("[INFO] Connecting to NFCe URL ...")
    page = requests.post(url)
    
    if page.status_code == 200:
        data = get_data(page)
    else:
        print("Problema na conexão com a página do Sefaz: ", page.status_code)

    print(data)


if __name__ == '__main__':
    main()