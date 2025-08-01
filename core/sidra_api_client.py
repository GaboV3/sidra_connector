import pandas as pd
import requests
import xml.etree.ElementTree as ET
import re

try:
    from qgis.core import QgsMessageLog, Qgis
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False

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
            self.full_query_url = table_query
            match = re.search(r'/t/(\d+)', table_query)
            if match:
                self.table_code = int(match.group(1))
            else:
                raise ValueError(f"Não foi possível extrair o código da tabela da URL: {table_query}")
        else:
            self.table_code = int(table_query)

        self.base_url = f"https://apisidra.ibge.gov.br/values/t/{self.table_code}"


    def fetch_and_parse(self, params: dict = None) -> tuple:
        """
        Busca e analisa dados da API do SIDRA com base nos parâmetros fornecidos.

        :param params: Um dicionário de parâmetros para a consulta da API (ignorado se uma URL completa foi usada na inicialização).
        :return: Uma tupla (sidra_data_dict, header_info) onde sidra_data_dict é um dicionário de lookup e header_info contém metadados.
        """

        if self.full_query_url:
            final_url = self.full_query_url
        else:
            if params is None:
                params = {}
            
            sanitized_params = {k: str(v).replace(" ", "") for k, v in params.items()}

            final_url = self.base_url
            if sanitized_params:
                path_params = "/".join([f"{k}/{v}" for k, v in sanitized_params.items()])
                final_url = f"{self.base_url}/{path_params}"

        try:
            response = requests.get(final_url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Timeout na requisição à API SIDRA: {final_url}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Erro de conexão com a API SIDRA: {final_url}")
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(f"Erro HTTP na API SIDRA: {e.response.status_code} - {final_url}")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Erro na requisição à API SIDRA: {e}")
        
        if response.headers.get('Content-Type', '').startswith('application/xml'):
            df = self._parse_xml(response.text)
        else:
            data = response.json()
            if not data or len(data) <= 1:
                return {}, {}
            
            header = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=header.keys())
            
            column_mapping = {k: v for k, v in header.items()}
            if QGIS_AVAILABLE:
                QgsMessageLog.logMessage(f"Mapeamento de colunas: {column_mapping}", "SIDRA Connector", Qgis.Info)
        
        sidra_data_dict, header_info = self._convert_dataframe_to_dict(df)
        return sidra_data_dict, header_info

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

        geo_code_col = None
        
        # Lista de todos os níveis territoriais do IBGE
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

        for i in range(1, 10):
            dim_name = f'D{i}N'
            dim_code = f'D{i}C'

            if header_map.get(dim_name) and any(k in header_map[dim_name].lower() for k in niveis_geograficos):
                geo_code_col = header_map.get(dim_code)
                break

        if geo_code_col is None:
            raise ValueError("Erro: Não foi possível identificar a coluna de código geográfico no cabeçalho do XML.")
        
        if geo_code_col in df.columns:
            df.rename(columns={geo_code_col: 'geo_code'}, inplace=True)
        
        sidra_data_dict, header_info = self._convert_dataframe_to_dict(df)
        return sidra_data_dict, header_info

    def _convert_dataframe_to_dict(self, df: pd.DataFrame) -> tuple:
        """
        Converte um DataFrame em um dicionário de lookup e extrai informações do cabeçalho.
        
        :param df: DataFrame com os dados do SIDRA
        :return: Tupla (sidra_data_dict, header_info)
        """
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(f"Iniciando conversão do DataFrame. Shape: {df.shape}", "SIDRA Connector", Qgis.Info)
            QgsMessageLog.logMessage(f"Colunas disponíveis: {list(df.columns)}", "SIDRA Connector", Qgis.Info)
        
        if df.empty:
            if QGIS_AVAILABLE:
                QgsMessageLog.logMessage("DataFrame vazio recebido da API SIDRA", "SIDRA Connector", Qgis.Warning)
            return {}, {}
        
        sidra_data_dict = {}
        header_info = {}
        
        excluded_cols = {
            'geo_code', 'D1C', 'D1N', 'D2C', 'D2N', 'D3C', 'D3N', 'D4C', 'D4N',
            'NC', 'NN', 'MC', 'MN'
        }
        
        value_cols = []
        if 'V' in df.columns:
            value_cols.append('V')
        
        for col in df.columns:
            if col not in excluded_cols and col not in value_cols:
                value_cols.append(col)
        
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(f"Colunas de valores identificadas: {value_cols}", "SIDRA Connector", Qgis.Info)
        
        if not df.empty:
            first_row = df.iloc[0]
            for col in df.columns:
                if col.endswith('N'):
                    header_info[col] = first_row[col] if pd.notna(first_row[col]) else col
        
        geo_code_col = None
        
        if 'geo_code' not in df.columns:
            if QGIS_AVAILABLE:
                QgsMessageLog.logMessage("Coluna 'geo_code' não encontrada. Tentando identificar coluna geográfica...", "SIDRA Connector", Qgis.Warning)
            
            if 'D1C' in df.columns:
                geo_code_col = 'D1C'
                if QGIS_AVAILABLE:
                    QgsMessageLog.logMessage("Usando coluna 'D1C' como código geográfico", "SIDRA Connector", Qgis.Info)
            else:
                geo_candidates = [col for col in df.columns if col.endswith('C') and any(dim in col for dim in ['D1', 'D2', 'D3', 'D4'])]
                if geo_candidates:
                    geo_code_col = geo_candidates[0]
                    if QGIS_AVAILABLE:
                        QgsMessageLog.logMessage(f"Usando coluna '{geo_code_col}' como código geográfico", "SIDRA Connector", Qgis.Info)
                else:
                    if QGIS_AVAILABLE:
                        QgsMessageLog.logMessage("Nenhuma coluna geográfica identificada", "SIDRA Connector", Qgis.Critical)
                    return {}, header_info
            
            df = df.rename(columns={geo_code_col: 'geo_code'})
        else:
            geo_code_col = 'geo_code'
        
        rows_processed = 0
        
        variable_column = None
        variable_candidates = ['D4N', 'D3N', 'D2N', 'D5N', 'D6N', 'D7N']
        
        for candidate in variable_candidates:
            if candidate in df.columns:
                unique_values = df[candidate].nunique()
                if unique_values > 1:
                    variable_column = candidate
                    break
        
        has_value_column = 'V' in df.columns       # Valor
        
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(f"Coluna de variável identificada: {variable_column}", "SIDRA Connector", Qgis.Info)
            QgsMessageLog.logMessage(f"Tem coluna de valor (V): {has_value_column}", "SIDRA Connector", Qgis.Info)
        
        if variable_column and has_value_column:
            for _, row in df.iterrows():
                if 'geo_code' in row and pd.notna(row['geo_code']):
                    geo_code = str(row['geo_code']).strip()
                    variable_name = str(row[variable_column]).strip() if pd.notna(row[variable_column]) else 'Valor'
                    value = row['V']
                    
                    if geo_code not in sidra_data_dict:
                        sidra_data_dict[geo_code] = {}
                    
                    try:
                        if pd.notna(value):
                            value_str = str(value).replace(',', '.')
                            if value_str.replace('.', '').replace('-', '').isdigit():
                                processed_value = float(value_str)
                            else:
                                processed_value = str(value)
                        else:
                            processed_value = None
                    except (ValueError, TypeError):
                        processed_value = str(value) if pd.notna(value) else None

                    var_key = variable_name
                    counter = 1
                    while var_key in sidra_data_dict[geo_code]:
                        var_key = f"{variable_name}_{counter}"
                        counter += 1
                    
                    sidra_data_dict[geo_code][var_key] = processed_value
                    rows_processed += 1
        
        else:
            if QGIS_AVAILABLE:
                QgsMessageLog.logMessage("Usando lógica de fallback - sem agrupamento por variável", "SIDRA Connector", Qgis.Info)
            
            for _, row in df.iterrows():
                if 'geo_code' in row and pd.notna(row['geo_code']):
                    geo_code = str(row['geo_code']).strip()
                    
                    row_data = {}
                    for col in value_cols:
                        if pd.notna(row[col]):
                            try:
                                value_str = str(row[col]).replace(',', '.')
                                if value_str.replace('.', '').replace('-', '').isdigit():
                                    row_data[col] = float(value_str)
                                else:
                                    row_data[col] = str(row[col])
                            except (ValueError, TypeError):
                                row_data[col] = str(row[col])
                    
                    if row_data:
                        sidra_data_dict[geo_code] = row_data
                        rows_processed += 1
        
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(f"Conversão concluída: {len(sidra_data_dict)} registros geográficos, {rows_processed} linhas processadas", "SIDRA Connector", Qgis.Info)
            if len(sidra_data_dict) > 0:
                sample_key = next(iter(sidra_data_dict.keys()))
                sample_data = sidra_data_dict[sample_key]
                variables = list(sample_data.keys())
                QgsMessageLog.logMessage(f"Exemplo de dados: geo_code={sample_key}, variáveis={variables}", "SIDRA Connector", Qgis.Info)
        
        return sidra_data_dict, header_info
