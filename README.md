# SIDRA Connector

## Descrição

O **SIDRA Connector** é um plugin para o QGIS projetado para facilitar a integração de dados estatísticos do Sistema IBGE de Recuperação Automática (SIDRA) com as malhas territoriais digitais do IBGE. Ele permite que usuários, como analistas de dados, pesquisadores e planejadores urbanos, busquem, baixem e vinculem dados de tabelas do SIDRA diretamente a camadas vetoriais no QGIS.

Este projeto visa otimizar o fluxo de trabalho de análise geoespacial, eliminando a necessidade de baixar e processar dados manualmente.

## Funcionalidades

*   **Assistente de Busca:** Pesquise tabelas do IBGE por palavras-chave com busca dinâmica em tempo real e construa URLs da API de forma interativa e guiada.
*   **Download de Malhas Vetoriais:** Baixe malhas territoriais (municípios, estados, etc.) do IBGE em diferentes formatos e resoluções.
*   **União de Dados:** Vincule os dados estatísticos baixados do SIDRA com as camadas vetoriais correspondentes de forma automática.

## Como Usar

1.  **Abra o Plugin:** Clique no ícone do SIDRA Connector para abrir a janela principal.

### Opção 1: Usando o Assistente de Busca (Recomendado)
2.  **Buscar Tabela:** Clique no botão "Montar API / Buscar Tabela..." para abrir o assistente.
3.  **Pesquisar:** Digite palavras-chave e veja os resultados aparecerem em tempo real (ex: "população", "PIB", "educação").
4.  **Selecionar:** Clique duas vezes na tabela desejada da lista de resultados.
5.  **Configurar:** Siga os diálogos interativos para selecionar:
    - Períodos (anos/meses)
    - Nível geográfico (Estados, Municípios, etc.)
    - Variáveis da tabela
    - Categorias das classificações
6.  **URL Automática:** A URL da API será gerada e inserida automaticamente.

### Opção 2: URL Manual
2.  **URL da API:** Cole diretamente uma URL da API do SIDRA no campo correspondente.

### Finalização
7.  **Download da Malha:** Opcionalmente, baixe uma malha vetorial correspondente usando a seção "Download de Malha".
8.  **Selecionar Camada:** Escolha uma camada vetorial já carregada no seu projeto.
9.  **Executar União:** Clique em "Buscar e Unir Dados" para processar e criar a nova camada com os dados unidos.

## Contribuições

Contribuições são bem-vindas! Se você encontrar um bug ou tiver uma sugestão, por favor, abra uma [issue](https://github.com/GaboV3/sidra_connector/issues).

## Autor

*   **Gabriel Henrique Angelo** - [GaboV3](https://github.com/GaboV3)

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
