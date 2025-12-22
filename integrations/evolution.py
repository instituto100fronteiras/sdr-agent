
import requests
import time
from typing import List, Optional, Dict, Any
from config.settings import (
    EVOLUTION_API_URL, 
    EVOLUTION_API_KEY, 
    EVOLUTION_INSTANCE_NAME
)
from utils.logger import logger
from utils.retry import retry_with_logging

class EvolutionClient:
    def __init__(self):
        if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
            raise ValueError("Evolution API credenciais não configuradas.")
        
        self.base_url = EVOLUTION_API_URL.rstrip('/')
        self.api_key = EVOLUTION_API_KEY
        self.instance = EVOLUTION_INSTANCE_NAME
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    @retry_with_logging(max_attempts=3)
    def send_text_message(self, phone: str, text: str) -> Optional[Dict[str, Any]]:
        """Envia uma mensagem de texto simples."""
        try:
            url = f"{self.base_url}/message/sendText/{self.instance}"
            payload = {
                "number": phone,
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": False
                },
                "textMessage": {
                    "text": text
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {phone}: {e}")
            raise

    def send_text_in_parts(self, phone: str, text: str) -> List[Dict[str, Any]]:
        """
        Envia mensagem dividida em partes (balões) de ~200 caracteres,
        respeitando pontuação para quebra natural.
        """
        parts = self._split_text(text)
        results = []
        
        for i, part in enumerate(parts):
            # Adiciona delay maior entre mensagens se não for a primeira
            if i > 0:
                time.sleep(3) 

            result = self.send_text_message(phone, part)
            results.append(result)
            
        return results

    def _split_text(self, text: str, max_len: int = 200) -> List[str]:
        """Auxiliar para dividir texto inteligentemente."""
        if len(text) <= max_len:
            return [text]
            
        parts = []
        while text:
            if len(text) <= max_len:
                parts.append(text)
                break
                
            # Tenta quebrar na última pontuação ou espaço antes do limite
            split_at = -1
            chunk = text[:max_len]
            
            # Prioridade de quebra: \n > . > , > espaço
            for char in ['\n', '.', '!', '?', ',', ' ']:
                last_idx = chunk.rfind(char)
                if last_idx != -1:
                    # Inclui o caractere na quebra
                    split_at = last_idx + 1 
                    break
            
            if split_at == -1:
                split_at = max_len # Força quebra se não achar ponto natural
                
            parts.append(text[:split_at].strip())
            text = text[split_at:].strip()
            
        return parts

    @retry_with_logging(max_attempts=3)
    def check_number_exists(self, phone: str) -> bool:
        """
        Verifica se o número existe no WhatsApp.
        Usa o endpoint v2: POST /chat/whatsappNumbers/{instance}
        """
        try:
            url = f"{self.base_url}/chat/whatsappNumbers/{self.instance}"
            payload = {"numbers": [phone]}
            
            # Endpoint v2 é POST
            response = requests.post(url, json=payload, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            # Resposta v2: [{ "number": "...", "exists": true, "jid": "..." }]
            if isinstance(data, list):
                if not data: return False
                return data[0].get('exists', False)
            return data.get('exists', False)
            
        except Exception as e:
            logger.warning(f"Erro ao verificar número {phone}: {e}")
            # Em caso de erro de API, assumimos False (fail safe) para não spammar inválidos
            return False 

    def get_message_status(self, message_id: str) -> str:
        """
        Consulta status da mensagem.
        Evolution API foca em Webhooks, mas mantemos interface.
        """
        # Placeholder pois polling não é o padrão da Evolution
        return "unknown"

# Instância global
try:
    evolution = EvolutionClient()
except Exception as e:
    logger.warning(f"Não foi possível inicializar EvolutionClient: {e}")
    evolution = None
