# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, Qgis, QgsMessageLog
import os
import shutil

def get_project_vector_layers():
    """
    Retorna uma lista de todas as camadas vetoriais com geometria no projeto atual.
    """
    layers = QgsProject.instance().mapLayers().values()
    return [lyr for lyr in layers if isinstance(lyr, QgsVectorLayer) and lyr.wkbType() != QgsWkbTypes.NoGeometry]

def get_layer_fields(layer):
    """
    Retorna uma lista com os nomes dos campos de uma camada.
    """
    if not layer or not isinstance(layer, QgsVectorLayer):
        return []
    return [field.name() for field in layer.fields()]

def add_layer_to_project(layer):
    """
    Adiciona uma camada ao projeto QGIS atual.
    """
    if layer and layer.isValid():
        QgsProject.instance().addMapLayer(layer)
        return True
    return False

def load_vector_layer(path, name):
    """
    Carrega uma camada vetorial a partir de um caminho.
    """
    layer = QgsVectorLayer(path, name, "ogr")
    return layer

def safe_cleanup_dir(path):
    """
    Remove de forma segura um diretório e todo o seu conteúdo.
    """
    try:
        if path and os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        QgsMessageLog.logMessage(f"Não foi possível limpar o diretório temporário {path}: {e}", "SIDRA Connector", Qgis.Warning)
