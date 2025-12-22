
import streamlit as st
import pandas as pd
from dash_utils.data import get_kpis_today, get_leads_dataframe
from dash_utils.actions import toggle_agent_status, get_agent_status
from components.cards import kpi_grid
from components.charts import funnel_chart

# Configuração da Página
st.set_page_config(
    page_title="SDR Agent - 100fronteiras",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Customizado (Tema Escuro + Cores da Marca)
st.markdown("""
<style>
    /* Cores: Azul (#1E40AF) e Laranja (#F97316) */
    .stMetric {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .stButton button {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("🤖 SDR Agent - 100fronteiras")
        st.markdown("*Monitoramento e Controle em Tempo Real*")
    
    with c2:
        is_active = get_agent_status()
        status_label = "🟢 RODANDO" if is_active else "🔴 PAUSADO"
        st.metric("Status do Agente", status_label)
        
        if st.button("Ligar/Desligar Agente"):
            toggle_agent_status(not is_active)
            st.rerun()

    st.divider()

    # KPIs
    st.subheader("📊 Performance Hoje")
    kpis = get_kpis_today()
    kpi_grid(kpis)

    st.divider()

    # Visão Geral (Funil + Tabela Recente)
    c_funnel, c_recent = st.columns([2, 3])

    with c_funnel:
        st.subheader("Funil de Leads")
        df_leads = get_leads_dataframe()
        funnel_chart(df_leads)

    with c_recent:
        st.subheader("Últimos Leads Cadastrados")
        if not df_leads.empty:
            recent = df_leads.sort_values("created_at", ascending=False).head(10)
            st.dataframe(
                recent[["name", "company", "phone", "status", "created_at"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum lead encontrado.")

if __name__ == "__main__":
    main()
