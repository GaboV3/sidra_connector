# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SidraConnectorDialogBase(object):
    def setupUi(self, SidraConnectorDialogBase):
        SidraConnectorDialogBase.setObjectName("SidraConnectorDialogBase")
        SidraConnectorDialogBase.resize(500, 550)
        self.verticalLayout = QtWidgets.QVBoxLayout(SidraConnectorDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_3 = QtWidgets.QGroupBox(SidraConnectorDialogBase)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 0, 0, 1, 1)
        self.cb_ano_malha = QtWidgets.QComboBox(self.groupBox_3)
        self.cb_ano_malha.setObjectName("cb_ano_malha")
        self.gridLayout_3.addWidget(self.cb_ano_malha, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 1, 0, 1, 1)
        self.cb_localidade_malha = QtWidgets.QComboBox(self.groupBox_3)
        self.cb_localidade_malha.setObjectName("cb_localidade_malha")
        self.gridLayout_3.addWidget(self.cb_localidade_malha, 1, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_3)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 2, 0, 1, 1)
        self.cb_tipo_malha = QtWidgets.QComboBox(self.groupBox_3)
        self.cb_tipo_malha.setObjectName("cb_tipo_malha")
        self.gridLayout_3.addWidget(self.cb_tipo_malha, 2, 1, 1, 1)
        self.btn_download_malha = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_download_malha.setObjectName("btn_download_malha")
        self.gridLayout_3.addWidget(self.btn_download_malha, 3, 0, 1, 2)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.line = QtWidgets.QFrame(SidraConnectorDialogBase)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.groupBox = QtWidgets.QGroupBox(SidraConnectorDialogBase)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.le_api_url = QtWidgets.QLineEdit(self.groupBox)
        self.le_api_url.setObjectName("le_api_url")
        self.verticalLayout_2.addWidget(self.le_api_url)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(SidraConnectorDialogBase)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
        self.cb_target_layer = RefreshableComboBox(self.groupBox_2)
        self.cb_target_layer.setObjectName("cb_target_layer")
        self.gridLayout.addWidget(self.cb_target_layer, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.cb_target_field = QtWidgets.QComboBox(self.groupBox_2)
        self.cb_target_field.setObjectName("cb_target_field")
        self.gridLayout.addWidget(self.cb_target_field, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btn_fetch_join = QtWidgets.QPushButton(SidraConnectorDialogBase)
        self.btn_fetch_join.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_fetch_join.setFont(font)
        self.btn_fetch_join.setObjectName("btn_fetch_join")
        self.verticalLayout.addWidget(self.btn_fetch_join)

        self.retranslateUi(SidraConnectorDialogBase)
        QtCore.QMetaObject.connectSlotsByName(SidraConnectorDialogBase)

    def retranslateUi(self, SidraConnectorDialogBase):
        _translate = QtCore.QCoreApplication.translate
        SidraConnectorDialogBase.setWindowTitle(_translate("SidraConnectorDialogBase", "SIDRA Connector"))
        self.groupBox_3.setTitle(_translate("SidraConnectorDialogBase", "1. Baixar Malha Territorial do IBGE (Opcional)"))
        self.label_7.setText(_translate("SidraConnectorDialogBase", "Ano:"))
        self.label_8.setText(_translate("SidraConnectorDialogBase", "Localidade:"))
        self.label_9.setText(_translate("SidraConnectorDialogBase", "Tipo de Malha:"))
        self.btn_download_malha.setText(_translate("SidraConnectorDialogBase", "Baixar e Carregar Malha na Camada"))
        self.groupBox.setTitle(_translate("SidraConnectorDialogBase", "2. Unir Dados da API SIDRA"))
        self.label.setText(_translate("SidraConnectorDialogBase", "URL da API SIDRA (gerada em \"Links > Para uso em programas\" no site do SIDRA):"))
        self.le_api_url.setToolTip(_translate("SidraConnectorDialogBase", "Cole aqui a URL completa da API, obtida no site do SIDRA"))
        self.le_api_url.setPlaceholderText(_translate("SidraConnectorDialogBase", "Ex: http://api.sidra.ibge.gov.br/values/t/5938/..."))
        self.groupBox_2.setTitle(_translate("SidraConnectorDialogBase", "3. Configuração da União (Join)"))
        self.label_5.setText(_translate("SidraConnectorDialogBase", "Camada Vetorial Alvo:"))
        self.label_6.setText(_translate("SidraConnectorDialogBase", "Campo de União (da Camada Alvo):"))
        self.btn_fetch_join.setText(_translate("SidraConnectorDialogBase", "Buscar Dados e Unir à Camada Alvo"))
from sidra_connector.ui.custom_widgets import RefreshableComboBox


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SidraConnectorDialogBase = QtWidgets.QDialog()
    ui = Ui_SidraConnectorDialogBase()
    ui.setupUi(SidraConnectorDialogBase)
    SidraConnectorDialogBase.show()
    sys.exit(app.exec_())
