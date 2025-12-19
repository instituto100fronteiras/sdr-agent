
import csv
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from integrations.supabase_client import supabase
from integrations.chatwoot import chatwoot
from utils.validators import validate_phone, normalize_phone
from utils.logger import logger

class LeadService:
    def __init__(self):
        self.db = supabase
        self.chat_api = chatwoot

    def import_from_csv(self, filepath: str) -> Dict[str, int]:
        """
        Importa leads de um arquivo CSV.
        Colunas esperadas: name, phone, company, sector, city
        """
        stats = {"total": 0, "imported": 0, "skipped": 0, "errors": 0}
        
        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    stats["total"] += 1
                    
                    try:
                        raw_phone = row.get("phone", "")
                        if not validate_phone(raw_phone):
                            logger.warning(f"Telefone inválido ignorado: {raw_phone}")
                            stats["skipped"] += 1
                            continue
                            
                        normalized = normalize_phone(raw_phone)
                        
                        # Verifica se já existe no banco (Supabase)
                        existing = self.db.get_lead_by_phone(normalized)
                        if existing:
                            stats["skipped"] += 1
                            continue

                        # Prepara dados
                        lead_data = {
                            "name": row.get("name"),
                            "phone": normalized,
                            "company": row.get("company"),
                            "sector": row.get("sector"),
                            "city": row.get("city"),
                            "status": "new",
                            "metadata": {}
                        }
                        
                        self.db.create_lead(lead_data)
                        stats["imported"] += 1
                        
                    except Exception as e:
                        logger.error(f"Erro ao importar linha {stats['total']}: {e}")
                        stats["errors"] += 1
                        
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {filepath}")
            raise
            
        return stats

    def get_next_to_contact(self) -> Optional[Dict[str, Any]]:
        """
        Obtém o próximo lead para contato.
        Verifica duplicidade no Chatwoot antes de retornar.
        Se existir no Chatwoot, marca no banco e busca o próximo.
        """
        max_attempts_search = 10  # Evita loop infinito se todos estiverem duplicados
        
        for _ in range(max_attempts_search):
            lead = self.db.get_next_lead_to_contact()
            if not lead:
                return None
                
            phone = lead.get("phone")
            
            # Verificação de segurança: Duplicidade no Chatwoot
            # Se o lead já existe no Chatwoot, não devemos abordar como "frio"
            try:
                contact_id = self.chat_api.find_contact_by_phone(phone)
                
                if contact_id:
                    logger.info(f"Lead {phone} já existe no Chatwoot (ID: {contact_id}). Pulando.")
                    
                    # Verifica se já foi recusado
                    if self.chat_api.check_if_declined(contact_id):
                        self.mark_as_declined(lead["id"])
                    else:
                        # Se existe mas não recusou, talvez já esteja em atendimento humano ou outro fluxo
                        # Marcamos como 'interacted_externally' para não spamar
                        self.db.update_lead(lead["id"], {
                            "status": "interacted_externally",
                            "chatwoot_id": contact_id
                        })
                    
                    # Tenta o próximo no loop
                    continue
                    
            except Exception as e:
                logger.error(f"Erro ao verificar Chatwoot para lead {phone}: {e}")
                # Em caso de erro na verificação externa, talvez seja seguro pular por precaução
                continue

            return lead

        return None

    def mark_as_contacted(self, lead_id: str, template_used: str):
        """Atualiza status para contatado."""
        self.db.update_lead(lead_id, {
            "status": "contacted",
            "last_contact_at": datetime.utcnow().isoformat(),
            "last_template": template_used,
            "contact_count": 1 # Assumindo incremento simples, ideal seria ler e somar
        })

    def mark_as_responded(self, lead_id: str):
        """Atualiza status para respondido (handover)."""
        self.db.update_lead(lead_id, {
            "status": "responded",
            "responded_at": datetime.utcnow().isoformat()
        })

    def mark_as_declined(self, lead_id: str):
        """Atualiza status para recusado."""
        self.db.update_lead(lead_id, {
            "status": "declined",
            "declined_at": datetime.utcnow().isoformat()
        })

    def schedule_followup(self, lead_id: str, days: int):
        """Agenda follow-up."""
        next_date = datetime.utcnow() + timedelta(days=days)
        self.db.update_lead(lead_id, {
            "status": "follow_up_scheduled",
            "next_contact_at": next_date.isoformat()
        })

# Instância global
lead_service = LeadService()
