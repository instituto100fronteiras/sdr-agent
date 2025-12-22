import requests
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME

def test_endpoints():
    print(f"URL: {EVOLUTION_API_URL}")
    print(f"Instance: {EVOLUTION_INSTANCE_NAME}")
    
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    # Check Connection State
    print("\nChecking Connection State...")
    state_url = f"{EVOLUTION_API_URL}/instance/connectionState/{EVOLUTION_INSTANCE_NAME}"
    try:
        response = requests.get(state_url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test number (dummy or real format)
    number = "5545999881234" 
    
    endpoints = [
        {
            "name": "v2_whatsappNumbers",
            "method": "POST",
            "url": f"{EVOLUTION_API_URL}/chat/whatsappNumbers/{EVOLUTION_INSTANCE_NAME}",
            "json": {"numbers": [number]}
        },
        {
            "name": "v1_checkIsWhatsapp",
            "method": "POST",
            "url": f"{EVOLUTION_API_URL}/chat/checkIsWhatsapp/{EVOLUTION_INSTANCE_NAME}",
            "json": {"numbers": [number]}
        },
        {
            "name": "v1_checkNumberStatus_GET",
            "method": "GET",
            "url": f"{EVOLUTION_API_URL}/chat/checkNumberStatus/{EVOLUTION_INSTANCE_NAME}/{number}",
            "json": None
        }
    ]
    
    for ep in endpoints:
        print(f"\nTesting {ep['name']}...")
        print(f"URL: {ep['url']}")
        try:
            if ep['method'] == "POST":
                response = requests.post(ep['url'], headers=headers, json=ep['json'], timeout=10)
            else:
                response = requests.get(ep['url'], headers=headers, timeout=10)
                
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}") # Truncate for readability
            
            if response.status_code == 200:
                print(f"SUCCESS: {ep['name']} looks correct!")
                # Analyze response structure
                try:
                    data = response.json()
                    print(f"JSON structure keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
                except:
                    pass
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_endpoints()
