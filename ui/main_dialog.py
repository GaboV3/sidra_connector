# -*- coding: utf-8 -*-

from qgis.core import Qgis, QgsVectorLayer
from qgis.PyQt import QtWidgets

from .main_dialog_base_ui import Ui_SidraConnectorDialogBase
from ..gis import layer_manager, task_manager
from ..core.data_joiner import DataJoiner
from ..utils import constants

class SidraConnectorDialog(QtWidgets.QDialog, Ui_SidraConnectorDialogBase):
    """
    Lógica da janela de diálogo principal do plugin.
    """

    def __init__(self, iface, parent=None):
        """
        Construtor da janela de diálogo.
        """
        super(SidraConnectorDialog, self).__init__(parent)
        self.setupUi(self)
        
        self.iface = iface

        self.cb_target_layer.aboutToShowPopup.connect(self.populate_layers_combobox)
        self.cb_target_layer.currentIndexChanged.connect(self.on_layer_selection_changed)
        self.btn_download_malha.clicked.connect(self.handle_download_mesh)
        self.btn_fetch_join.clicked.connect(self.handle_fetch_and_join)
        
        self.populate_malha_comboboxes()
        self.populate_layers_combobox()
        self.on_layer_selection_changed()

    def populate_malha_comboboxes(self):
        """
        Popula as comboboxes relacionadas ao download de malhas territoriais.
        """
        self.cb_ano_malha.addItems([str(y) for y in range(2024, 1999, -1)])
        self.cb_localidade_malha.addItems(constants.UFS.keys())
        self.cb_tipo_malha.addItems(constants.MALHAS.keys())

    def populate_layers_combobox(self):
        """
        Popula a combobox de camadas com as camadas vetoriais do projeto.
        """
        self.cb_target_layer.blockSignals(True)
        current_layer = self.cb_target_layer.currentData()
        self.cb_target_layer.clear()
        
        self.cb_target_layer.addItem("Selecione uma camada...", None)
        
        vector_layers = layer_manager.get_project_vector_layers()
        for layer in vector_layers:
            self.cb_target_layer.addItem(layer.name(), layer)
        
        index = self.cb_target_layer.findData(current_layer)
        if index != -1:
            self.cb_target_layer.setCurrentIndex(index)
        else:
            self.cb_target_layer.setCurrentIndex(0)
            
        self.cb_target_layer.blockSignals(False)
        self.on_layer_selection_changed()

    def populate_fields_combobox(self):
        """
        Popula a combobox de campos com os campos da camada alvo selecionada.
        """
        self.cb_target_field.clear()
        layer = self.cb_target_layer.currentData()
        if layer:
            self.cb_target_field.addItems(layer_manager.get_layer_fields(layer))

    def on_layer_selection_changed(self):
        """
        Habilita/desabilita botões e popula campos com base na seleção da camada.
        """
        layer_is_selected = self.cb_target_layer.currentData() is not None
        self.btn_fetch_join.setEnabled(layer_is_selected)
        self.populate_fields_combobox()

    def handle_download_mesh(self):
        """
        Inicia o processo de download da malha territorial.
        """
        ano = self.cb_ano_malha.currentText()
        localidade_nome = self.cb_localidade_malha.currentText()
        malha_nome = self.cb_tipo_malha.currentText()
        
        localidade_sigla = constants.UFS[localidade_nome]
        malha_prefixo = constants.MALHAS[malha_nome]

        if localidade_sigla == "BR":
            url_path = f"Brasil/{localidade_sigla}_{malha_prefixo}_{ano}.zip"
        else:
            url_path = f"UFs/{localidade_sigla}/{localidade_sigla}_{malha_prefixo}_{ano}.zip"

        base_url = constants.IBGE_MESH_BASE_URL.format(ano=ano)
        url = base_url + url_path
        layer_name = f"{malha_prefixo}_{localidade_nome}_{ano}".replace(" ", "_")

        self.iface.messageBar().pushMessage("Download", f"Iniciando download da malha: {layer_name}", level=Qgis.Info, duration=5)
        task_manager.run_download_task(url, layer_name, self.on_download_success, self.on_download_error)

    def on_download_success(self, new_layer):
        """Callback de sucesso para o download."""
        self.iface.messageBar().pushMessage("Sucesso", f"Camada '{new_layer.name()}' carregada com sucesso!", level=Qgis.Success)

    def on_download_error(self, error_message):
        """Callback de erro para o download."""
        self.iface.messageBar().pushMessage("Erro no Download", error_message, level=Qgis.Critical, duration=10)

    def handle_fetch_and_join(self):
        """
        Inicia o processo de busca de dados da API e união à camada.
        """
        api_url = self.le_api_url.text().strip()
        target_layer = self.cb_target_layer.currentData()
        join_field = self.cb_target_field.currentText()

        # Validações de entrada
        if not api_url:
            self.iface.messageBar().pushMessage("Erro", "URL da API deve ser preenchida.", level=Qgis.Critical)
            return
            
        if not api_url.startswith(('http://', 'https://')):
            self.iface.messageBar().pushMessage("Erro", "URL deve começar com http:// ou https://", level=Qgis.Critical)
            return
            
        if not target_layer:
            self.iface.messageBar().pushMessage("Erro", "Camada alvo deve ser selecionada.", level=Qgis.Critical)
            return
            
        if not join_field:
            self.iface.messageBar().pushMessage("Erro", "Campo de união deve ser selecionado.", level=Qgis.Critical)
            return

        self.iface.messageBar().pushMessage("SIDRA Connector", "Buscando dados na API...", level=Qgis.Info, duration=5)
        task_manager.run_fetch_task(api_url, self.on_fetch_success, self.on_fetch_error)

    def on_fetch_success(self, sidra_data, header_info):
        """Callback de sucesso para a busca de dados."""
        self.iface.messageBar().pushMessage("SIDRA Connector", "Dados recebidos. Processando e unindo...", level=Qgis.Info)
        
        # Validação adicional dos dados recebidos
        if not sidra_data or not isinstance(sidra_data, dict):
            self.iface.messageBar().pushMessage(
                "Erro", 
                "A API não retornou dados válidos. Verifique se a URL está correta e se contém dados para o período/localização especificados.", 
                level=Qgis.Critical, 
                duration=10
            )
            return
        
        if len(sidra_data) == 0:
            self.iface.messageBar().pushMessage(
                "Aviso", 
                "A API retornou dados vazios. Verifique se a URL da API está correta e se há dados disponíveis para os parâmetros especificados.", 
                level=Qgis.Warning, 
                duration=10
            )
            return
        
        target_layer = self.cb_target_layer.currentData()
        join_field = self.cb_target_field.currentText()

        try:
            joiner = DataJoiner(target_layer, join_field, sidra_data, header_info)
            new_layer, join_count, unmatched, layer_keys = joiner.join_data()
            
            layer_manager.add_layer_to_project(new_layer)

            if join_count > 0:
                self.iface.messageBar().pushMessage("Sucesso", f"Cópia da camada criada com {join_count} feições unidas!", Qgis.Success)
            else:
                sidra_keys_sample = list(sidra_data.keys())[:5] if sidra_data else []
                self.iface.messageBar().pushMessage(
                    "Aviso", 
                    f"Nenhuma correspondência encontrada. Verifique o formato dos códigos. "
                    f"Exemplos da sua camada: {layer_keys}. "
                    f"Exemplos dos dados SIDRA: {sidra_keys_sample}.",
                    level=Qgis.Warning, 
                    duration=20
                )
        except ValueError as e:
            self.iface.messageBar().pushMessage("Erro de Validação", f"Dados inválidos: {e}", Qgis.Critical)
        except TypeError as e:
            self.iface.messageBar().pushMessage("Erro de Tipo", f"Erro no processamento dos dados: {e}", Qgis.Critical)
        except Exception as e:
            self.iface.messageBar().pushMessage("Erro", f"Falha no processamento ou união: {e}", Qgis.Critical)

    def on_fetch_error(self, error_message):
        """Callback de erro para a busca de dados."""
        self.iface.messageBar().pushMessage("Erro na API", f"Ocorreu um erro: {error_message}", level=Qgis.Critical, duration=10)

