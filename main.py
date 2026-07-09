import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"
SENHA_ADMIN = "1234"

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- LÓGICA DO ADMIN ---
def painel_admin():
    st.header("⚙️ Painel do Operador")
    if st.button("🔄 Atualizar Lista"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if solics:
        st.write("### Pedidos Pendentes")
        for id_firebase, info in solics.items():
            if info.get('estado') == "Pendente":
                usuario = info.get('usuario')
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 {usuario}")
                
                # Botões com chave única baseada no ID do Firebase
                if c2.button("✅ Aprovar", key=f"apr_{id_firebase}"):
                    expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                    requests.patch(f"{URL_TOKENS}/{usuario}.json", json={"expira": expira})
                    requests.patch(f"{URL_SOLICITACOES}/{id_firebase}.json", json={"estado": "Aprovado"})
                    st.rerun()
                    
                if c3.button("❌ Recusar", key=f"rec_{id_firebase}"):
                    requests.patch(f"{URL_SOLICITACOES}/{id_firebase}.json", json={"estado": "Recusado"})
                    st.rerun()
    else: st.write("Nenhuma solicitação pendente.")
    
    if st.button("Sair do Painel"): st.session_state.autenticado = False; st.rerun()

# --- LÓGICA DO CLIENTE ---
def painel_cliente():
    if not st.session_state.autenticado:
        st.subheader("🔑 Acesso ao Karaoke")
        nome = st.text_input("Seu Nome:")
        senha = st.text_input("Senha (ou Código Admin):", type="password")
        
        col1, col2 = st.columns(2)
        if col1.button("Entrar"):
            # Login Admin
            if nome == "ADMIN" and senha == SENHA_ADMIN:
                st.session_state.nome = "ADMIN"
                st.session_state.autenticado = True
                st.rerun()
            # Login Cliente
            else:
                token_data = requests.get(f"{URL_TOKENS}/{nome}.json").json()
                if token_data and 'expira' in token_data:
                    expira = datetime.datetime.fromisoformat(token_data.get('expira'))
                    if datetime.datetime.now() < expira:
                        st.session_state.nome = nome
                        st.session_state.autenticado = True
                        st.rerun()
                    else: st.error("Acesso expirado!")
                else: st.error("Utilizador não encontrado ou não aprovado.")

        if col2.button("Solicitar Acesso"):
            if nome:
                requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
                st.info("Pedido enviado! Aguarde aprovação.")
            else: st.warning("Digite seu nome!")
    else:
        # Área de Karaoke
        st.success(f"Bem-vindo, {st.session_state.nome}!")
        token_data = requests.get(f"{URL_TOKENS}/{st.session_state.nome}.json").json()
        expira = datetime.datetime.fromisoformat(token_data.get('expira'))
        
        resta = expira - datetime.datetime.now()
        if resta.total_seconds() > 0:
            st.metric("⏱️ Tempo Restante", str(resta).split('.')[0])
        else:
            st.error("Tempo esgotado!"); st.session_state.autenticado = False; st.rerun()
        
        if st.button("Sair"): st.session_state.autenticado = False; st.rerun()

# --- EXECUÇÃO ---
if st.session_state.get('nome') == "ADMIN": painel_admin()
else: painel_cliente()
