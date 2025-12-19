
import logging
import time
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from .logger import logger

def get_retry_decorator(
    max_attempts: int = 3,
    min_seconds: int = 2,
    max_seconds: int = 10,
    exceptions: tuple = (Exception,)
):
    """
    Retorna um decorator de retry configurado.
    
    Args:
        max_attempts: Número máximo de tentativas.
        min_seconds: Tempo mínimo de espera (base do exponencial).
        max_seconds: Tempo máximo de espera entre tentativas.
        exceptions: Tupla de classes de exceção para capturar.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )

def retry_with_logging(func=None, max_attempts=3, min_seconds=2, max_seconds=10, exceptions=(Exception,)):
    """
    Decorator facilitador para usar em funções.
    Pode ser usado como @retry_with_logging ou @retry_with_logging(max_attempts=5)
    """
    if func is None:
        return lambda f: retry_with_logging(
            f, max_attempts=max_attempts, min_seconds=min_seconds, 
            max_seconds=max_seconds, exceptions=exceptions
        )

    decorator = get_retry_decorator(max_attempts, min_seconds, max_seconds, exceptions)
    return decorator(func)
