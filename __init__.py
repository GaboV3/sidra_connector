# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SidraConnector
                                 A QGIS plugin
 Um plugin para buscar dados da API SIDRA do IBGE e uni-los a camadas vetoriais.
                             -------------------
        begin                : 2025-07-29
        copyright            : (C) 2025 by Gabriel Henrique Angelo
        email                : angelo.henrique.gabriel@gmail.com
 ***************************************************************************/

 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SidraConnector class from file plugin.py.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .plugin import SidraConnector
    return SidraConnector(iface)
