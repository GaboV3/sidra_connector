# -*- coding: utf-8 -*-

import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .ui.main_dialog import SidraConnectorDialog
from .gis.task_manager import active_tasks, cancel_all_tasks

class SidraConnector:
    """
    Classe principal do plugin que gerencia a integração com a interface do QGIS.
    """

    def __init__(self, iface):
        """
        Construtor.
        :param iface: Uma instância da interface do QGIS.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.menu = u'&SIDRA Connector'
        self.dialog = None

    def initGui(self):
        """
        Cria a ação e o item de menu para o plugin.
        """
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action = QAction(QIcon(icon_path), 'SIDRA Connector', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)

    def unload(self):
        """
        Remove o item de menu e a ação quando o plugin é descarregado
        e cancela todas as tarefas ativas.
        """
        cancel_all_tasks()
        self.iface.removePluginMenu(u'&SIDRA Connector', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """
        Executa o diálogo do plugin. Cria uma nova instância se necessário.
        """
        # Sempre crie um novo diálogo para evitar estado antigo
        self.dialog = SidraConnectorDialog(self.iface)
        self.dialog.show()
        # O resultado da execução é tratado dentro da própria classe de diálogo
        self.dialog.exec_()
