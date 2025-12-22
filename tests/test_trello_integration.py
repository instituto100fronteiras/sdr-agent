
import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from integrations.trello import TrelloClient

class TestTrelloIntegration(unittest.TestCase):
    
    def setUp(self):
        self.trello = TrelloClient()
        self.trello.api_key = "fake_key"
        self.trello.token = "fake_token"
        self.trello.board_id = "fake_board"

    @patch('requests.get')
    def test_connection_success(self, mock_get):
        # Mock Response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"username": "sdr_agent"}
        mock_get.return_value = mock_resp
        
        self.assertTrue(self.trello.test_connection())

    @patch('requests.post')
    def test_create_card(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "card_123"}
        mock_post.return_value = mock_resp
        
        card_id = self.trello.create_card("list_1", "Test Card")
        self.assertEqual(card_id, "card_123")
        
    @patch('requests.put')
    def test_move_card(self, mock_put):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_put.return_value = mock_resp
        
        success = self.trello.move_card("card_123", "list_2")
        self.assertTrue(success)

    @patch('requests.get')
    def test_find_card_by_phone(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        # O retorno agora é uma lista de cards (dicionários)
        mock_resp.json.return_value = {"cards": [{"id": "card_existing", "name": "Test", "desc": "Phone 123", "idList": "list_1"}]}
        mock_get.return_value = mock_resp
        
        card_data = self.trello.find_card_by_desc_term("123")
        self.assertEqual(card_data["id"], "card_existing")
        self.assertEqual(card_data["idList"], "list_1")

if __name__ == '__main__':
    unittest.main()
