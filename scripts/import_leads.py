
import argparse
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.lead_service import lead_service
from utils.logger import setup_logger

logger = setup_logger("import_script")

def main():
    parser = argparse.ArgumentParser(description="Importa leads de um arquivo CSV para o Supabase.")
    parser.add_argument("--file", required=True, help="Caminho para o arquivo CSV de leads.")
    
    args = parser.parse_args()
    filepath = args.file
    
    if not os.path.exists(filepath):
        print(f"Erro: Arquivo não encontrado: {filepath}")
        return

    print(f"Iniciando importação de: {filepath}...")
    
    try:
        stats = lead_service.import_from_csv(filepath)
        
        print("\n--- Relatório de Importação ---")
        print(f"Total processado: {stats['total']}")
        print(f"Importados com sucesso: {stats['imported']}")
        print(f"Ignorados (inválidos/duplicados): {stats['skipped']}")
        print(f"Erros: {stats['errors']}")
        print("-------------------------------")
        
    except Exception as e:
        logger.error(f"Erro fatal durante importação: {e}")
        print(f"Erro fatal: {e}")

if __name__ == "__main__":
    main()
