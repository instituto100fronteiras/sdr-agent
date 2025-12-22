
import os
from integrations.supabase_client import supabase
from services.message_service import message_service
# Falta importar o controlador global do agente se existir, ou usar DB para controle de estado.
# Vamos assumir controle via DB (tabela agent_state ou config no env/memory).
# Por simplificação, vamos assumir que existe uma flag no DB ou no settings que o agente lê.

def toggle_agent_status(active: bool):
    """Pausa ou Retoma o agente."""
    # Como o agente roda em loop, o ideal é ter uma tabela de configuração no banco.
    # Vou sugerir criar/usar a tabela 'agent_state' (que já vi no supabase_client)
    try:
        # Atualiza status_message ou similar para indicar pausa
        # Ou cria uma tabela 'settings' no supabase
        # Por enquanto faz mock no print e tenta salvar estado
        
        state = supabase.get_agent_state()
        new_state = {"is_active": active} # Adicionar campo is_active no state se não tiver
        
        # Update via supabase client (usando método genérico se tiver ou direto)
        # O método update_agent_state existe em integration
        supabase.update_agent_state(new_state)
        return True
    except Exception as e:
        print(f"Erro ao alterar status: {e}")
        return False

def get_agent_status():
    """Retorna estado atual."""
    try:
        state = supabase.get_agent_state()
        return state.get("is_active", True)
    except:
        return True

def send_manual_message(lead_id: str, message: str, phone: str = None):
    """Envia mensagem manual."""
    try:
        # Se não tem phone, busca do lead
        if not phone:
            lead = supabase.client.table("leads").select("phone").eq("id", lead_id).single().execute()
            phone = lead.data['phone']
            
        # Usa MessageService
        # message_service.send_message_via_evolution(phone, message) # Método privado/interno
        # Vamos usar a evolution integration direto ou expor metodo no service
        from integrations.evolution import evolution_client
        
        if evolution_client.send_message(phone, message):
            # Log
            supabase.log_message(lead_id, "outbound", message)
            return True
        return False
    except Exception as e:
        print(f"Erro ao enviar mensagem manual: {e}")
        return False

def update_lead_status(lead_id: str, new_status: str):
    """Atualiza status do lead."""
    try:
        supabase.update_lead(lead_id, {"status": new_status})
        return True
    except:
        return False
