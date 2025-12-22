
import streamlit as st
from dash_utils.actions import get_agent_status, toggle_agent_status
from integrations.trello import trello_client
# from integrations.evolution import evolution_client # Se tiver método de check status

st.title("⚙️ Configurações & Status")

# Status Geral
st.header("Status do Sistema")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Trello", "Conectado" if trello_client.board_id else "Desconectado")
with c2:
    st.metric("Evolution API", "Ativo") # Mock ou check real
with c3:
    st.metric("Supabase", "Ativo")

st.divider()

# Controle do Agente
st.header("Controle do Agente")

active = get_agent_status()
if active:
    st.success("O Agente está RODANDO 🟢")
    if st.button("Pausar Agente"):
        toggle_agent_status(False)
        st.rerun()
else:
    st.error("O Agente está PAUSADO 🔴")
    if st.button("Retomar Agente"):
        toggle_agent_status(True)
        st.rerun()

st.divider()

# Warm-up Config
st.header("Configuração de Warm-up")
current_day = 5 # Mock: ler do DB ou settings de persistencia
limit = 20 # Mock

col1, col2 = st.columns(2)
with col1:
    st.metric("Dia Atual", f"Dia {current_day}")
with col2:
    st.metric("Limite Hoje", f"{limit} msgs")

if st.button("Resetar Warm-up (Voltar p/ Dia 1)"):
    st.warning("Funcionalidade não implementada (Requer persistência de estado)")

st.divider()

# Logs do Sistema (Opcional)
with st.expander("Ver Logs do Sistema"):
    st.code("Logs de execução apareceriam aqui...", language="bash")
