
import random
from typing import Dict, Any, Optional
from config.templates import format_message
from integrations.evolution import evolution
from integrations.chatwoot import chatwoot
from integrations.supabase_client import supabase
from services.lead_service import lead_service
from utils.logger import logger

class MessageService:
    def __init__(self):
        self.evolution = evolution
        self.chatwoot = chatwoot
        self.db = supabase
        self.lead_service = lead_service

    def send_first_contact(self, lead: Dict[str, Any]) -> bool:
        """
        Envia a primeira mensagem de contato para um lead.
        Escolhe um template aleatório (A, B, C).
        """
        phone = lead.get("phone")
        nome = lead.get("name")
        empresa = lead.get("company")
        setor = lead.get("sector")
        
        # 1. Dupla verificação no Chatwoot (Segurança)
        if self._check_exists_in_chatwoot(phone):
            logger.warning(f"Abortando envio para {phone}: Já existe no Chatwoot.")
            self.lead_service.mark_as_declined(lead["id"]) # Ou outro status apropriado
            return False

        # 2. Escolhe Template
        template_id = random.choice(["A", "B", "C"])
        try:
            message_text = format_message(template_id, nome, empresa, setor)
        except Exception as e:
            logger.error(f"Erro ao formatar template {template_id} para {phone}: {e}")
            return False

        # 3. Envia Mensagem
        try:
            # Usa send_text_in_parts para parecer mais natural se for longo
            self.evolution.send_text_in_parts(phone, message_text)
            
            # 4. Logs e Atualizações
            self.db.log_message(lead["id"], "outbound", message_text)
            self.lead_service.mark_as_contacted(lead["id"], template_id)
            
            # Agenda follow-up automático para daqui 2 dias (exemplo)
            self.lead_service.schedule_followup(lead["id"], days=2)
            
            logger.info(f"Primeiro contato enviado para {phone} (Template {template_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar first contact para {phone}: {e}")
            return False

    def send_followup(self, lead: Dict[str, Any], followup_number: int = 1) -> bool:
        """
        Envia mensagem de follow-up.
        """
        phone = lead.get("phone")
        nome = lead.get("name")

        if self._check_exists_in_chatwoot(phone):
            logger.warning(f"Abortando follow-up para {phone}: Já existe no Chatwoot.")
            return False

        # Templates simples de follow-up (hardcoded por enquanto conforme escopo fase 1)
        if followup_number == 1:
            text = f"Oi {nome}, conseguiu dar uma olhada na minha mensagem anterior?"
        elif followup_number == 2:
            text = f"Olá {nome}, imagino que esteja corrido. Apenas para reforçar que adoraríamos ter a {lead.get('company')} conosco."
        else:
            text = f"{nome}, essa é minha última tentativa. Caso faça sentido no futuro, estou à disposição."

        try:
            self.evolution.send_text_message(phone, text)
            
            self.db.log_message(lead["id"], "outbound", text)
            
            # Se for o último follow-up, talvez não agende o próximo ou mude status
            if followup_number < 3:
                self.lead_service.schedule_followup(lead["id"], days=3)
            else:
                 # Marca como finalizado/perdidou ou mantém apenas no log
                 pass

            logger.info(f"Follow-up {followup_number} enviado para {phone}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar follow-up para {phone}: {e}")
            return False

    def handle_incoming(self, phone: str, content: str):
        """
        Processa mensagens recebidas (Webhook).
        """
        # Verifica se é um lead nosso
        lead = self.db.get_lead_by_phone(phone)
        
        if not lead:
            logger.info(f"Mensagem recebida de desconhecido {phone}. Ignorando processamento de lead.")
            return

        # Loga a mensagem inbound
        self.db.log_message(lead["id"], "inbound", content)
        
        # Palavras de parada (Stop words)
        content_lower = content.lower()
        stop_words = ["pare", "stop", "nao quero", "não quero", "remover", "sair"]
        
        if any(w in content_lower for w in stop_words):
            self.lead_service.mark_as_declined(lead["id"])
            logger.info(f"Lead {phone} solicitou parada.")
            return

        # Se respondeu qualquer outra coisa, marcamos como respondido (Handover)
        if lead["status"] not in ["responded", "declined", "converted"]:
            self.lead_service.mark_as_responded(lead["id"])
            logger.info(f"Lead {phone} respondeu. Status atualizado para 'responded'.")

    def _check_exists_in_chatwoot(self, phone: str) -> bool:
        """Verifica se o contato já existe no Chatwoot."""
        try:
            contact_id = self.chatwoot.find_contact_by_phone(phone)
            return contact_id is not None
        except Exception:
            # Se der erro na verificação, assume False para não bloquear (ou True para segurar)
            # Fail-safe: Se não conseguir checar, loga erro e permite (ou bloqueia). 
            # Decisão: Por segurança, se a API do Chatwoot estiver fora, melhor não mandar mensagem fria.
            return True 

# Instância global
message_service = MessageService()
