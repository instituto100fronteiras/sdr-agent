
import requests
from typing import Optional, List, Dict, Any
from config.settings import (
    CHATWOOT_API_URL,
    CHATWOOT_API_TOKEN,
    CHATWOOT_ACCOUNT_ID
)
from utils.logger import logger
from utils.retry import retry_with_logging

class ChatwootClient:
    def __init__(self):
        if not CHATWOOT_API_URL or not CHATWOOT_API_TOKEN or not CHATWOOT_ACCOUNT_ID:
            raise ValueError("Chatwoot credenciais não configuradas.")
        
        self.base_url = CHATWOOT_API_URL.rstrip('/')
        self.api_token = CHATWOOT_API_TOKEN
        self.account_id = CHATWOOT_ACCOUNT_ID
        self.headers = {
            "api_access_token": self.api_token,
            "Content-Type": "application/json"
        }
        
        # Palavras-chave de recusa
        self.declined_keywords = [
            "não tenho interesse", 
            "não quero", 
            "para de mandar", 
            "remova meu número", 
            "não me ligue"
        ]

    @retry_with_logging(max_attempts=3)
    def find_contact_by_phone(self, phone: str) -> Optional[int]:
        """
        Busca um contato pelo telefone.
        Retorna o contact_id se encontrado, ou None.
        """
        try:
            # A busca no Chatwoot geralmente espera o número com +
            search_query = phone if phone.startswith('+') else f"+{phone}"
            
            url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/search"
            params = {"q": search_query}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            payload = data.get("payload", [])
            
            if payload:
                # Retorna o primeiro match
                return payload[0].get("id")
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar contato Chatwoot {phone}: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def get_conversation_history(self, contact_id: int) -> List[Dict[str, Any]]:
        """Recupera as últimas mensagens das conversas do contato."""
        try:
            # 1. Buscar conversas do contato
            url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/{contact_id}/conversations"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            conversations = response.json().get("payload", [])
            messages = []
            
            # 2. Para cada conversa, buscar as mensagens (limitado a 10 no total para o contexto)
            for conv in conversations:
                conv_id = conv.get("id")
                msg_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conv_id}/messages"
                msg_resp = requests.get(msg_url, headers=self.headers, timeout=10)
                
                if msg_resp.status_code == 200:
                    conv_msgs = msg_resp.json().get("payload", [])
                    # Simplificando a estrutura
                    for m in conv_msgs:
                        messages.append({
                            "content": m.get("content"),
                            "sender_type": m.get("sender_type"), # 'Contact' ou 'User'
                            "created_at": m.get("created_at")
                        })
            
            # Ordena por data (mais recente primeiro) e limita
            messages.sort(key=lambda x: x['created_at'], reverse=True)
            return messages[:10]
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico Chatwoot para contato {contact_id}: {e}")
            raise

    def check_if_declined(self, contact_id: int) -> bool:
        """
        Verifica se o contato enviou alguma mensagem de recusa recentemente.
        """
        try:
            history = self.get_conversation_history(contact_id)
            
            for msg in history:
                # Verifica apenas mensagens enviadas pelo contato
                if msg.get("sender_type") == "Contact":
                    content = msg.get("content", "").lower()
                    if any(keyword in content for keyword in self.declined_keywords):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Erro ao verificar recusa para contato {contact_id}: {e}")
            return False

    @retry_with_logging(max_attempts=3)
    def get_all_contacts(self, page: int = 1) -> List[Dict[str, Any]]:
        """Recupera lista de contatos (paginada)."""
        try:
            url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts"
            params = {"page": page, "sort": "-last_activity_at"}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json().get("payload", [])
        except Exception as e:
            logger.error(f"Erro ao buscar contatos página {page}: {e}")
            raise

# Instância global
try:
    chatwoot = ChatwootClient()
except Exception as e:
    logger.warning(f"Não foi possível inicializar ChatwootClient: {e}")
    chatwoot = None
