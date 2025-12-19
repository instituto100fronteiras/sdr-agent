
import sys
import argparse
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.google_maps_search import google_maps_searcher
from utils.logger import setup_logger, logger

def main():
    setup_logger("google_maps_search")
    
    parser = argparse.ArgumentParser(description="Busca leads no Google Maps via SerpAPI")
    parser.add_argument("--query", required=True, help="Termo de busca (ex: arquitetos, clinicas)")
    parser.add_argument("--city", required=True, help="Cidade para busca")
    parser.add_argument("--limit", type=int, default=20, help="Limite de resultados para processar")
    
    args = parser.parse_args()
    
    logger.info("=== Iniciando Busca de Leads no Google Maps ===")
    logger.info(f"Termo: {args.query}")
    logger.info(f"Cidade: {args.city}")
    logger.info(f"Limite: {args.limit}")
    
    try:
        # 1. Busca
        results = google_maps_searcher.search_businesses(args.query, args.city, limit=args.limit)
        
        if not results:
            logger.warning("Nenhum resultado encontrado no Google Maps.")
            return

        # 2. Valida e Salva
        stats = google_maps_searcher.validate_and_save_leads(results)
        
        logger.info("=== Relatório da Busca ===")
        logger.info(f"Encontrados (Google): {stats['encontrados']}")
        logger.info(f"Com Telefone: {stats['com_telefone']}")
        logger.info(f"Duplicados (Ignorados): {stats['duplicados']}")
        logger.info(f"Com WhatsApp (Válidos): {stats['com_whatsapp']}")
        logger.info(f"Salvos no DB: {stats['salvos']}")
        logger.info("==========================")
        
    except KeyboardInterrupt:
        logger.info("Operação interrompida pelo usuário.")
    except Exception as e:
        logger.critical(f"Erro fatal na busca: {e}")

if __name__ == "__main__":
    main()
