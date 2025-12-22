
import streamlit as st

def metric_card(label, value, delta=None, prefix="", suffix=""):
    """
    Exibe um card de métrica estilizado.
    """
    st.metric(
        label=label,
        value=f"{prefix}{value}{suffix}",
        delta=delta
    )

def kpi_grid(kpis):
    """
    Renderiza grid de KPIs principais.
    Esperado: dict com new_leads, sent_today, responded_today, response_rate
    """
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        metric_card("Mensagens Hoje", kpis.get("sent_today", 0))
    with c2:
        metric_card("Respostas Hoje", kpis.get("responded_today", 0))
    with c3:
        metric_card("Taxa Resposta", kpis.get("response_rate", 0), suffix="%")
    with c4:
        metric_card("Leads Novos", kpis.get("new_leads", 0))
