
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.import_chatwoot import chatwoot_importer
from utils.logger import setup_logger, logger

def main():
    setup_logger("chatwoot_importer")
    logger.info("=== Iniciando Importação Inteligente do Chatwoot ===")
    
    try:
        stats = chatwoot_importer.import_existing_leads()
        
        logger.info("=== Relatório Final ===")
        logger.info(f"Leads Importados (Novos): {stats['imported']}")
        logger.info(f"Leads Atualizados (Existentes): {stats['updated']}")
        logger.info(f"Erros/Ignorados: {stats['ignored']}")
        logger.info("=======================")
        
    except KeyboardInterrupt:
        logger.info("Operação interrompida pelo usuário.")
    except Exception as e:
        logger.critical(f"Erro fatal na importação: {e}")

if __name__ == "__main__":
    main()
