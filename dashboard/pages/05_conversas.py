
import streamlit as st
from dash_utils.data import get_conversations, get_lead_history
from dash_utils.actions import send_manual_message
import time

st.title("💬 Conversas em Tempo Real")

# Layout de Chat: Lista lateral, Chat principal
c_list, c_chat = st.columns([1, 2])

with c_list:
    st.subheader("Recentes")
    # Busca conversas (agrupadas por lead)
    convs = get_conversations(limit=20)
    
    selected_lead = None
    
    if not convs:
        st.info("Nenhuma conversa recente.")
    else:
        for c in convs:
            # Card clicável (usando button simulado)
            label = f"{c['name']} \n{c['last_message'][:30]}..."
            if st.button(label, key=c['lead_id'], use_container_width=True):
                st.session_state['selected_lead_id'] = c['lead_id']
                st.session_state['selected_lead_name'] = c['name']
                st.session_state['selected_lead_phone'] = c['phone']

with c_chat:
    lead_id = st.session_state.get('selected_lead_id')
    
    if lead_id:
        st.subheader(f"Chat com {st.session_state.get('selected_lead_name')} ({st.session_state.get('selected_lead_phone')})")
        
        # Histórico
        history = get_lead_history(lead_id)
        
        # Container de mensagens
        chat_container = st.container(height=400)
        
        with chat_container:
            for msg in history:
                role = "user" if msg['direction'] == 'inbound' else "assistant"
                with st.chat_message(role):
                    st.write(msg['content'])
                    st.caption(msg['sent_at'])
        
        # Input de resposta
        with st.form("chat_input"):
            new_msg = st.text_input("Digite sua mensagem...")
            send_btn = st.form_submit_button("Enviar")
            
            if send_btn and new_msg:
                if send_manual_message(lead_id, new_msg):
                    st.success("Enviada!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Falha ao enviar.")
    else:
        st.info("Selecione uma conversa ao lado.")
