# -*- coding: utf-8 -*-

from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsApplication, QgsVectorLayer
from qgis.PyQt.QtCore import pyqtSignal

from ..core.sidra_api_client import SidraApiClient
from ..core.mesh_downloader import MeshDownloader, fetch_available_years
from .layer_manager import load_vector_layer, add_layer_to_project

active_tasks = []

def cancel_all_tasks():
    """Cancela todas as tarefas ativas na lista."""
    for task in active_tasks:
        if task.isRunning():
            task.cancel()
    active_tasks.clear()

class FetchAvailableYearsTask(QgsTask):
    """Tarefa para buscar os anos de malhas disponíveis no site do IBGE."""
    yearsReady = pyqtSignal(list)
    fetchError = pyqtSignal(str)

    def __init__(self):
        super().__init__('A buscar anos de malhas disponíveis...', QgsTask.CanCancel)
        self.exception = None
        self.years = []

    def run(self):
        try:
            self.years = fetch_available_years()
            return True
        except Exception as e:
            self.exception = str(e)
            return False

    def finished(self, result):
        if self in active_tasks:
            active_tasks.remove(self)
        if result:
            self.yearsReady.emit(self.years)
        else:
            error_message = self.exception if self.exception else 'A tarefa foi cancelada.'
            self.fetchError.emit(error_message)


class FetchSidraDataTask(QgsTask):
    """Tarefa para buscar dados da API SIDRA em segundo plano."""
    dataReady = pyqtSignal(dict, dict)
    fetchError = pyqtSignal(str)

    def __init__(self, url):
        super().__init__(f'A procurar dados da API SIDRA', QgsTask.CanCancel)
        self.url = url
        self.exception = None
        self.sidra_data = None
        self.header_info = None

    def run(self):
        QgsMessageLog.logMessage(f'A iniciar busca de dados de: {self.url}', 'SIDRA Connector', Qgis.Info)
        try:
            client = SidraApiClient(self.url)
            self.sidra_data, self.header_info = client.fetch_and_parse()
            
            # Log adicional para debug
            if isinstance(self.sidra_data, dict):
                QgsMessageLog.logMessage(f'Dados recebidos: {len(self.sidra_data)} registros', 'SIDRA Connector', Qgis.Info)
                if len(self.sidra_data) > 0:
                    sample_keys = list(self.sidra_data.keys())[:3]
                    QgsMessageLog.logMessage(f'Códigos geográficos de exemplo: {sample_keys}', 'SIDRA Connector', Qgis.Info)
            else:
                QgsMessageLog.logMessage(f'Dados recebidos têm tipo incorreto: {type(self.sidra_data)}', 'SIDRA Connector', Qgis.Warning)
            
            return True
        except Exception as e:
            self.exception = str(e)
            QgsMessageLog.logMessage(f'Erro na busca de dados: {e}', 'SIDRA Connector', Qgis.Critical)
            return False

    def finished(self, result):
        if self in active_tasks:
            active_tasks.remove(self)
        if result and self.sidra_data is not None:
            self.dataReady.emit(self.sidra_data, self.header_info)
        else:
            error_message = self.exception if self.exception else 'A tarefa foi cancelada.'
            self.fetchError.emit(error_message)

class DownloadAndLoadLayerTask(QgsTask):
    """Tarefa para baixar, extrair e carregar um shapefile."""
    layerReady = pyqtSignal(QgsVectorLayer)
    downloadError = pyqtSignal(str)

    def __init__(self, url, layer_name):
        super().__init__(f'A baixar malha: {layer_name}', QgsTask.CanCancel)
        self.url = url
        self.layer_name = layer_name
        self.exception = None
        self.downloader = None
        self.new_layer = None

    def run(self):
        try:
            self.downloader = MeshDownloader(self.url)
            
            def progress_update(progress):
                self.setProgress(progress)

            shapefile_path = self.downloader.download_and_extract(progress_update)
            
            if self.isCanceled():
                return False

            self.new_layer = load_vector_layer(shapefile_path, self.layer_name)
            return self.new_layer.isValid()

        except Exception as e:
            self.exception = str(e)
            return False

    def finished(self, result):
        if self in active_tasks:
            active_tasks.remove(self)
        
        if self.downloader:
            self.downloader.cleanup()

        if result and self.new_layer:
            add_layer_to_project(self.new_layer)
            self.layerReady.emit(self.new_layer)
        else:
            error_message = f"Falha ao baixar/carregar a malha: {self.exception}"
            if self.isCanceled():
                error_message = "Download da malha cancelado."
            self.downloadError.emit(error_message)

def run_fetch_years_task(on_success, on_error):
    """Inicia a tarefa para buscar os anos disponíveis."""
    task = FetchAvailableYearsTask()
    task.yearsReady.connect(on_success)
    task.fetchError.connect(on_error)
    active_tasks.append(task)
    QgsApplication.taskManager().addTask(task)

def run_fetch_task(url, on_success, on_error):
    """Inicia a tarefa de busca de dados do SIDRA."""
    task = FetchSidraDataTask(url)
    task.dataReady.connect(on_success)
    task.fetchError.connect(on_error)
    active_tasks.append(task)
    QgsApplication.taskManager().addTask(task)

def run_download_task(url, layer_name, on_success, on_error):
    """Inicia a tarefa de download de malha."""
    task = DownloadAndLoadLayerTask(url, layer_name)
    task.layerReady.connect(on_success)
    task.downloadError.connect(on_error)
    active_tasks.append(task)
    QgsApplication.taskManager().addTask(task)
