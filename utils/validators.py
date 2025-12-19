
import re
from datetime import datetime
import pytz
from config.settings import (
    TIMEZONE,
    WORK_HOURS_MORNING_START,
    WORK_HOURS_MORNING_END,
    WORK_HOURS_AFTERNOON_START,
    WORK_HOURS_AFTERNOON_END
)
from .logger import logger

def normalize_phone(phone: str) -> str:
    """
    Remove todos os caracteres não numéricos do telefone.
    Retorna apenas dígitos.
    """
    if not phone:
        return ""
    return re.sub(r'\D', '', str(phone))

def validate_phone_br(phone: str) -> bool:
    """
    Valida telefone brasileiro (celular).
    Espera formato com DDI 55 + DDD (2 dígitos) + 9 + 8 dígitos.
    """
    normalized = normalize_phone(phone)
    # 55 + 2 (DDD) + 1 (9) + 8 (número) = 13 dígitos
    # Aceita também sem o 9 extra em alguns casos legados, mas o padrão é 13 ou 12.
    # Regex simplificado: ^55\d{10,11}$
    return bool(re.match(r'^55[1-9]{2}9?\d{8}$', normalized))

def validate_phone_py(phone: str) -> bool:
    """
    Valida telefone paraguaio.
    DDI 595 + 9 dígitos (geralmente).
    Ex: 595 9XX XXX XXX
    """
    normalized = normalize_phone(phone)
    # 595 + 9 dígitos = 12 dígitos
    return bool(re.match(r'^5959\d{8}$', normalized))

def validate_phone_ar(phone: str) -> bool:
    """
    Valida telefone argentino.
    DDI 54 + 9 + código área + número.
    Móveis na argentina usam 9 após o DDI 54.
    """
    normalized = normalize_phone(phone)
    # 54 + 9 + 10 a 11 dígitos variáveis dependendo da área
    return bool(re.match(r'^549\d{10,11}$', normalized))

def validate_phone(phone: str) -> bool:
    """
    Valida se o telefone pertence a algum dos países suportados (BR, PY, AR).
    """
    return validate_phone_br(phone) or validate_phone_py(phone) or validate_phone_ar(phone)

def is_working_hours() -> bool:
    """
    Verifica se o horário atual está dentro do horário comercial configurado.
    Considera timezone, dias da semana (Seg-Sex) e intervalos.
    """
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)

    # Verifica final de semana (0=Segunda, 6=Domingo)
    if now.weekday() >= 5:
        logger.info("Fora do horário: Final de semana.")
        return False

    current_time = now.strftime("%H:%M")

    # Verifica janelas de horário
    is_morning = WORK_HOURS_MORNING_START <= current_time <= WORK_HOURS_MORNING_END
    is_afternoon = WORK_HOURS_AFTERNOON_START <= current_time <= WORK_HOURS_AFTERNOON_END

    if is_morning or is_afternoon:
        return True
    
    logger.info(f"Fora do horário comercial: {current_time}")
    return False
