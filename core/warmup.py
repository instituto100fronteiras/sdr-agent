
from datetime import datetime, date
from config.settings import WARMUP_ENABLED, WARMUP_START_DATE
from integrations.supabase_client import supabase
from utils.validators import is_working_hours
from utils.logger import logger

class WarmupManager:
    def __init__(self):
        self.enabled = WARMUP_ENABLED
        self.start_date = None
        
        if self.enabled and WARMUP_START_DATE:
            try:
                self.start_date = datetime.strptime(WARMUP_START_DATE, "%Y-%m-%d").date()
            except ValueError:
                logger.error(f"Data de warm-up inválida: {WARMUP_START_DATE}")
                self.enabled = False

    def get_max_messages_today(self) -> int:
        """
        Calcula o limite diário de mensagens baseado na tabela de aquecimento.
        """
        if not self.enabled or not self.start_date:
            return 1000  # Limite alto se warm-up desligado (mas seguro)

        days_diff = (date.today() - self.start_date).days
        
        if days_diff < 0:
            return 0 # Ainda não começou
            
        # Tabela de Warm-up
        if days_diff <= 3:
            return 5
        elif days_diff <= 7:
            return 10
        elif days_diff <= 14:
            return 15
        elif days_diff <= 21:
            return 20
        else:
            return 25

    def can_send_now(self) -> bool:
        """
        Verifica se pode enviar mensagem agora.
        Considera:
        1. Horário comercial
        2. Limite diário (warm-up)
        """
        if not is_working_hours():
            logger.info("Tentativa de envio fora do horário comercial.")
            return False

        current_state = supabase.get_agent_state()
        
        # Verifica se mudou o dia para resetar contador (caso o script rode contínuo)
        last_day_str = current_state.get("current_day")
        if last_day_str != date.today().isoformat():
            self.reset_daily_count()
            current_state = supabase.get_agent_state() # Recarrega estado zerado

        sent_today = current_state.get("messages_sent_today", 0)
        limit = self.get_max_messages_today()

        if sent_today >= limit:
            logger.info(f"Limite diário atingido: {sent_today}/{limit}")
            return False

        return True

    def increment_daily_count(self):
        """Incrementa o contador de mensagens enviadas hoje."""
        current = supabase.get_agent_state()
        new_count = current.get("messages_sent_today", 0) + 1
        
        supabase.update_agent_state({
            "messages_sent_today": new_count,
            "last_active": datetime.utcnow().isoformat()
        })
        logger.debug(f"Contador diário incrementado: {new_count}")

    def reset_daily_count(self):
        """Reseta o contador (chamado na virada do dia)."""
        supabase.update_agent_state({
            "messages_sent_today": 0,
            "current_day": date.today().isoformat()
        })
        logger.info("Contador diário resetado.")

# Instância global
warmup = WarmupManager()
