import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"
SENHA_ADMIN = "1234" # DEFINA A SENHA DO ADMIN AQUI

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- TELA DE LOGIN GERAL ---
if not st.session_state.autenticado:
    st.subheader("🔑 Acesso ao Karaoke")
    nome = st.text_input("Seu Nome:")
    senha = st.text_input("Código (ou Senha Admin):", type="password")
    
    if st.button("Entrar"):
        # Login como ADMIN
        if nome == "ADMIN" and senha == SENHA_ADMIN:
            st.session_state.nome = "ADMIN"
            st.session_state.autenticado = True
            st.rerun()
        # Login como Cliente
        else:
            token_data = requests.get(f"{URL_TOKENS}/{nome}.json").json()
            if token_data and token_data.get('senha') == senha:
                expira = datetime.datetime.fromisoformat(token_data.get('expira'))
                if datetime.datetime.now() < expira:
                    st.session_state.nome = nome
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Código expirado!")
            else:
                st.error("Nome ou senha incorretos.")

    if st.button("Solicitar Acesso (Cliente)"):
        if nome:
            requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
            st.session_state.nome_temp = nome
            st.rerun()
        else:
            st.warning("Digite seu nome primeiro!")

    if 'nome_temp' in st.session_state:
        st.info(f"Aguardando aprovação para {st.session_state.nome_temp}...")
        if st.button("🔄 Verificar Acesso"):
            st.rerun()

# --- PAINEL DO ADMIN ---
elif st.session_state.nome == "ADMIN":
    st.header("⚙️ Painel do Operador")
    if st.button("🔄 Atualizar Lista"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if solics:
        for key, info in solics.items():
            if info.get('estado') == "Pendente":
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {info.get('usuario')}")
                if col2.button("✅ Aprovar", key=f"apr_{key}"):
                    expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                    requests.patch(f"{BASE_URL}/tokens/{info['usuario']}.json", json={"senha": "123", "expira": expira})
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Aprovado"})
                    st.rerun()
                if col3.button("❌ Recusar", key=f"rec_{key}"):
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Recusado"})
                    st.rerun()
    else: st.write("Nenhuma solicitação pendente.")
    if st.button("Sair"): st.session_state.autenticado = False; st.rerun()

# --- ÁREA DO CLIENTE ---
else:
    token_data = requests.get(f"{URL_TOKENS}/{st.session_state.nome}.json").json()
    if token_data:
        expira = datetime.datetime.fromisoformat(token_data.get('expira'))
        if datetime.datetime.now() < expira:
            st.success(f"Bem-vindo, {st.session_state.nome}!")
            resta = expira - datetime.datetime.now()
            st.metric("Tempo restante", str(resta).split('.')[0])
            if st.button("Sair"): st.session_state.autenticado = False; st.rerun()
        else:
            st.error("Tempo esgotado!"); st.session_state.autenticado = False; st.rerun()
