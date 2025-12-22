
import os
import pandas as pd
from integrations.supabase_client import supabase
from datetime import datetime, timedelta

def get_leads_dataframe():
    """Busca todos os leads e retorna como DataFrame."""
    try:
        if not supabase: return pd.DataFrame()
        
        # Busca leads (assumindo limite razoável ou paginação futura)
        response = supabase.client.table("leads").select("*").execute()
        data = response.data
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Converte datas
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        if 'next_contact_at' in df.columns:
            df['next_contact_at'] = pd.to_datetime(df['next_contact_at'])
            
        return df
    except Exception as e:
        print(f"Erro ao buscar leads: {e}")
        return pd.DataFrame()

def get_message_logs_dataframe():
    """Busca logs de mensagens e retorna DataFrame."""
    try:
        if not supabase: return pd.DataFrame()
        
        # Pegar logs dos últimos 30 dias para performance
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        response = supabase.client.table("messages")\
            .select("*")\
            .gte("sent_at", thirty_days_ago)\
            .execute()
            
        data = response.data
        if not data: return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['sent_at'] = pd.to_datetime(df['sent_at'])
        return df
        
    except Exception as e:
        print(f"Erro ao buscar logs: {e}")
        return pd.DataFrame()

def get_kpis_today():
    """Retorna KPIs do dia (Sent, Responded, Rate, New Leads)."""
    try:
        if not supabase: return {}
        
        today = datetime.now().date()
        today_iso = today.isoformat()
        
        # Leads criados hoje
        new_leads = supabase.client.table("leads")\
            .select("id", count="exact")\
            .gte("created_at", today_iso)\
            .execute().count

        # Mensagens enviadas hoje (outbound)
        sent = supabase.client.table("message_logs")\
            .select("id", count="exact")\
            .gte("sent_at", today_iso)\
            .eq("direction", "outbound")\
            .execute().count
            
        # Respostas recebidas hoje (inbound)
        # Nota: Idealmente contar distinct lead_id ou conversas
        responded = supabase.client.table("message_logs")\
            .select("id", count="exact")\
            .gte("sent_at", today_iso)\
            .eq("direction", "inbound")\
            .execute().count
            
        rate = (responded / sent * 100) if sent > 0 else 0
        
        return {
            "new_leads": new_leads or 0,
            "sent_today": sent or 0,
            "responded_today": responded or 0,
            "response_rate": round(rate, 1)
        }
        
    except Exception as e:
        print(f"Erro ao calcular KPIs: {e}")
        return {"new_leads": 0, "sent_today": 0, "responded_today": 0, "response_rate": 0}

def get_conversations(limit=20):
    """Retorna lista de conversas recentes (leads com mensagens)."""
    # Simplificação: busca leads que tiveram mensagem recente
    try:
        # Busca últimos logs
        response = supabase.client.table("message_logs")\
            .select("lead_id, content, sent_at, direction")\
            .order("sent_at", desc=True)\
            .limit(limit)\
            .execute()
            
        data = response.data
        if not data: return []
        
        # Enriquece com dados do lead
        # Agrupa por lead_id para mostrar só a última
        conversations = []
        seen_leads = set()
        
        for msg in data:
            lid = msg['lead_id']
            if lid in seen_leads: continue
            
            seen_leads.add(lid)
            
            # Busca nome do lead
            lead_resp = supabase.client.table("leads").select("name, phone, company").eq("id", lid).single().execute()
            lead = lead_resp.data if lead_resp.data else {"name": "Desconhecido", "phone": "N/A"}
            
            conversations.append({
                "lead_id": lid,
                "name": lead.get('name'),
                "company": lead.get('company'),
                "phone": lead.get('phone'),
                "last_message": msg['content'],
                "time": msg['sent_at'],
                "direction": msg['direction']
            })
            
        return conversations
        
    except Exception as e:
        print(f"Erro ao buscar conversas: {e}")
        return []

def get_lead_history(lead_id: str):
    """Busca histórico completo de mensagens de um lead."""
    try:
        response = supabase.client.table("message_logs")\
            .select("*")\
            .eq("lead_id", lead_id)\
            .order("sent_at", desc=False)\
            .execute()
        return response.data
    except Exception as e:
        return []
