
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def funnel_chart(df_leads):
    """
    Funil de Vendas Horizontal: New -> Contacted -> Responded -> Interested -> Converted
    """
    if df_leads.empty:
        st.info("Sem dados para funil.")
        return

    # Contagem por status
    status_order = ["new", "contacted", "responded", "interested", "converted", "declined", "archived"]
    
    counts = df_leads['status'].value_counts()
    
    # Filtra e ordena
    data = []
    for s in status_order:
        val = counts.get(s, 0)
        # Opcional: não mostrar zero ou archived
        if s != "archived": 
            data.append({"stage": s.capitalize(), "count": val})
            
    df_funnel = pd.DataFrame(data)
    
    fig = px.funnel(df_funnel, x='count', y='stage', title="Funil de Leads")
    st.plotly_chart(fig, use_container_width=True)

def hourly_response_chart(df_logs):
    """
    Gráfico de linha: Respostas por hora do dia.
    """
    if df_logs.empty:
        st.info("Sem logs para gráfico horário.")
        return
        
    # Filtra inbound
    df_in = df_logs[df_logs['direction'] == 'inbound'].copy()
    if df_in.empty:
        st.info("Sem respostas registradas para gráfico.")
        return
        
    df_in['hour'] = df_in['sent_at'].dt.hour
    hourly = df_in['hour'].value_counts().sort_index()
    
    # Cria DF com todas as horas 0-23
    df_chart = pd.DataFrame({'hour': range(24)})
    df_chart['count'] = df_chart['hour'].map(hourly).fillna(0)
    
    fig = px.line(df_chart, x='hour', y='count', title="Melhor Horário de Resposta", markers=True)
    st.plotly_chart(fig, use_container_width=True)

def daily_history_chart(df_logs):
    """
    Histórico diário de mensagens (Enviadas vs Recebidas)
    """
    if df_logs.empty: return
    
    df_logs['date'] = df_logs['sent_at'].dt.date
    daily = df_logs.groupby(['date', 'direction']).size().reset_index(name='count')
    
    fig = px.bar(daily, x='date', y='count', color='direction', title="Histórico Diário de Mensagens",
                 color_discrete_map={"outbound": "#1E40AF", "inbound": "#F97316"})
    st.plotly_chart(fig, use_container_width=True)
