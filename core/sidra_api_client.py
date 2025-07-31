# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET

class SidraApiClient:
    """
    Cliente para interagir com a API SIDRA do IBGE.
    Responsável por buscar e processar os dados da API.
    """

    def __init__(self, api_url):
        """
        Construtor.
        :param api_url: A URL completa da consulta da API SIDRA.
        """
        self.url = api_url

    def fetch_and_parse(self):
        """
        Busca os dados da URL e os processa.
        :return: Uma tupla contendo (dados_de_lookup, info_cabecalho) ou lança uma exceção em caso de erro.
        """
        xml_data = self._fetch_raw_data()
        if not xml_data:
            raise ValueError("Não foram recebidos dados XML válidos da API.")
        
        return self._parse_xml(xml_data)

    def _fetch_raw_data(self):
        """
        Realiza a requisição HTTP para a API.
        """
        try:
            headers = {'Accept': 'application/xml, text/xml'}
            response = requests.get(self.url, timeout=120, headers=headers)

            if response.status_code == 200:
                response.encoding = 'utf-8'
                response_text = response.text.strip()
                
                if response_text.startswith('<'):
                    return response_text
                else:
                    raise ConnectionError("A API não retornou XML, mesmo após ser solicitado.")
            else:
                response_text = response.text
                if "excedeu o limite" in response_text.lower():
                    raise ValueError("A consulta é muito grande e excedeu o limite de 50.000 valores da API.")
                else:
                    raise ConnectionError(f"Erro de requisição: {response.status_code} ({response.reason}).")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ocorreu um erro de conexão ao tentar acessar a API: {e}")

    def _parse_xml(self, xml_data):
        """
        Processa a string XML para extrair os dados e o cabeçalho.
        """
        parser = ET.XMLParser(encoding="utf-8")
        root = ET.fromstring(xml_data.encode('utf-8'), parser=parser)
        
        ns = {'ibge': 'http://schemas.datacontract.org/2004/07/IBGE.BTE.Tabela'}
        all_nodes = root.findall('.//ibge:ValorDescritoPorSuasDimensoes', ns)
        
        if not all_nodes:
            raise ValueError("Nenhum dado encontrado no XML (tag 'ValorDescritoPorSuasDimensoes').")

        header_node = all_nodes[0]
        data_rows_nodes = all_nodes[1:]
        header_map = {child.tag.split('}')[-1]: child.text for child in header_node}
        
        geo_code_field = None
        for i in range(1, 10):
            dim_code, dim_name = f'D{i}C', f'D{i}N'
            if header_map.get(dim_name) and any(k in header_map[dim_name].lower() for k in ['município', 'unidade da federação']):
                geo_code_field = dim_code
                break
        
        if not geo_code_field:
            raise ValueError("Não foi possível identificar a coluna de código geográfico no cabeçalho do XML.")
        
        data_rows = [{child.tag.split('}')[-1]: child.text for child in node} for node in data_rows_nodes]
        if not data_rows:
            return {}, header_map # Retorna dados vazios mas com cabeçalho se a consulta for válida mas sem resultados

        lookup = {}
        for row in data_rows:
            geo_code = row.get(geo_code_field)
            value = row.get('V')
            if geo_code and value and value.strip() not in ['...', '-']:
                normalized_sidra_key = str(geo_code).strip()
                if normalized_sidra_key not in lookup:
                    lookup[normalized_sidra_key] = {}
                
                class_key_parts = []
                for i in range(1, 10):
                    class_name_field = f'D{i}N'
                    if class_name_field in header_map and header_map[class_name_field] and f'D{i}C' != geo_code_field:
                         class_name = row.get(class_name_field)
                         if class_name:
                            class_key_parts.append(class_name)
                
                class_key = " ".join(class_key_parts) if class_key_parts else header_map.get('D2N', 'Valor')
                lookup[normalized_sidra_key][class_key] = value
        
        return lookup, header_map
