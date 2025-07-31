# -*- coding: utf-8 -*-

import os
import requests
import zipfile
import tempfile
import shutil
import re
from ..utils import constants

def fetch_available_years():
    """
    Busca os anos disponíveis para malhas municipais no FTP do IBGE.
    :return: Uma lista de strings com os anos, ordenada do mais recente para o mais antigo.
    """
    try:
        # A URL base contém as pastas de cada ano, ex: 'municipio_2020/'
        url = constants.IBGE_MESH_BASE_URL_PARENT
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        
        # Usa uma expressão regular para encontrar links que correspondem ao padrão de pasta de ano
        # Ex: <a href="municipio_2020/">municipio_2020/</a>
        year_folders = re.findall(r'href="municipio_(\d{4})/"', response.text)
        
        if not year_folders:
            raise ValueError("Nenhuma pasta de ano encontrada na página do IBGE.")
            
        # Converte para inteiros para ordenação e depois de volta para string
        years = sorted([int(y) for y in year_folders], reverse=True)
        return [str(y) for y in years]

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Não foi possível conectar ao servidor do IBGE para buscar os anos: {e}")


class MeshDownloader:
    """
    Responsável por baixar e extrair ficheiros de malha territorial do IBGE.
    """

    def __init__(self, url):
        """
        Construtor.
        :param url: A URL completa para o ficheiro .zip da malha.
        """
        self.url = url
        self.temp_dir_path = tempfile.mkdtemp()

    def download_and_extract(self, progress_callback=None):
        """
        Baixa o ficheiro zip, extrai e retorna o caminho para o shapefile.
        :param progress_callback: Uma função opcional para relatar o progresso.
        :return: O caminho completo para o ficheiro .shp extraído.
        """
        try:
            zip_path = os.path.join(self.temp_dir_path, 'download.zip')
            
            response = requests.get(self.url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress = (bytes_downloaded / total_size) * 100
                        progress_callback(progress)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                shapefile_name = next((name for name in zip_ref.namelist() if name.lower().endswith('.shp')), None)
                if not shapefile_name:
                    raise FileNotFoundError("Nenhum ficheiro .shp encontrado no arquivo .zip.")
                zip_ref.extractall(self.temp_dir_path)
                return os.path.join(self.temp_dir_path, shapefile_name)

        except requests.exceptions.RequestException as e:
            self.cleanup()
            raise ConnectionError(f"Falha no download da malha: {e}")
        except Exception as e:
            self.cleanup()
            raise e

    def cleanup(self):
        """
        Remove o diretório temporário e o seu conteúdo.
        """
        try:
            if self.temp_dir_path and os.path.exists(self.temp_dir_path):
                shutil.rmtree(self.temp_dir_path)
        except Exception:
            # Logar o erro seria uma boa prática aqui
            pass
