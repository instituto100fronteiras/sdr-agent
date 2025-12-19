
import sys
import signal
import os
import atexit
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.scheduler import run_scheduler
from utils.logger import logger

PID_FILE = Path(__file__).resolve().parent.parent / "logs" / "scheduler.pid"

def remove_pid_file():
    """Remove o arquivo de PID ao encerrar."""
    if PID_FILE.exists():
        try:
            PID_FILE.unlink()
        except OSError as e:
            logger.error(f"Erro ao remover PID file: {e}")

def check_pid_file():
    """Verifica se já existe um processo rodando."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Verifica se o processo ainda existe
            try:
                os.kill(old_pid, 0)
                logger.error(f"Já existe uma instância rodando (PID: {old_pid}). Abortando.")
                sys.exit(1)
            except OSError:
                # Processo não existe, arquivo é "stale"
                logger.warning("Encontrado PID file antigo. Removendo.")
                remove_pid_file()
        except ValueError:
            remove_pid_file()

def write_pid_file():
    """Escreve o PID atual no arquivo."""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def handle_exit(signum, frame):
    """Trata sinais de encerramento (CTRL+C, SIGTERM)."""
    logger.info(f"Recebido sinal de parada ({signum}). Encerrando scheduler...")
    remove_pid_file()
    sys.exit(0)

def main():
    check_pid_file()
    write_pid_file()
    
    # Garante limpeza na saída
    atexit.register(remove_pid_file)
    
    # Registra handlers de sinal
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    pid = os.getpid()
    logger.info(f"Iniciando processo do Scheduler (PID: {pid})")
    
    try:
        run_scheduler()
    except Exception as e:
        logger.critical(f"O Scheduler caiu inesperadamente: {e}")
        remove_pid_file()
        sys.exit(1)

if __name__ == "__main__":
    main()
