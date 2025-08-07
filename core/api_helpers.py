# -*- coding: utf-8 -*-
"""
Módulo com funções auxiliares para comunicação com a API do SIDRA.
"""

import requests
import json
from qgis.core import QgsMessageLog, Qgis

def get_metadata_from_api(tabela_id):
    """
    Busca os metadados (a estrutura completa) de uma tabela diretamente da API do SIDRA.
    
    Args:
        tabela_id (str): ID da tabela do SIDRA
        
    Returns:
        dict: Metadados da tabela em formato JSON ou None em caso de erro
    """
    url = f"https://sidra.ibge.gov.br/Ajax/JSon/Tabela/1/{tabela_id}?versao=-1"
    
    QgsMessageLog.logMessage(f"Buscando metadados para a tabela {tabela_id}...", "SIDRA Connector", Qgis.Info)
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        QgsMessageLog.logMessage("Metadados recebidos com sucesso.", "SIDRA Connector", Qgis.Info)
        return response.json()
        
    except requests.exceptions.HTTPError as errh:
        error_msg = f"Erro HTTP: {errh}. Verifique se o código da tabela '{tabela_id}' está correto e disponível."
        QgsMessageLog.logMessage(error_msg, "SIDRA Connector", Qgis.Critical)
        
    except requests.exceptions.RequestException as err:
        error_msg = f"Erro de conexão: {err}"
        QgsMessageLog.logMessage(error_msg, "SIDRA Connector", Qgis.Critical)
        
    except json.JSONDecodeError:
        error_msg = "Erro: A resposta da API não é um JSON válido."
        QgsMessageLog.logMessage(error_msg, "SIDRA Connector", Qgis.Critical)
    
    return None


def montar_url_interativa(tabela_id, nivel_geo, variaveis, periodos, classificacoes_selecionadas):
    """
    Monta a string final da URL da API do SIDRA para buscar valores.
    
    Args:
        tabela_id (str): ID da tabela
        nivel_geo (tuple): Tupla com (id, nome, sigla) do nível geográfico
        variaveis (list): Lista de tuplas com variáveis selecionadas
        periodos (list): Lista de tuplas com períodos selecionados  
        classificacoes_selecionadas (dict): Dicionário com classificações e categorias
        
    Returns:
        str: URL completa da API do SIDRA
    """
    base_url = "https://apisidra.ibge.gov.br/values"
    
    # Tabela
    url_parts = [f"/t/{tabela_id}"]
    
    # Nível Geográfico (n) e Territórios (all para todos)
    url_parts.append(f"/n{nivel_geo[0]}/all")
    
    # Variáveis (v)
    ids_variaveis = ",".join([str(v[0]) for v in variaveis])
    url_parts.append(f"/v/{ids_variaveis}")
    
    # Períodos (p)
    codigos_periodos = ",".join([str(p[2]) for p in periodos])
    url_parts.append(f"/p/{codigos_periodos}")
    
    # Classificações (c) e Categorias
    for class_id, cat_ids in classificacoes_selecionadas.items():
        ids_categorias = ",".join(map(str, cat_ids))
        url_parts.append(f"/c{class_id}/{ids_categorias}")
        
    # Parâmetros de formato (f=u para nome da unidade)
    url_parts.append("/f/u")
    
    return base_url + "".join(url_parts)
