# -*- coding: utf-8 -*-
"""
Diálogo do assistente de busca de tabelas do SIDRA.
"""

import os
import sqlite3
from qgis.PyQt import QtWidgets, QtCore
from qgis.core import QgsMessageLog, Qgis

from ..core.api_helpers import get_metadata_from_api, montar_url_interativa

class QueryBuilderDialog(QtWidgets.QDialog):
    """
    Diálogo que permite ao usuário pesquisar tabelas do SIDRA e construir URLs da API.
    """

    def __init__(self, plugin_dir, parent=None):
        """
        Construtor do diálogo.
        
        Args:
            plugin_dir (str): Diretório do plugin onde está o banco de dados
            parent: Widget pai
        """
        super(QueryBuilderDialog, self).__init__(parent)
        self.plugin_dir = plugin_dir
        self.generated_url = None
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """
        Configura a interface do usuário.
        """
        self.setWindowTitle("Assistente de Busca - SIDRA Connector")
        self.setFixedSize(600, 400)
        
        # Layout principal
        layout = QtWidgets.QVBoxLayout(self)
        
        # Seção de busca
        search_group = QtWidgets.QGroupBox("Buscar Tabelas")
        search_layout = QtWidgets.QVBoxLayout(search_group)
        
        # Campo de busca
        search_input_layout = QtWidgets.QHBoxLayout()
        self.le_search = QtWidgets.QLineEdit()
        self.le_search.setPlaceholderText("Digite palavras-chave para buscar tabelas...")
        self.btn_clear = QtWidgets.QPushButton("Limpar")
        self.btn_clear.setMaximumWidth(80)
        
        search_input_layout.addWidget(self.le_search)
        search_input_layout.addWidget(self.btn_clear)
        
        search_layout.addLayout(search_input_layout)
        
        # Label de status
        self.lbl_status = QtWidgets.QLabel("Digite pelo menos 2 caracteres para iniciar a busca...")
        self.lbl_status.setStyleSheet("color: gray; font-style: italic;")
        
        # Lista de resultados
        self.list_results = QtWidgets.QListWidget()
        self.list_results.setMaximumHeight(200)
        
        search_layout.addWidget(self.lbl_status)
        search_layout.addWidget(self.list_results)
        
        # Seção de tabela selecionada
        selected_group = QtWidgets.QGroupBox("Tabela Selecionada")
        selected_layout = QtWidgets.QVBoxLayout(selected_group)
        
        self.lbl_selected_table = QtWidgets.QLabel("Nenhuma tabela selecionada")
        self.lbl_selected_table.setWordWrap(True)
        self.btn_build_query = QtWidgets.QPushButton("Construir Consulta")
        self.btn_build_query.setEnabled(False)
        
        selected_layout.addWidget(self.lbl_selected_table)
        selected_layout.addWidget(self.btn_build_query)
        
        # Botões de ação
        button_layout = QtWidgets.QHBoxLayout()
        self.btn_cancel = QtWidgets.QPushButton("Cancelar")
        self.btn_ok = QtWidgets.QPushButton("OK")
        self.btn_ok.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_ok)
        
        # Adicionar ao layout principal
        layout.addWidget(search_group)
        layout.addWidget(selected_group)
        layout.addLayout(button_layout)

    def connect_signals(self):
        """
        Conecta os sinais dos widgets.
        """
        # Timer para busca dinâmica
        self.search_timer = QtCore.QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        # Conectar eventos
        self.le_search.textChanged.connect(self.on_search_text_changed)
        self.btn_clear.clicked.connect(self.clear_search)
        self.list_results.itemDoubleClicked.connect(self.on_table_selected)
        self.btn_build_query.clicked.connect(self.build_query)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)

    def get_db_connection(self):
        """
        Estabelece conexão com o banco de dados de agregados.
        
        Returns:
            sqlite3.Connection: Conexão com o banco ou None em caso de erro
        """
        db_path = os.path.join(self.plugin_dir, "agregados_ibge.db")
        
        if not os.path.exists(db_path):
            QtWidgets.QMessageBox.critical(
                self, 
                "Erro", 
                f"Banco de dados não encontrado em: {db_path}\n\n"
                "Certifique-se de que o arquivo agregados_ibge.db está na pasta do plugin."
            )
            return None
            
        try:
            return sqlite3.connect(db_path)
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Erro de Banco de Dados", 
                f"Não foi possível conectar ao banco de dados: {e}"
            )
            return None

    def on_search_text_changed(self):
        """
        Manipula a mudança no texto de busca com delay para evitar muitas consultas.
        """
        search_text = self.le_search.text().strip()
        
        # Parar o timer anterior
        self.search_timer.stop()
        
        if len(search_text) < 2:
            # Limpar resultados se o texto for muito curto
            self.list_results.clear()
            self.lbl_status.setText("Digite pelo menos 2 caracteres para iniciar a busca...")
            self.lbl_status.setStyleSheet("color: gray; font-style: italic;")
            return
            
        # Iniciar novo timer de 500ms
        self.search_timer.start(500)

    def clear_search(self):
        """
        Limpa o campo de busca e os resultados.
        """
        self.le_search.clear()
        self.list_results.clear()
        self.lbl_status.setText("Digite pelo menos 2 caracteres para iniciar a busca...")
        self.lbl_status.setStyleSheet("color: gray; font-style: italic;")

    def perform_search(self):
        """
        Realiza a busca dinâmica de tabelas.
        """
        search_term = self.le_search.text().strip()
        
        if len(search_term) < 2:
            return
            
        self.lbl_status.setText("Buscando...")
        self.lbl_status.setStyleSheet("color: blue; font-style: italic;")
        
        # Realizar a busca
        self.search_tables(search_term)

    def search_tables(self):
        """
        Realiza a busca de tabelas no banco de dados.
        """
    def search_tables(self, search_term=None):
        """
        Realiza a busca de tabelas no banco de dados.
        
        Args:
            search_term (str): Termo de busca. Se None, usa o valor do campo de texto.
        """
        if search_term is None:
            search_term = self.le_search.text().strip()
        
        if len(search_term) < 2:
            self.lbl_status.setText("Digite pelo menos 2 caracteres para iniciar a busca...")
            self.lbl_status.setStyleSheet("color: gray; font-style: italic;")
            return

        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Busca por nome da tabela ou grupo
            query = """
                SELECT a.id, a.nome, g.nome as grupo_nome 
                FROM agregados a 
                JOIN grupos g ON a.grupo_id = g.id 
                WHERE a.nome LIKE ? OR g.nome LIKE ?
                ORDER BY a.nome
                LIMIT 50
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
            results = cursor.fetchall()
            
            # Limpar resultados anteriores
            self.list_results.clear()
            
            if results:
                for table_id, table_name, group_name in results:
                    item = QtWidgets.QListWidgetItem(f"[{table_id}] {table_name} ({group_name})")
                    item.setData(QtCore.Qt.UserRole, table_id)
                    self.list_results.addItem(item)
                
                # Atualizar status
                count = len(results)
                max_text = " (mostrando primeiros 50)" if count == 50 else ""
                self.lbl_status.setText(f"{count} resultado(s) encontrado(s){max_text}")
                self.lbl_status.setStyleSheet("color: green;")
            else:
                self.lbl_status.setText("Nenhum resultado encontrado")
                self.lbl_status.setStyleSheet("color: orange;")
                
        except sqlite3.Error as e:
            self.lbl_status.setText(f"Erro na busca: {e}")
            self.lbl_status.setStyleSheet("color: red;")
            QtWidgets.QMessageBox.critical(
                self, 
                "Erro de Busca", 
                f"Erro ao buscar no banco de dados: {e}"
            )
        finally:
            conn.close()

    def on_table_selected(self, item):
        """
        Manipula a seleção de uma tabela da lista.
        
        Args:
            item (QListWidgetItem): Item selecionado
        """
        table_id = item.data(QtCore.Qt.UserRole)
        
        if table_id is None:
            # Item inválido (como mensagem de "nenhum resultado")
            return
            
        self.selected_table_id = table_id
        self.lbl_selected_table.setText(f"Tabela selecionada: {item.text()}")
        self.btn_build_query.setEnabled(True)

    def build_query(self):
        """
        Constrói a consulta interativa para a tabela selecionada.
        """
        if not hasattr(self, 'selected_table_id'):
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione uma tabela primeiro.")
            return
            
        # Buscar metadados da tabela
        metadata = get_metadata_from_api(str(self.selected_table_id))
        
        if not metadata:
            QtWidgets.QMessageBox.critical(
                self, 
                "Erro", 
                "Não foi possível obter os metadados da tabela. Verifique sua conexão com a internet."
            )
            return
        
        try:
            # Selecionar períodos
            periodos_disponiveis = [
                (p.get('Id'), p.get('Nome'), p.get('Codigo')) 
                for p in metadata.get('Periodos', {}).get('Periodos', [])
            ]
            periodos_selecionados = self.show_selection_dialog(
                "Selecione o(s) Período(s)", 
                periodos_disponiveis
            )
            if not periodos_selecionados:
                return
                
            # Selecionar nível geográfico
            niveis_disponiveis = [
                (n.get('Id'), n.get('Nome'), n.get('Sigla')) 
                for n in metadata.get('Territorios', {}).get('NiveisTabela', [])
            ]
            nivel_selecionado = self.show_selection_dialog(
                "Selecione o Nível Geográfico", 
                niveis_disponiveis, 
                single_selection=True
            )
            if not nivel_selecionado:
                return
                
            # Selecionar variáveis
            variaveis_disponiveis = []
            for var in metadata.get('Variaveis', []):
                unidade = ""
                if isinstance(var.get('UnidadeDeMedida'), list):
                    if var.get('UnidadeDeMedida'):
                        unidade = var.get('UnidadeDeMedida')[0].get('Unidade', '')
                else:
                    unidade = var.get('UnidadeDeMedida', '')
                    
                variaveis_disponiveis.append((var.get('Id'), var.get('Nome'), unidade))
                
                # Adicionar variáveis derivadas
                for derivada in var.get('VariaveisDerivadas', []):
                    unidade_derivada = derivada.get('UnidadeDeMedida', '')
                    variaveis_disponiveis.append(
                        (derivada.get('Id'), f"  └─ {derivada.get('Nome')}", unidade_derivada)
                    )
                    
            variaveis_selecionadas = self.show_selection_dialog(
                "Selecione a(s) Variável(is)", 
                variaveis_disponiveis
            )
            if not variaveis_selecionadas:
                return
                
            # Selecionar categorias para cada classificação
            classificacoes_selecionadas = {}
            for classif in metadata.get('Classificacoes', []):
                class_id = classif.get('Id')
                class_nome = classif.get('Nome')
                
                categorias_disponiveis = []
                for cat in classif.get('Categorias', []):
                    indentacao = "  " * cat.get('IdentacaoApresentacao', 0)
                    categorias_disponiveis.append(
                        (cat.get('Id'), f"{indentacao}{cat.get('Nome')}")
                    )
                
                if categorias_disponiveis:
                    categorias_selecionadas = self.show_selection_dialog(
                        f"Selecione categorias para: {class_nome}",
                        categorias_disponiveis
                    )
                    if categorias_selecionadas:
                        classificacoes_selecionadas[class_id] = [item[0] for item in categorias_selecionadas]
            
            # Montar URL
            self.generated_url = montar_url_interativa(
                self.selected_table_id,
                nivel_selecionado[0],
                variaveis_selecionadas,
                periodos_selecionados,
                classificacoes_selecionadas
            )
            
            # Habilitar botão OK
            self.btn_ok.setEnabled(True)
            
            QtWidgets.QMessageBox.information(
                self, 
                "Sucesso", 
                "URL da API gerada com sucesso! Clique em OK para usar a URL gerada."
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Erro", 
                f"Erro ao processar metadados da tabela: {e}"
            )

    def show_selection_dialog(self, title, options, single_selection=False):
        """
        Exibe um diálogo de seleção múltipla ou simples.
        
        Args:
            title (str): Título do diálogo
            options (list): Lista de tuplas (id, nome, info_extra)
            single_selection (bool): Se True, permite apenas uma seleção
            
        Returns:
            list: Lista de tuplas selecionadas ou None se cancelado
        """
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(500, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Lista de opções
        list_widget = QtWidgets.QListWidget()
        
        for option in options:
            item_id, item_name = option[0], option[1]
            info_extra = f" ({option[2]})" if len(option) > 2 and option[2] else ""
            
            item = QtWidgets.QListWidgetItem(f"{item_name} (ID: {item_id}){info_extra}")
            item.setData(QtCore.Qt.UserRole, option)
            list_widget.addItem(item)
        
        if not single_selection:
            list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        
        layout.addWidget(list_widget)
        
        # Botões
        button_layout = QtWidgets.QHBoxLayout()
        btn_ok = QtWidgets.QPushButton("OK")
        btn_cancel = QtWidgets.QPushButton("Cancelar")
        
        button_layout.addStretch()
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_ok)
        
        layout.addLayout(button_layout)
        
        # Conectar sinais
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        # Executar diálogo
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_items = list_widget.selectedItems()
            
            if not selected_items:
                QtWidgets.QMessageBox.warning(self, "Aviso", "Nenhum item selecionado.")
                return None
                
            return [item.data(QtCore.Qt.UserRole) for item in selected_items]
        
        return None

    def get_generated_url(self):
        """
        Retorna a URL gerada pelo assistente.
        
        Returns:
            str: URL da API ou None se não foi gerada
        """
        return self.generated_url
