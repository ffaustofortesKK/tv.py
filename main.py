import streamlit as st
import requests
import datetime
import time

# --- CONFIGURAÇÕES ---
URL_BASE = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_TOKENS = f"{URL_BASE}/tokens.json"
URL_PEDIDOS = f"{URL_BASE}/pedidos.json"
URL_SOLICITACOES = f"{URL_BASE}/solicitacoes.json"

# --- FUNÇÕES ---
def validar_usuario(nome):
    # Verifica se o usuário tem token válido no Firebase
    resp = requests.get(URL_TOKENS).json()
    if resp and nome in resp:
        expira = datetime.datetime.fromisoformat(resp[nome].get('expira'))
        return datetime.datetime.now() < expira
    return False

# --- INTERFACE ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.subheader("🔑 Acesso ao Karaoke")
    nome = st.text_input("Nome de utilizador:")
    
    if st.button("Solicitar Acesso"):
        if nome:
            requests.put(f"{URL_SOLICITACOES}/{nome}.json", json={"status": "pendente", "timestamp": str(datetime.datetime.now())})
            st.info("Pedido enviado! Aguarde a aprovação do Administrador...")
        else:
            st.warning("Insira o seu nome.")

    # Loop de verificação (o cliente fica aqui até ser aprovado)
    if st.button("Verificar Aprovação"):
        if validar_usuario(nome):
            st.session_state.nome = nome
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Ainda não aprovado ou acesso expirado.")

else:
    # --- PAINEL DO OPERADOR ---
    if st.session_state.nome == "ADMIN":
        st.header("⚙️ Painel do Administrador")
        if st.button("🔄 Refresh"): st.rerun()
        
        solics = requests.get(URL_SOLICITACOES).json()
        if solics:
            for user, dados in solics.items():
                col1, col2, col3 = st.columns([2,1,1])
                col1.write(f"Utilizador: **{user}**")
                if col2.button("Aprovar", key=f"ap_{user}"):
                    # Gera senha de 3h
                    expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                    requests.put(f"{URL_TOKENS}/{user}.json", json={"senha": "123", "expira": expira})
                    requests.delete(f"{URL_SOLICITACOES}/{user}.json")
                    st.rerun()
                if col3.button("Recusar", key=f"re_{user}"):
                    requests.put(f"{URL_SOLICITACOES}/{user}.json", json={"status": "recusado"})
                    st.rerun()
        else:
            st.write("Nenhum pedido pendente.")
    else:
        st.write(f"Bem-vindo {st.session_state.nome}! Pode começar a cantar.")
