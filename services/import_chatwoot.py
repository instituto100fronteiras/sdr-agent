
import openai
from typing import List, Dict, Any, Optional
from config.settings import OPENAI_API_KEY
from integrations.chatwoot import chatwoot
from integrations.supabase_client import supabase
from utils.logger import logger
from utils.validators import normalize_phone

class ChatwootImporter:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada.")
        if not chatwoot:
            raise ValueError("Integração Chatwoot não disponível.")
        
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def list_all_chatwoot_contacts(self) -> List[Dict[str, Any]]:
        """
        Busca todos os contatos do Chatwoot que têm telefone.
        Percorre todas as páginas até acabar.
        """
        all_contacts = []
        page = 1
        
        logger.info("Iniciando busca de contatos no Chatwoot...")
        
        while True:
            contacts = chatwoot.get_all_contacts(page=page)
            if not contacts:
                break
                
            for c in contacts:
                phone = c.get("phone_number")
                if phone:
                    all_contacts.append({
                        "contact_id": c.get("id"),
                        "name": c.get("name"),
                        "phone": phone,
                        "last_activity_at": c.get("last_activity_at")
                    })
            
            logger.info(f"Página {page} processada. Total acumulado: {len(all_contacts)}")
            page += 1
            
        return all_contacts

    def get_conversation_summary(self, contact_id: int) -> Dict[str, Any]:
        """
        Busca mensagens e usa IA para gerar resumo e status.
        """
        history = chatwoot.get_conversation_history(contact_id)
        
        if not history:
            return {
                "summary": "Sem histórico de mensagens.",
                "status": "new" 
            }

        # Formata para o prompt
        messages_text = ""
        for msg in history: # já está ordenado do mais recente, vamos reverter para cronológico no prompt se preciso
            role = "Agente/Nós" if msg['sender_type'] == 'User' else "Cliente"
            content = msg['content']
            messages_text += f"{role}: {content}\n"

        prompt = f"""
        Analise a seguinte conversa entre nossa empresa e um lead.
        
        Conversa:
        {messages_text}
        
        Tarefas:
        1. Gere um resumo de 2 a 3 frases sobre o contexto.
        2. Classifique o status atual em UM destes:
           - "aguardando_resposta" (última mensagem foi nossa pergunta/oferta e ele não respondeu)
           - "aguardando_followup" (última mensagem foi dele e precisa de resposta nossa)
           - "conversa_fria" (sem interação relevante recente, conversa morreu)
           - "recusou" (disse que não quer, não tem interesse)
           - "interessado" (demonstrou interesse claro, quer saber mais, agendar)

        Responda no formato exato:
        Status: [STATUS]
        Resumo: [RESUMO]
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um analista de CRM experiente."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.0
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parser simples
            status = "new"  # Default
            summary = "Erro ao gerar resumo."
            
            lines = content.split('\n')
            for line in lines:
                if line.startswith("Status:"):
                    status = line.replace("Status:", "").strip().lower()
                elif line.startswith("Resumo:"):
                    summary = line.replace("Resumo:", "").strip()
            
            # Normalização de segurança
            valid_stats = ["aguardando_resposta", "aguardando_followup", "conversa_fria", "recusou", "interessado"]
            if status not in valid_stats:
                status = "manual_review" # Fallback

            return {"status": status, "summary": summary}

        except Exception as e:
            logger.error(f"Erro na análise de IA para contato {contact_id}: {e}")
            return {"status": "manual_review", "summary": "Falha na análise automática."}

    def import_existing_leads(self):
        """
        Executa o processo completo de importação.
        """
        contacts = self.list_all_chatwoot_contacts()
        stats = {"imported": 0, "updated": 0, "ignored": 0}
        
        logger.info(f"Encontrados {len(contacts)} contatos com telefone. Iniciando análise...")
        
        for i, contact in enumerate(contacts):
            try:
                phone_raw = contact["phone"]
                phone_norm = normalize_phone(phone_raw)
                
                # Análise de IA
                analysis = self.get_conversation_summary(contact["contact_id"])
                
                # Mapeamento de status para o nosso DB
                # DB Status: new, working, contacted, follow_up_scheduled, converted, lost
                db_status = "new"
                ai_status = analysis["status"]
                
                if ai_status == "aguardando_resposta":
                    db_status = "contacted"
                elif ai_status == "aguardando_followup":
                    db_status = "working" # ou follow_up_scheduled
                elif ai_status == "conversa_fria":
                    db_status = "lost" # ou new para tentar reativar
                elif ai_status == "recusou":
                    db_status = "lost"
                elif ai_status == "interessado":
                    db_status = "working"
                
                lead_data = {
                    "name": contact["name"],
                    "phone": phone_norm,
                    "status": db_status,
                    "notes": f"[Import Bot] Status Anterior: {ai_status}. Resumo: {analysis['summary']}",
                    "chatwoot_id": contact["contact_id"]
                }
                
                # Verifica existência
                existing = supabase.get_lead_by_phone(phone_norm)
                
                if existing:
                    # Atualiza
                    old_notes = existing.get("notes", "") or ""
                    new_notes = f"{old_notes}\n\n{lead_data['notes']}"
                    supabase.update_lead(existing["id"], {
                        "notes": new_notes,
                        # Opcional: atualizar status se quisermos forçar a visão da IA
                        # "status": db_status 
                    })
                    stats["updated"] += 1
                else:
                    # Cria
                    supabase.create_lead(lead_data)
                    stats["imported"] += 1
                    
                if i > 0 and i % 5 == 0:
                    logger.info(f"Progresso: {i}/{len(contacts)}...")
                    
            except Exception as e:
                logger.error(f"Erro ao processar contato {contact}: {e}")
                stats["ignored"] += 1
                
        return stats

# Instância global
chatwoot_importer = ChatwootImporter()
