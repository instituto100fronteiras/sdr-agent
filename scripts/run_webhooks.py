
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from api.webhooks import start_server
from utils.logger import setup_logger

if __name__ == "__main__":
    # Configura o logger para este processo
    setup_logger("webhook_server")
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServidor de webhooks interrompido.")
    except Exception as e:
        print(f"Erro fatal no servidor de webhooks: {e}")
