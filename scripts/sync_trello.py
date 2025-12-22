
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.trello_service import trello_service
from utils.logger import logger

def main():
    print("=== Sincronização de Leads com Trello ===")
    print("Buscando leads sem card vinculado e procurando no Trello...")
    
    try:
        stats = trello_service.sync_all_leads_with_trello()
        
        print("\n=== Relatório ===")
        print(f"Total Processado: {stats['total']}")
        print(f"Vinculados (Encontrados): {stats['linked']}")
        print(f"Não Encontrados: {stats['not_found']}")
        print("=================")
        
    except Exception as e:
        logger.error(f"Erro fatal no script de sync: {e}")
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()
