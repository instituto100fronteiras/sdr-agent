
import streamlit as st
from dash_utils.data import get_leads_dataframe
from dash_utils.actions import send_manual_message, update_lead_status
from components.tables import leads_table

st.title("📇 Gerenciamento de Leads")

# Carrega dados
df = get_leads_dataframe()

# Sidebar Filters
with st.sidebar:
    st.header("Filtros")
    
    if not df.empty:
        status_filter = st.multiselect("Status", df['status'].unique())
        city_filter = st.multiselect("Cidade", df['city'].unique())
        
        # Aplica filtros
        if status_filter:
            df = df[df['status'].isin(status_filter)]
        if city_filter:
            df = df[df['city'].isin(city_filter)]
            
    search_term = st.text_input("Buscar (Nome, Empresa ou Telefone)")
    if search_term and not df.empty:
        mask = (
            df['name'].str.contains(search_term, case=False, na=False) |
            df['company'].str.contains(search_term, case=False, na=False) |
            df['phone'].str.contains(search_term, case=False, na=False)
        )
        df = df[mask]

# Tabela Principal
leads_table(df)

# Ações Rápidas (Expander)
with st.expander("⚡ Ações Rápidas", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Enviar Mensagem Manual")
        target_lead_id = st.text_input("ID do Lead (copie da tabela se habilitado)")
        msg_content = st.text_area("Mensagem")
        if st.button("Enviar"):
            if target_lead_id and msg_content:
                if send_manual_message(target_lead_id, msg_content):
                    st.success("Enviada!")
                else:
                    st.error("Erro ao enviar.")
            else:
                st.warning("Preencha ID e Mensagem.")
                
    with col2:
        st.subheader("Alterar Status")
        new_status = st.selectbox("Novo Status", ["interested", "declined", "archived", "contacted"])
        if st.button("Atualizar Status"):
             if target_lead_id:
                 if update_lead_status(target_lead_id, new_status):
                     st.success("Atualizado!")
                     st.rerun()
