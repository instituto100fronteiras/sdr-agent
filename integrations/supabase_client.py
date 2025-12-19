
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from config.settings import SUPABASE_URL, SUPABASE_KEY
from utils.logger import logger
from utils.retry import retry_with_logging

class SupabaseClient:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credenciais não configuradas.")
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    @retry_with_logging(max_attempts=3)
    def get_lead_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Busca um lead pelo telefone."""
        try:
            response = self.client.table("leads").select("*").eq("phone", phone).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar lead por telefone {phone}: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def create_lead(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo lead."""
        try:
            # Adiciona timestamps se não existirem
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table("leads").insert(data).execute()
            logger.info(f"Lead criado: {data.get('phone')}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao criar lead: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza dados de um lead."""
        try:
            data["updated_at"] = datetime.utcnow().isoformat()
            response = self.client.table("leads").update(data).eq("id", lead_id).execute()
            logger.info(f"Lead atualizado: {lead_id}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar lead {lead_id}: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def get_leads_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Busca leads por status."""
        try:
            response = self.client.table("leads").select("*").eq("status", status).execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar leads por status {status}: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def get_next_lead_to_contact(self) -> Optional[Dict[str, Any]]:
        """
        Busca o próximo lead para contato.
        Regra: Status 'new' ou 'follow_up_scheduled' com data <= agora.
        Ordena por prioridade ou data de criação.
        """
        try:
            # Prioriza 'new' por enquanto, pode ser ajustado
            response = self.client.table("leads")\
                .select("*")\
                .eq("status", "new")\
                .order("created_at", desc=False)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            
            # Se não tem 'new', verifica agendados (lógica simples por enquanto)
            now = datetime.utcnow().isoformat()
            response = self.client.table("leads")\
                .select("*")\
                .eq("status", "follow_up_scheduled")\
                .lte("next_contact_at", now)\
                .order("next_contact_at", desc=False)\
                .limit(1)\
                .execute()

            if response.data:
                return response.data[0]

            return None
        except Exception as e:
            logger.error(f"Erro ao buscar próximo lead: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def log_message(self, lead_id: str, direction: str, content: str) -> Dict[str, Any]:
        """
        Registra uma mensagem no histórico.
        direction: 'inbound' ou 'outbound'
        """
        try:
            data = {
                "lead_id": lead_id,
                "direction": direction,
                "content": content,
                "sent_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("message_logs").insert(data).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao logar mensagem para lead {lead_id}: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def get_agent_state(self) -> Dict[str, Any]:
        """Recupera o estado atual do agente (ex: contadores diários)."""
        try:
            # Assume que existe uma tabela 'agent_state' com apenas uma linha ou chave fixa
            response = self.client.table("agent_state").select("*").limit(1).execute()
            if response.data:
                return response.data[0]
            # Se não existir, cria um estado inicial
            initial_state = {
                "messages_sent_today": 0,
                "last_active": datetime.utcnow().isoformat(),
                "current_day": datetime.now().date().isoformat()
            }
            return self.update_agent_state(initial_state)
        except Exception as e:
            logger.error(f"Erro ao buscar estado do agente: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def update_agent_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza o estado do agente."""
        try:
            # Primeiro verifica se existe para fazer update ou insert
            # Simplificação: assume que ID 1 é o singleton do estado
            data["updated_at"] = datetime.utcnow().isoformat()
            
            # Tenta update primeiro (assumindo id=1 fixo para simplicidade ou via tabela single row)
             # Na prática, vamos tentar buscar o primeiro registro de novo para pegar o ID
            existing = self.client.table("agent_state").select("id").limit(1).execute()
            
            if existing.data:
                state_id = existing.data[0]['id']
                response = self.client.table("agent_state").update(data).eq("id", state_id).execute()
            else:
                response = self.client.table("agent_state").insert(data).execute()
                
            return response.data[0]
        except Exception as e:
            logger.error(f"Erro ao atualizar estado do agente: {e}")
            raise

    @retry_with_logging(max_attempts=3)
    def add_to_sync_queue(self, integration: str, action: str, payload: Dict[str, Any]):
        """Adiciona uma tarefa à fila de sincronização (ex: Trello)."""
        try:
            data = {
                "integration": integration,
                "action": action,
                "payload": payload,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            self.client.table("sync_queue").insert(data).execute()
            logger.info(f"Adicionado à fila de sync: {integration} - {action}")
        except Exception as e:
            logger.error(f"Erro ao adicionar à fila de sync: {e}")
            raise

# Instância global
try:
    supabase = SupabaseClient()
except Exception as e:
    logger.warning(f"Não foi possível inicializar SupabaseClient: {e}")
    supabase = None
