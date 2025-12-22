
from typing import Dict, Any, Optional
from datetime import datetime
from integrations.trello import trello_client
from integrations.supabase_client import supabase
from config.settings import (
    TRELLO_LIST_COLD,
    TRELLO_LIST_CONNECTION,
    TRELLO_LIST_INTERESTED,
    TRELLO_LIST_ARCHIVED
)
from utils.logger import logger

class TrelloService:
    def __init__(self):
        self.client = trello_client
        self.db = supabase

    def create_lead_card(self, lead: Dict[str, Any]) -> Optional[str]:
        """
        Cria card na lista COLD para um novo lead contactado.
        """
        if not TRELLO_LIST_COLD:
            logger.warning("TRELLO_LIST_COLD não configurada. Card não será criado.")
            return None

        try:
            # Formata Nome: "{Empresa} - {Nome}" ou apenas "{Nome}"
            company = lead.get('company')
            name = lead.get('name')
            card_name = f"{company} - {name}" if company else name
            
            # Formata Descrição
            phone = lead.get('phone')
            city = lead.get('city', 'N/A')
            sector = lead.get('sector', 'N/A')
            website = lead.get('website', 'N/A')
            
            description = (
                f"**Telefone:** {phone}\n"
                f"**Cidade:** {city}\n"
                f"**Setor:** {sector}\n"
                f"**Website:** {website}\n"
                f"**Data Contato:** {datetime.now().strftime('%d/%m/%Y')}"
            )

            # Cria Card
            card_id = self.client.create_card(TRELLO_LIST_COLD, card_name, description)
            
            if card_id:
                # Salva ID no Supabase (precisa ter campo trello_card_id na tabela leads ou metadata)
                # Assumindo que podemos salvar em metadata por enquanto se não houver coluna
                # Mas o ideal é salvar onde der. Vamos tentar update_lead.
                
                # TODO: Garantir que tabela leads tem coluna trello_card_id ou usar jsonb
                # Por hora, vamos tentar atualizar via update_lead se existir campo, 
                # senão logamos que foi criado mas não vinculado.
                
                try:
                    self.db.update_lead(lead['id'], {"trello_card_id": card_id})
                except Exception as db_e:
                    logger.warning(f"Erro ao salvar trello_card_id no DB: {db_e}")

                # Comentário Inicial
                self.client.add_comment(card_id, "Primeiro contato enviado via SDR Agent")
                
                return card_id
            
        except Exception as e:
            logger.error(f"Erro no create_lead_card para lead {lead.get('id')}: {e}")
            return None

    def on_lead_responded(self, lead: Dict[str, Any]):
        """
        Move card de COLD para CONNECTION quando lead responde.
        """
        card_id = self._get_card_id(lead)
        if not card_id or not TRELLO_LIST_CONNECTION:
            return

        if self.client.move_card(card_id, TRELLO_LIST_CONNECTION):
            self.client.add_comment(card_id, f"Cliente respondeu em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    def on_lead_interested(self, lead: Dict[str, Any]):
        """
        Move card para INTERESTED.
        """
        card_id = self._get_card_id(lead)
        if not card_id or not TRELLO_LIST_INTERESTED:
            return

        if self.client.move_card(card_id, TRELLO_LIST_INTERESTED):
            self.client.add_comment(card_id, "Cliente demonstrou interesse!")

    def on_lead_declined(self, lead: Dict[str, Any], reason: str = "Desconhecido"):
        """
        Move card para ARCHIVED.
        """
        card_id = self._get_card_id(lead)
        if not card_id or not TRELLO_LIST_ARCHIVED:
            return

        if self.client.move_card(card_id, TRELLO_LIST_ARCHIVED):
            self.client.add_comment(card_id, f"Cliente recusou ou pediu para parar. Motivo: {reason}")
            # Opcional: Arquivar de fato (sumir da lista) ou deixar na lista 'Arquivados'
            # Users request: "Move card to ARCHIVED" -> lista visual.
            # Também podemos chamar self.client.archive_card(card_id) se quiser sumir com ele.
            # Vamos manter na lista visual por enquanto.

    def _get_card_id(self, lead: Dict[str, Any]) -> Optional[str]:
        """Recupera ID do card do lead, buscando no Trello se não tiver no DB."""
        # 1. Tenta pegar do lead (se já tiver sido salvo)
        if lead.get("trello_card_id"):
            return lead.get("trello_card_id")
            
        # 2. Se não tem, tenta buscar no Trello pelo telefone
        phone = lead.get("phone")
        if phone:
            card_id = self.client.find_card_by_desc_term(phone)
            if card_id:
                # Atualiza DB para evitar busca futura
                try:
                    self.db.update_lead(lead['id'], {"trello_card_id": card_id})
                except: pass
                return card_id
        
        return None

    def sync_pending_actions(self):
        """
        Placeholder para retries.
        Pode ler de uma tabela 'sync_queue' no BD.
        """
        pass

# Instância global
trello_service = TrelloService()
