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
        
        if not target_layer.isValid():
            raise ValueError("A camada vetorial fornecida não é válida.")
            
        if not join_field_name or join_field_name not in [field.name() for field in target_layer.fields()]:
            raise ValueError(f"Campo de união '{join_field_name}' não encontrado na camada.")
        
        if not isinstance(sidra_data, dict):
            raise TypeError("Os dados do SIDRA devem ser fornecidos como um dicionário.")
            
        if not sidra_data:
            raise ValueError(f"Nenhum dado do SIDRA foi fornecido. Verifique se a URL da API está correta e retorna dados válidos.")
        
        self.target_layer = target_layer
        self.join_field_name = join_field_name
        self.sidra_data = sidra_data
        self.header_info = header_info if header_info else {}

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
        used_field_names = set()
        
        for class_value in all_class_values:
            # Criar nome mais descritivo e único
            safe_class = str(class_value).lower()
            # Remover caracteres especiais mas manter mais informação
            safe_class = safe_class.replace(' - ', '_').replace(' ', '_').replace('/', '_')
            safe_class = safe_class.replace('(', '').replace(')', '').replace('-', '_')
            
            # Aumentar limite para 40 caracteres (limite do QGIS é ~63)
            base_name = safe_class[:40]
            field_name = f"{base_name}"
            
            # Garantir que o nome é único
            counter = 1
            original_field_name = field_name
            while field_name in used_field_names:
                field_name = f"{original_field_name}_{counter}"
                counter += 1
            
            # Garantir que não excede limite do QGIS (63 caracteres)
            if len(field_name) > 60:
                field_name = field_name[:60]
            
            used_field_names.add(field_name)
            
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
