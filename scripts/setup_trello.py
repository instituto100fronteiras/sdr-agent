
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.trello_service import trello_service
from integrations.trello import trello_client
from config.settings import TRELLO_BOARD_ID

def main():
    print("=== Setup Trello Integration ===")
    
    # 1. Test Connection
    print("\n1. Testando Conexão...")
    if trello_client.test_connection():
        print("✅ Conexão OK!")
    else:
        print("❌ Falha na conexão. Verifique TRELLO_API_KEY e TRELLO_TOKEN.")
        return

    # 2. Check Board
    if not TRELLO_BOARD_ID:
        print("\n❌ TRELLO_BOARD_ID não configurado no .env")
        print("Liste seus boards (via API ou navegador) e configure o ID.")
        return
        
    print(f"\n2. Verificando Board {TRELLO_BOARD_ID}...")
    lists = trello_client.get_board_lists()
    
    if not lists:
        print("⚠️  Nenhuma lista encontrada ou erro ao acessar board.")
        return

    print(f"\n✅ Total de listas encontradas: {len(lists)}")
    print("-" * 40)
    print(f"{'ID':<30} | {'NOME'}")
    print("-" * 40)
    
    current_lists = {l['name']: l['id'] for l in lists}
    
    for l in lists:
        print(f"{l['id']:<30} | {l['name']}")
    print("-" * 40)
    
    # 3. Suggest Configuration
    required_lists = {
        "Contato Frio": "TRELLO_LIST_COLD",
        "Conexão": "TRELLO_LIST_CONNECTION",
        "Interessados": "TRELLO_LIST_INTERESTED",
        "Arquivados": "TRELLO_LIST_ARCHIVED"
    }
    
    print("\n=== Configuração Sugerida para .env ===")
    
    missing_lists = []
    
    for list_name, env_var in required_lists.items():
        list_id = current_lists.get(list_name)
        
        if list_id:
            print(f"{env_var}={list_id}")
        else:
            print(f"# {env_var}=??? (Lista '{list_name}' não encontrada)")
            missing_lists.append(list_name)
            
    # 4. Create Missing Lists?
    if missing_lists:
        print(f"\n⚠️  Listas faltando: {', '.join(missing_lists)}")
        # Implementar criação automática se desejar?
        # Na integração simples Trello.py não fiz create_list, então só aviso.
        print("Crie essas listas no Trello e rode o script novamente para pegar os IDs.")

if __name__ == "__main__":
    main()
