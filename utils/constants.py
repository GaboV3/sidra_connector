# -*- coding: utf-8 -*-

"""
Ficheiro para armazenar constantes usadas em todo o plugin.
"""

# Dicionário de Unidades da Federação
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

# Dicionário de tipos de malhas territoriais
MALHAS = {
    "Municípios": "Municipios",
    "Unidades da Federação": "UF",
    "Grandes Regiões": "Regioes",
    "Regiões Geográficas Imediatas": "RG_Imediatas",
    "Regiões Geográficas Intermediárias": "RG_Intermediarias",
    "País": "Pais"
}

# URL "pai" que contém as pastas dos anos
IBGE_MESH_BASE_URL_PARENT = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/"

# URL base para download das malhas do IBGE (com placeholder para o ano)
IBGE_MESH_BASE_URL = IBGE_MESH_BASE_URL_PARENT + "municipio_{ano}/"
