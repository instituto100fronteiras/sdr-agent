
import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Certifique-se de que o diretório de logs existe
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "sdr_agent.log"

def setup_logger(name: str = "sdr_agent") -> logging.Logger:
    """
    Configura e retorna um logger com rotação diária de arquivo e saída no console.
    Formato: [TIMESTAMP] [LEVEL] [MODULE] message
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evita duplicação de handlers se o logger já estiver configurado
    if logger.hasHandlers():
        return logger

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler (Rotação Diária)
    file_handler = TimedRotatingFileHandler(
        filename=LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=30, # Mantém logs por 30 dias
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Adiciona handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Instância padrão para uso rápido
logger = setup_logger()
