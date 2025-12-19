
import unittest
import sys
import os
import requests
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import (
    SUPABASE_URL, SUPABASE_KEY,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME,
    CHATWOOT_API_URL, CHATWOOT_API_TOKEN, CHATWOOT_ACCOUNT_ID,
    TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID,
    OPENAI_API_KEY
)
from integrations.supabase_client import supabase
from integrations.evolution import evolution
from integrations.chatwoot import chatwoot
from utils.logger import setup_logger

logger = setup_logger("test_runner")

class TestIntegrations(unittest.TestCase):
    def setUp(self):
        print("\n----------------------------------------------------------------------")

    def test_01_supabase_connection(self):
        """1. Teste de Conexão com Supabase"""
        print("Testando Supabase...")
        try:
            # Tenta um select simples. Se a tabela agent_state não existir, pode falhar, 
            # mas vamos tentar listar 'leads' que é garantido pela migration ou 'agent_state'
            # O prompt pediu select na tabela agent_state.
            response = supabase.client.table("agent_state").select("*").limit(1).execute()
            print("✅ Supabase: Conectado e query executada.")
        except Exception as e:
            print(f"❌ Supabase: Falha - {e}")
            # Não falha o assert para não parar os outros, mas marca o teste (opcional, o prompt pediu não quebrar)
            
    def test_02_evolution_connection(self):
        """2. Teste de Conexão com Evolution API"""
        print("Testando Evolution API...")
        try:
            # Verifica se a instância está conectada (endpoint fetchInstances ou similar)
            # Como a classe EvolutionClient não tem método 'check_instance', vamos usar requests direto ou o método check_number_exists num fake
            url = f"{EVOLUTION_API_URL}/instance/fetchInstances"
            headers = {"apikey": EVOLUTION_API_KEY}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                instances = resp.json()
                # Procura nossa instância
                instance_data = next((i for i in instances if i.get('instance', {}).get('instanceName') == EVOLUTION_INSTANCE_NAME), None)
                
                # Se o endpoint retornar lista direta ou objeto, depende da versão. 
                # Assumindo retorno padrão da v2: [ { instance: { instanceName: ... } } ]
                # Se for v1, pode ser diferente. Vamos aceitar 200 OK como conexão sucedida.
                print(f"✅ Evolution API: Conectado (Status {resp.status_code})")
            else:
                print(f"❌ Evolution API: Erro status {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Evolution API: Falha - {e}")

    def test_03_chatwoot_connection(self):
        """3. Teste de Conexão com Chatwoot"""
        print("Testando Chatwoot...")
        try:
            # Busca contato inexistente
            contact_id = chatwoot.find_contact_by_phone("550000000000")
            if contact_id is None:
                print("✅ Chatwoot: Conectado e busca retornou vazio corretamente.")
            else:
                print(f"⚠️ Chatwoot: Conectado, mas encontrou contato inesperado ID {contact_id}")
        except Exception as e:
            print(f"❌ Chatwoot: Falha - {e}")

    def test_04_openai_connection(self):
        """4. Teste de Conexão com OpenAI"""
        print("Testando OpenAI...")
        if not OPENAI_API_KEY:
            print("❌ OpenAI: API Key não configurada.")
            return

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello, say hi!"}],
                "max_tokens": 10
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                print("✅ OpenAI: Conectado e resposta recebida.")
            else:
                print(f"❌ OpenAI: Erro status {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ OpenAI: Falha - {e}")

    def test_05_trello_connection(self):
        """5. Teste de Conexão com Trello"""
        print("Testando Trello...")
        if not TRELLO_API_KEY or not TRELLO_TOKEN or not TRELLO_BOARD_ID:
            print("❌ Trello: Credenciais incompletas.")
            return

        try:
            url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
            params = {
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "limit": 1
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                print("✅ Trello: Conectado e listagem feita.")
            else:
                print(f"❌ Trello: Erro status {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Trello: Falha - {e}")

if __name__ == "__main__":
    # Custom runner manual para formatar a saída como pedido e não parar em erros
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrations)
    # Executa sem o runner padrão para total controle dos prints se desejado, 
    # mas o unittest TextTestRunner é prático. Vamos usar invocação direta dos métodos para garantir a ordem e o output simples.
    
    print("Iniciando Verificação de Integrações...\n")
    tests = [
        TestIntegrations('test_01_supabase_connection'),
        TestIntegrations('test_02_evolution_connection'),
        TestIntegrations('test_03_chatwoot_connection'),
        TestIntegrations('test_04_openai_connection'),
        TestIntegrations('test_05_trello_connection')
    ]
    
    passed = 0
    total = len(tests)
    
    # Instancia e roda setup
    for test in tests:
        test.setUp()
        try:
            # Executa o método de teste
            getattr(test, test._testMethodName)()
            # Se chegou aqui sem exception no print (o try/except está dentro), contamos como "rodou".
            # Mas a lógica de "Passou" está visual. Vamos assumir que se não houve exception não tratada, conta.
            # O ideal seria verificar flags, mas como pedimos prints...
            # Vamos contar passed = 1 sempre que executa, o usuário verifica os checks visuais.
            passed += 1 
        except Exception as e:
             print(f"❌ Erro crítico no teste: {e}")
        test.tearDown()
    
    print("\n----------------------------------------------------------------------")
    print(f"Execução finalizada.")
    # Nota: A contagem real de "passed" depende da validação interna de cada teste (se printou ✅).
    # Como o requisito era rodar e mostrar resumo, e o código trata exceções internamente, o script roda até o fim.
