
import streamlit as st
from services.google_maps_search import google_maps_search
import pandas as pd

st.title("🔍 Buscar Novos Leads (Google Maps)")

with st.form("search_form"):
    c1, c2 = st.columns(2)
    with c1:
        query = st.text_input("Termo de Busca", placeholder="Ex: Arquitetos, Clínicas, Advogados")
    with c2:
        city = st.selectbox("Cidade", ["Foz do Iguaçu, PR", "Ciudad del Este, Paraguay", "Puerto Iguazú, Argentina"])
        
    limit = st.slider("Limite de Resultados", 5, 20, 10)
    # validate_whatsapp = st.checkbox("Validar WhatsApp (Mais lento)", value=True)
    
    submitted = st.form_submit_button("🚀 Iniciar Busca")

if submitted and query:
    with st.status("Processando busca...", expanded=True) as status:
        st.write("Conectando SerpAPI...")
        
        # Executa busca (usando o service existente)
        # O service retorna lista de dicts
        try:
            results = google_maps_search.search_leads(query, city, limit=limit) # validate_whatsapp removido pois não é argumento do search_leads direto no código atual, ele faz interno se configurado. Mas o service.py tem parametro?
            # Analisando google_maps_search.py: search_leads(query, location, limit)
            
            status.update(label="Busca concluída!", state="complete", expanded=False)
            
            if results:
                st.success(f"{len(results)} leads encontrados!")
                
                # Mostra tabela
                df_res = pd.DataFrame(results)
                st.dataframe(df_res[["title", "phone", "address"]], use_container_width=True)
                
                # Botão para salvar (o service já salva? Verificar.)
                # O service search_leads do google_maps_search.py já chama _save_leads!
                st.info("Os leads válidos foram salvos automaticamente no banco de dados.")
                
            else:
                st.warning("Nenhum lead encontrado com telefone válido.")
                
        except Exception as e:
            st.error(f"Erro na busca: {e}")
            status.update(label="Falha", state="error")
