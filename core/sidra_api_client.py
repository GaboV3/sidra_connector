import pandas as pd
import requests
import xml.etree.ElementTree as ET
import re

class SidraApiClient:
    """
    Cliente para interagir com a API do SIDRA para obter dados de tabelas.
    """

    def __init__(self, table_query: any):
        """
        Inicializa o cliente da API do SIDRA.

        :param table_query: O código da tabela (int) ou a URL completa da API do SIDRA (str).
        """
        self.full_query_url = None
        if isinstance(table_query, str) and table_query.startswith('http'):
            # Se uma URL completa for fornecida, armazena-a.
            self.full_query_url = table_query
            match = re.search(r'/t/(\d+)', table_query)
            if match:
                self.table_code = int(match.group(1))
            else:
                raise ValueError(f"Não foi possível extrair o código da tabela da URL: {table_query}")
        else:
            # Caso contrário, trata como um código de tabela.
            self.table_code = int(table_query)

        self.base_url = f"https://apisidra.ibge.gov.br/values/t/{self.table_code}"


    def fetch_and_parse(self, params: dict = None) -> pd.DataFrame:
        """
        Busca e analisa dados da API do SIDRA com base nos parâmetros fornecidos.

        :param params: Um dicionário de parâmetros para a consulta da API (ignorado se uma URL completa foi usada na inicialização).
        :return: Um DataFrame do pandas contendo os dados.
        """
        # Se uma URL completa foi fornecida na inicialização, use-a diretamente.
        if self.full_query_url:
            final_url = self.full_query_url
        else:
            # Caso contrário, construa a URL a partir dos parâmetros.
            if params is None:
                params = {}
            
            sanitized_params = {k: str(v).replace(" ", "") for k, v in params.items()}

            final_url = self.base_url
            if sanitized_params:
                path_params = "/".join([f"{k}/{v}" for k, v in sanitized_params.items()])
                final_url = f"{self.base_url}/{path_params}"

        response = requests.get(final_url)
        response.raise_for_status()  # Lança um erro para respostas com status ruins
        
        # O SIDRA retorna XML quando o formato não é especificado
        if response.headers.get('Content-Type', '').startswith('application/xml'):
            return self._parse_xml(response.text)
        
        # Assume JSON para outros casos (embora o padrão seja XML)
        data = response.json()
        if not data or len(data) <= 1:
            return pd.DataFrame()
        
        header = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=header.values())
        return df

    def _parse_xml(self, xml_string: str) -> pd.DataFrame:
        """
        Analisa uma string XML da resposta da API do SIDRA e a converte em um DataFrame.

        :param xml_string: A string XML a ser analisada.
        :return: Um DataFrame do pandas contendo os dados analisados.
        """
        root = ET.fromstring(xml_string)
        
        namespace = {'ns': 'http://schemas.datacontract.org/2004/07/IBGE.BTE.Tabela'}
        all_rows = []
        
        header_element = root.find('ns:ValorDescritoPorSuasDimensoes', namespace)
        if header_element is None:
            return pd.DataFrame()

        header_map = {child.tag.split('}')[-1]: child.text for child in header_element}
        
        data_elements = root.findall('ns:ValorDescritoPorSuasDimensoes', namespace)[1:]
        
        for elem in data_elements:
            row_data = {header_map[child.tag.split('}')[-1]]: child.text for child in elem}
            all_rows.append(row_data)
            
        if not all_rows:
            return pd.DataFrame()

        df = pd.DataFrame(all_rows)

        # Identifica a coluna de código geográfico dinamicamente
        geo_code_col = None
        
        # Lista abrangente de todos os níveis territoriais do IBGE para garantir a detecção
        niveis_geograficos = [
            'brasil',
            'grande região',
            'unidade da federação',
            'região metropolitana',
            'região integrada de desenvolvimento',
            'microrregião geográfica',
            'mesorregião geográfica',
            'região geográfica imediata',
            'região geográfica intermediária',
            'município',
            'distrito',
            'subdistrito',
            'bairro',
            'setor censitário'
        ]

        for i in range(1, 10): # Verifica as dimensões de D1 a D9
            dim_name = f'D{i}N'
            dim_code = f'D{i}C'

            # Verifica se o nome da dimensão corresponde a algum nível geográfico conhecido
            if header_map.get(dim_name) and any(k in header_map[dim_name].lower() for k in niveis_geograficos):
                geo_code_col = header_map.get(dim_code)
                break

        if geo_code_col is None:
            raise ValueError("Erro: Não foi possível identificar a coluna de código geográfico no cabeçalho do XML.")
        
        # Renomeia a coluna de código geográfico para um nome padrão para facilitar a junção
        if geo_code_col in df.columns:
            df.rename(columns={geo_code_col: 'geo_code'}, inplace=True)
        
        # --- INÍCIO DA MODIFICAÇÃO ---
        # Adiciona um log de depuração para mostrar a estrutura do DataFrame retornado.
        # Isto ajuda a depurar erros de "unpacking" no código que chama esta função.
        print("--- Depuração SidraApiClient: DataFrame Criado ---")
        print(df.head())
        print("-------------------------------------------------")
        # --- FIM DA MODIFICAÇÃO ---

        return df
