
import requests
from typing import Optional, List, Dict, Any
from config.settings import (
    TRELLO_API_KEY, 
    TRELLO_TOKEN, 
    TRELLO_BOARD_ID
)
from utils.logger import logger
from utils.retry import retry_with_logging

class TrelloClient:
    def __init__(self):
        self.api_key = TRELLO_API_KEY
        self.token = TRELLO_TOKEN
        self.board_id = TRELLO_BOARD_ID
        self.base_url = "https://api.trello.com/1"
        self.auth_params = {
            "key": self.api_key,
            "token": self.token
        }

    def test_connection(self) -> bool:
        """Testa se as credenciais estão válidas obtendo dados do usuário."""
        try:
            url = f"{self.base_url}/members/me"
            response = requests.get(url, params=self.auth_params, timeout=10)
            response.raise_for_status()
            logger.info(f"Conexão com Trello estabelecida: {response.json().get('username')}")
            return True
        except Exception as e:
            logger.error(f"Falha na conexão com Trello: {e}")
            return False

    def get_board_lists(self) -> List[Dict[str, Any]]:
        """Retorna todas as listas do board configurado."""
        if not self.board_id:
            logger.warning("TRELLO_BOARD_ID não configurado.")
            return []
            
        try:
            url = f"{self.base_url}/boards/{self.board_id}/lists"
            response = requests.get(url, params=self.auth_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao buscar listas do board {self.board_id}: {e}")
            return []

    @retry_with_logging(max_attempts=3)
    def create_card(self, list_id: str, name: str, description: str = "") -> Optional[str]:
        """Cria um card em uma lista e retorna o ID do card."""
        try:
            url = f"{self.base_url}/cards"
            params = {
                **self.auth_params,
                "idList": list_id,
                "name": name,
                "desc": description,
                "pos": "top"
            }
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            card_id = response.json().get("id")
            logger.debug(f"Card criado no Trello: {card_id} ({name})")
            return card_id
        except Exception as e:
            logger.error(f"Erro ao criar card no Trello: {e}")
            return None

    @retry_with_logging(max_attempts=3)
    def move_card(self, card_id: str, list_id: str) -> bool:
        """Move card para outra lista."""
        try:
            url = f"{self.base_url}/cards/{card_id}"
            params = {
                **self.auth_params,
                "idList": list_id
            }
            response = requests.put(url, params=params, timeout=10)
            response.raise_for_status()
            logger.debug(f"Card {card_id} movido para lista {list_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao mover card {card_id}: {e}")
            return False

    def add_comment(self, card_id: str, comment: str) -> bool:
        """Adiciona comentário no card."""
        try:
            url = f"{self.base_url}/cards/{card_id}/actions/comments"
            params = {
                **self.auth_params,
                "text": comment
            }
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Erro ao comentar no card {card_id}: {e}")
            return False
            
    def archive_card(self, card_id: str) -> bool:
        """Arquiva um card (closed=true)."""
        try:
            url = f"{self.base_url}/cards/{card_id}"
            params = {
                **self.auth_params,
                "closed": "true"
            }
            response = requests.put(url, params=params, timeout=10)
            response.raise_for_status()
            logger.debug(f"Card {card_id} arquivado.")
            return True
        except Exception as e:
            logger.error(f"Erro ao arquivar card {card_id}: {e}")
            return False
            
    def find_card_by_desc_term(self, term: str) -> Optional[Dict[str, Any]]:
        """
        Busca card que tenha o termo (ex: telefone) na descrição ou nome.
        Retorna dicionário com dados do card ou None.
        """
        if not self.board_id: return None
        
        try:
            # Usa endpoint de busca do Trello
            url = f"{self.base_url}/search"
            # Busca global no texto do card (nome e desc)
            # board:{id} limita ao board específico
            query = f"board:{self.board_id} \"{term}\""
            params = {
                **self.auth_params,
                "query": query,
                "modelTypes": "cards",
                "card_fields": "id,name,desc,idList,shortUrl",
                "cards_limit": 1
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            cards = data.get("cards", [])
            
            if cards:
                return cards[0] # Retorna o objeto card completo
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar card por termo '{term}': {e}")
            return None

# Instância global
trello_client = TrelloClient()
