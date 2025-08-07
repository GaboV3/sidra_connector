import json
import sqlite3
import os

def criar_conexao(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def criar_tabelas(conn):
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grupos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agregados (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                grupo_id TEXT NOT NULL,
                FOREIGN KEY (grupo_id) REFERENCES grupos (id)
            );
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")

def processar_json_para_db(conn, caminho_arquivo):
    print(f"Processando o arquivo: {caminho_arquivo}...")
    cursor = conn.cursor()

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        if not isinstance(dados, list):
            print("Estrutura de JSON inesperada. O arquivo deve conter uma lista de grupos.")
            return

        for grupo in dados:
            grupo_id = grupo.get('id')
            grupo_nome = grupo.get('nome')
            
            if grupo_id and grupo_nome:
                cursor.execute(
                    "INSERT OR IGNORE INTO grupos (id, nome) VALUES (?, ?)",
                    (grupo_id, grupo_nome)
                )

                for agregado in grupo.get('agregados', []):
                    agregado_id = agregado.get('id')
                    agregado_nome = agregado.get('nome')
                    
                    if agregado_id and agregado_nome:
                        cursor.execute(
                            "INSERT OR IGNORE INTO agregados (id, nome, grupo_id) VALUES (?, ?, ?)",
                            (agregado_id, agregado_nome, grupo_id)
                        )
        
        conn.commit()
        print("Dados inseridos no banco de dados com sucesso.")

    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não contém um JSON válido.")
    except sqlite3.Error as e:
        print(f"Erro de banco de dados: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")

def main():
    db_filename = "agregados_ibge.db"
    
    json_filename = input("Digite o nome do arquivo JSON de agregados (ex: agregados.json): ")
    if not json_filename.strip():
        print("Nenhum nome de arquivo inserido.")
        return

    if not os.path.exists(json_filename):
        print(f"Erro: Arquivo '{json_filename}' não encontrado.")
        return

    conn = criar_conexao(db_filename)
    if conn:
        criar_tabelas(conn)
        processar_json_para_db(conn, json_filename)
        conn.close()
        print(f"Processo concluído. Banco de dados '{db_filename}' foi criado/atualizado.")

if __name__ == "__main__":
    main()
