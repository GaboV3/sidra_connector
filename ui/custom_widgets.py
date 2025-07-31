# -*- coding: utf-8 -*-

"""
Este arquivo contém as definições de widgets personalizados para o plugin.
"""

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal

class RefreshableComboBox(QtWidgets.QComboBox):
    """
    Uma QComboBox que emite um sinal personalizado (aboutToShowPopup)
    antes de mostrar seu menu popup. Isso permite que a lista de itens
    seja atualizada dinamicamente pouco antes de ser exibida ao usuário.
    """
    aboutToShowPopup = pyqtSignal()

    def showPopup(self):
        """
        Sobrescreve o método showPopup para emitir o sinal antes de
        chamar a implementação original.
        """
        self.aboutToShowPopup.emit()
        super(RefreshableComboBox, self).showPopup()
