
import streamlit as st
import pandas as pd

def leads_table(df_leads):
    """
    Renderiza tabela de leads interativa.
    """
    if df_leads.empty:
        st.info("Nenhum lead encontrado.")
        return

    # Formata colunas
    st.dataframe(
        df_leads,
        use_container_width=True,
        column_config={
            "phone": "Telefone",
            "name": "Nome",
            "company": "Empresa",
            "city": "Cidade",
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=[
                    "new", "contacted", "responded", 
                    "interested", "converted", "declined", "archived"
                ],
                required=True
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Criado em",
                format="DD/MM/YYYY HH:mm"
            ),
            "next_contact_at": st.column_config.DatetimeColumn(
                "Próximo Contato",
                format="DD/MM/YYYY HH:mm"
            ),
            "linkedin": st.column_config.LinkColumn("LinkedIn"),
            "website": st.column_config.LinkColumn("Website"),
        },
        hide_index=True
    )
