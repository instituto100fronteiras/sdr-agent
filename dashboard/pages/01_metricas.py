
import streamlit as st
import pandas as pd
import plotly.express as px
from dash_utils.data import get_leads_dataframe, get_message_logs_dataframe
from components.charts import hourly_response_chart, daily_history_chart

st.title("📈 Métricas Detalhadas")

df_leads = get_leads_dataframe()
df_logs = get_message_logs_dataframe()

tab1, tab2, tab3 = st.tabs(["Geral", "Por Setor e Cidade", "Temporal"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição de Status")
        if not df_leads.empty:
            fig_status = px.pie(df_leads, names='status', title="Status dos Leads", hole=0.4)
            st.plotly_chart(fig_status, use_container_width=True)
            
    with col2:
        st.subheader("Taxa de Conversão Estimada")
        if not df_leads.empty:
            total = len(df_leads)
            interested = len(df_leads[df_leads['status'] == 'interested'])
            rate = (interested / total * 100) if total > 0 else 0
            st.metric("Taxa de Interesse Global", f"{rate:.1f}%")

with tab2:
    if not df_leads.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Por Cidade")
            city_counts = df_leads['city'].value_counts().reset_index()
            fig_city = px.bar(city_counts, x='city', y='count', title="Leads por Cidade")
            st.plotly_chart(fig_city, use_container_width=True)
            
        with c2:
            st.subheader("Por Setor")
            if 'sector' in df_leads.columns:
                sector_counts = df_leads['sector'].value_counts().reset_index()
                fig_sector = px.bar(sector_counts, x='sector', y='count', title="Leads por Setor")
                st.plotly_chart(fig_sector, use_container_width=True)
            else:
                st.info("Coluna 'sector' não encontrada.")

with tab3:
    st.subheader("Análise Temporal")
    hourly_response_chart(df_logs)
    daily_history_chart(df_logs)
