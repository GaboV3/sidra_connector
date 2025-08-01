# SIDRA Connector

## Descrição

O **SIDRA Connector** é um plugin para o QGIS projetado para facilitar a integração de dados estatísticos do Sistema IBGE de Recuperação Automática (SIDRA) com as malhas territoriais digitais do IBGE. Ele permite que usuários, como analistas de dados, pesquisadores e planejadores urbanos, busquem, baixem e vinculem dados de tabelas do SIDRA diretamente a camadas vetoriais no QGIS.

Este projeto visa otimizar o fluxo de trabalho de análise geoespacial, eliminando a necessidade de baixar e processar dados manualmente de diferentes fontes.

## Funcionalidades

*   **Cliente de API SIDRA:** Conecte-se à API do SIDRA para pesquisar e extrair dados de tabelas, variáveis e classificações.
*   **Download de Malhas Vetoriais:** Baixe malhas territoriais (municípios, estados, etc.) do IBGE em diferentes formatos e resoluções.
*   **União de Dados:** Vincule os dados estatísticos baixados do SIDRA com as camadas vetoriais correspondentes de forma automática.
*   **Gerenciamento de Camadas:** Adicione as novas camadas (com os dados já vinculados) diretamente ao seu projeto QGIS.

## Instalação

1.  Baixe o arquivo `.zip` da versão mais recente na [página de Releases](https://github.com/GaboV3/sidra_connector/releases) do projeto.
2.  Abra o QGIS.
3.  Vá para o menu `Complementos > Gerenciar e Instalar Complementos...`.
4.  Na aba `Instalar a partir de um arquivo ZIP`, selecione o arquivo baixado e clique em `Instalar Complemento`.
5.  Após a instalação, o ícone do SIDRA Connector aparecerá na sua barra de ferramentas.

## Contribuições

Contribuições são bem-vindas! Se você encontrar um bug ou tiver uma sugestão, por favor, abra uma [issue](https://github.com/GaboV3/sidra_connector/issues).

## Autor

*   **Gabriel Henrique Angelo** - [GaboV3](https://github.com/GaboV3)

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
