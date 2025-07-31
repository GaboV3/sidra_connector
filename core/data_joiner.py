# -*- coding: utf-8 -*-

from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsFields,
    QgsWkbTypes,
    edit,
    Qgis
)
from qgis.PyQt.QtCore import QVariant

class DataJoiner:
    """
    Responsável por unir dados a uma camada vetorial, criando uma nova camada de resultado.
    """

    def __init__(self, target_layer, join_field_name, sidra_data, header_info):
        """
        Construtor.
        :param target_layer: A camada vetorial do QGIS onde os dados serão unidos.
        :param join_field_name: O nome do campo na camada alvo a ser usado para a união.
        :param sidra_data: Dicionário de lookup com os dados do SIDRA.
        :param header_info: Dicionário com informações do cabeçalho da API.
        """
        if not isinstance(target_layer, QgsVectorLayer):
            raise TypeError("O parâmetro 'target_layer' não é uma camada vetorial válida.")
        
        self.target_layer = target_layer
        self.join_field_name = join_field_name
        self.sidra_data = sidra_data
        self.header_info = header_info

    def join_data(self):
        """
        Executa a operação de união e retorna a nova camada e estatísticas.
        :return: Uma tupla (nova_camada, contagem_uniao, amostra_nao_correspondida, amostra_chave_camada).
        """
        new_fields = QgsFields()
        for field in self.target_layer.fields():
            new_fields.append(field)

        all_class_values = sorted(list(set(k for item in self.sidra_data.values() for k in item.keys())))
        period = self.header_info.get('D3N', 'periodo')
        field_map = {}
        for class_value in all_class_values:
            safe_class = str(class_value).lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
            field_name = f"sidra_{safe_class[:20]}_{period}"
            if new_fields.indexFromName(field_name) == -1:
                new_fields.append(QgsField(field_name, QVariant.Double))
            field_map[class_value] = field_name

        temp_layer = QgsVectorLayer(
            f"{QgsWkbTypes.displayString(self.target_layer.wkbType())}?crs={self.target_layer.crs().authid()}",
            f"{self.target_layer.name()}_sidra",
            "memory"
        )
        provider = temp_layer.dataProvider()
        provider.addAttributes(new_fields)
        temp_layer.updateFields()

        join_count = 0
        unmatched_keys_sample = []
        layer_keys_sample = []

        with edit(temp_layer):
            for feature in self.target_layer.getFeatures():
                new_feat = QgsFeature(new_fields)
                new_feat.setGeometry(feature.geometry())
                for i, field in enumerate(feature.fields()):
                    new_feat.setAttribute(i, feature.attribute(i))

                raw_key = feature[self.join_field_name]
                
                normalized_layer_key = None
                if raw_key is not None:
                    try:
                        normalized_layer_key = str(int(float(raw_key)))
                    except (ValueError, TypeError):
                        normalized_layer_key = str(raw_key).strip()

                if len(layer_keys_sample) < 5 and normalized_layer_key:
                    layer_keys_sample.append(normalized_layer_key)

                if normalized_layer_key and normalized_layer_key in self.sidra_data:
                    join_count += 1
                    for class_value, data_value in self.sidra_data[normalized_layer_key].items():
                        field_name = field_map.get(class_value)
                        if field_name:
                            try:
                                new_feat[field_name] = float(data_value)
                            except (ValueError, TypeError):
                                pass # Deixa o campo nulo se o valor não for conversível
                elif normalized_layer_key and len(unmatched_keys_sample) < 5:
                    unmatched_keys_sample.append(normalized_layer_key)
                
                temp_layer.addFeature(new_feat)

        return temp_layer, join_count, unmatched_keys_sample, layer_keys_sample
