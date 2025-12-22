
import streamlit as st
import pandas as pd
from datetime import datetime
from dash_utils.data import get_leads_dataframe

st.title("📅 Follow-ups Pendentes")

df = get_leads_dataframe()

if df.empty:
    st.info("Sem leads.")
else:
    # Lógica de Follow-up
    # Leads que não respondem há X dias e status é contacted ou follow_up_scheduled
    
    # Filtra candidatos
    candidates = df[
        (df['status'].isin(['contacted', 'follow_up_scheduled']))
    ].copy()
    
    if candidates.empty:
        st.success("🎉 Sem follow-ups pendentes!")
    else:
        # Tabela Priorizada
        st.subheader("Prioridade Alta")
        
        st.markdown("""
        > Leads contactados recentemente que precisam de atenção.
        """)
        
        # Mostra tabela simplificada
        st.dataframe(
            candidates[["name", "company", "phone", "status", "next_contact_at"]].sort_values("next_contact_at"),
            use_container_width=True,
            hide_index=True
        )

# Alertas
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.warning("⚠️ Leads sem resposta há > 3 dias: 0") # Mock
with c2:
    st.error("🚨 Leads 'Interessados' sem ação hoje: 0") # Mock
