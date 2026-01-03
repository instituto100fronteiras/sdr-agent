
import requests
from typing import List, Dict, Any
from serpapi import GoogleSearch
from config.settings import SERPAPI_KEY, SERPAPI_ENABLED
from integrations.supabase_client import supabase
from integrations.chatwoot import chatwoot
from integrations.evolution import evolution
from utils.logger import logger
from utils.validators import normalize_phone

class GoogleMapsSearcher:
    def __init__(self):
        if not SERPAPI_KEY:
            raise ValueError("SERPAPI_KEY não configurada.")

    def search_businesses(self, query: str, city: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Busca empresas no Google Maps via SerpAPI.
        """
        if not SERPAPI_ENABLED:
            logger.warning("SERPAPI_ENABLED is False. Skipping search.")
            return []

        logger.info(f"Buscando '{query}' em '{city}' via Google Maps (Limit: {limit})...")
        
        full_query = f"{query} em {city}"
        
        params = {
            "engine": "google_maps",
            "q": full_query,
            "api_key": SERPAPI_KEY,
            "hl": "pt-br",
            "num": limit # Nota: SerpAPI maps geralmente pagina de 20 em 20
        }

        try:
            # Usando requests direto como no exemplo do user, ou a lib oficial se preferir
            # O exemplo do user usava requests, vamos usar requests para garantir compatibilidade
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            local_results = data.get("local_results", [])
            
            # Se precisar de mais resultados (paginação), teríamos que implementar loop com 'serpapi_pagination'
            # Por enquanto, vamos focar na primeira paǵina de resultados (até 20)
            
            parsed_results = []
            for item in local_results:
                parsed_results.append({
                    "name": item.get("title"),
                    "phone": item.get("phone"),
                    "address": item.get("address"),
                    "website": item.get("website"),
                    "rating": item.get("rating"),
                    "reviews": item.get("reviews"),
                    "place_id": item.get("place_id"),
                    "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{item.get('place_id')}" if item.get("place_id") else None
                })
                
            logger.info(f"Encontrados {len(parsed_results)} resultados brutos.")
            return parsed_results
            
        except Exception as e:
            logger.error(f"Erro na busca SerpAPI: {e}")
            return []

    def validate_and_save_leads(self, results: List[Dict[str, Any]], skip_validation: bool = False) -> Dict[str, int]:
        """
        Valida telefones (WhatsApp), checa duplicidade e salva.
        """
        stats = {
            "encontrados": len(results),
            "com_telefone": 0,
            "com_whatsapp": 0,
            "salvos": 0,
            "duplicados": 0
        }
        
        logger.info("Iniciando validação e salvamento...")
        
        for item in results:
            raw_phone = item.get("phone")
            
            # 1. Filtra sem telefone
            if not raw_phone:
                continue
            
            try:
                # Normaliza
                phone = normalize_phone(raw_phone)
                stats["com_telefone"] += 1
                
                # 2. Check Duplicidade Supabase
                if supabase.get_lead_by_phone(phone):
                    logger.debug(f"Duplicado no Supabase: {phone}")
                    stats["duplicados"] += 1
                    continue
                    
                # 3. Check Duplicidade Chatwoot (evitar incomodar cliente antigo)
                if chatwoot and chatwoot.find_contact_by_phone(phone):
                     logger.debug(f"Duplicado no Chatwoot: {phone}")
                     stats["duplicados"] += 1
                     continue
                
                # 4. Valida WhatsApp (Evolution)
                is_whatsapp = False
                
                if skip_validation:
                     # Se pulou validação, assumimos que é válido (ou pelo menos tentaremos salvar)
                     is_whatsapp = True
                     logger.debug(f"PULANDO validação de WhatsApp para: {phone}")
                elif evolution:
                    # check_number_exists pode ser lento, cuidado com rate limit em loops grandes
                    is_whatsapp = evolution.check_number_exists(phone)
                
                if not is_whatsapp:
                    logger.debug(f"Não é WhatsApp (ou falha valid.): {phone}")
                    continue
                    
                if not skip_validation: # Só conta como 'com_whatsapp' se foi validado
                    stats["com_whatsapp"] += 1
                
                # 5. Salva (Criar Lead)
                lead_data = {
                    "name": item["name"],
                    "phone": phone,
                    "status": "new",
                    "source": "google_maps",
                    "notes": f"Rating: {item.get('rating')} ({item.get('reviews')} reviews). Address: {item.get('address')}",
                    # Campos extras podem ir em 'metadata' se existir coluna JSONB, ou concatenados nas notas
                }
                
                supabase.create_lead(lead_data)
                stats["salvos"] += 1
                logger.info(f"Lead salvo: {item['name']} ({phone})")
                
            except Exception as e:
                logger.error(f"Erro ao processar item {item.get('name')}: {e}")
                
        return stats

# Instância global
google_maps_searcher = GoogleMapsSearcher()
