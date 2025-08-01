# -*- coding: utf-8 -*-

"""
Ficheiro para armazenar constantes usadas em todo o plugin.
"""

UFS = {
    "Brasil": "BR", "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", 
    "Amazonas": "AM", "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF", 
    "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA", "Mato Grosso": "MT", 
    "Mato Grosso do Sul": "MS", "Minas Gerais": "MG", "Pará": "PA", 
    "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI", 
    "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS", 
    "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP", 
    "Sergipe": "SE", "Tocantins": "TO"
}

MALHAS = {
    "Municípios": "Municipios",
    "Unidades da Federação": "UF",
    "Grandes Regiões": "Regioes",
    "Regiões Geográficas Imediatas": "RG_Imediatas",
    "Regiões Geográficas Intermediárias": "RG_Intermediarias",
    "País": "Pais"
}

IBGE_MESH_BASE_URL_PARENT = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/"

IBGE_MESH_BASE_URL = IBGE_MESH_BASE_URL_PARENT + "municipio_{ano}/"

# Configurações de rede e performance
API_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 300  
MAX_RETRIES = 3  
CHUNK_SIZE = 65536
