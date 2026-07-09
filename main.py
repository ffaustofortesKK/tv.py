import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"

# --- INTERFACE ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- PAINEL DO ADMIN ---
if st.session_state.get('nome') == "ADMIN":
    st.header("⚙️ Painel de Aprovação")
    if st.button("🔄 Refresh de Pedidos"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if solics:
        for key, info in solics.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            col1.write(info['usuario'])
            
            if col2.button("✅ Aprovar", key=f"apr_{key}"):
                # Gera token de 3h e aprova
                expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                requests.patch(f"{BASE_URL}/tokens/{info['usuario']}.json", 
                               json={"senha": "123", "expira": expira})
                requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Aprovado"})
                st.rerun()
                
            if col3.button("❌ Recusar", key=f"rec_{key}"):
                requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Recusado"})
                st.rerun()
    else: st.write("Nenhum pedido pendente.")

# --- ÁREA DO CLIENTE ---
elif not st.session_state.autenticado:
    st.subheader("🔑 Acesso ao Karaoke")
    nome = st.text_input("Seu Nome:")
    if st.button("Solicitar Acesso"):
        requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
        st.session_state.nome_temp = nome
        st.session_state.aguardando = True

    if st.session_state.get('aguardando'):
        st.info(f"Olá {st.session_state.nome_temp}, aguardando aprovação...")
        # Lógica de espera (Refresh automático a cada 5s)
        import time; time.sleep(2)
        solics = requests.get(URL_SOLICITACOES).json()
        for key, info in (solics or {}).items():
            if info['usuario'] == st.session_state.nome_temp:
                if info.get('estado') == "Aprovado":
                    st.session_state.autenticado = True
                    st.session_state.nome = st.session_state.nome_temp
                    st.rerun()
                elif info.get('estado') == "Recusado":
                    st.error("Seu pedido foi recusado.")
                    st.session_state.aguardando = False

else:
    st.success(f"Bem-vindo, {st.session_state.nome}! Acesso liberado.")
