
import time
import schedule
from datetime import datetime
from config.settings import MESSAGE_INTERVAL_MINUTES
from services.lead_service import lead_service
from services.message_service import message_service
from core.warmup import warmup
from integrations.supabase_client import supabase
from utils.logger import logger
from utils.validators import is_working_hours

def heartbeat():
    """Atualiza o timestamp de última atividade do agente."""
    try:
        supabase.update_agent_state({"last_heartbeat": datetime.utcnow().isoformat()})
        logger.debug("Heartbeat enviado.")
    except Exception as e:
        logger.debug(f"Falha no heartbeat: {e}")

def process_next_lead():
    """
    Lógica principal de processamento.
    Tentativa de processar um lead se as condições permitirem.
    """
    logger.info("Iniciando ciclo de processamento...")

    # 1. Verifica Horário
    if not is_working_hours():
        logger.info("Fora do horário comercial. Aguardando...")
        return

    # 2. Verifica Warm-up / Limites
    if not warmup.can_send_now():
        logger.info("Limite de envio atingido ou warm-up não permite. Aguardando...")
        return

    # 3. Busca Próximo Lead
    try:
        lead = lead_service.get_next_to_contact()
        
        if not lead:
            logger.info("Nenhum lead pendente para contato no momento.")
            return

        logger.info(f"Processando lead: {lead.get('name')} ({lead.get('phone')}) - Status: {lead.get('status')}")

        # 4. Envia Mensagem (First Contact ou Follow-up)
        success = False
        status = lead.get("status")

        if status == "new":
            success = message_service.send_first_contact(lead)
        elif status == "follow_up_scheduled":
             # Calcula qual número de follow-up é baseado no histórico ou contador
             # Simplificação para Fase 1: assume que 'contact_count' começa em 0 e incrementa
             # Se status é follow_up_scheduled, já foi contactado pelo menos 1 vez.
             current_count = lead.get("contact_count", 0)
             # O próximo envio será o count atual + 1 (ex: se fez 1 contato, agora é o follow-up 1 (que seria a 2ª msg))
             # Ajuste na lógica: send_followup recebe o número do followup.
             # Se contact_count=1 (já mandou First Contact), então agora é Followup #1.
             success = message_service.send_followup(lead, followup_number=current_count)
             if success:
                 # Incrementa contador
                 supabase.update_lead(lead["id"], {"contact_count": current_count + 1})

        if success:
            warmup.increment_daily_count()
            logger.info(f"Mensagem enviada com sucesso para {lead.get('phone')}")
        else:
            logger.warning(f"Falha ao processar lead {lead.get('phone')}")

    except Exception as e:
        logger.error(f"Erro crítico no ciclo de processamento: {e}")

def run_scheduler():
    """Loop principal do agente."""
    logger.info("Iniciando Scheduler do SDR Agent...")
    
    # Agenda Heartbeat a cada 5 minutos
    schedule.every(5).minutes.do(heartbeat)
    
    # Agenda processamento principal
    # Usamos o intervalo configurado. 
    # Note que 'schedule' roda job periodicamente. 
    schedule.every(MESSAGE_INTERVAL_MINUTES).minutes.do(process_next_lead)

    # Executa uma vez imediatamente ao iniciar (opcional, para não esperar 30min no boot)
    process_next_lead()

    while True:
        try:
            schedule.run_pending()
            time.sleep(60) # Verifica agendamentos a cada minuto
        except KeyboardInterrupt:
            logger.info("Scheduler interrompido pelo usuário.")
            break
        except Exception as e:
            logger.error(f"Erro inesperado no loop principal: {e}")
            time.sleep(60) # Espera um pouco antes de retomar em caso de crash

if __name__ == "__main__":
    run_scheduler()
