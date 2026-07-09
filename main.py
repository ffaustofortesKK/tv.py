import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"
SENHA_ADMIN = "1234"

# --- FUNÇÕES AUXILIARES ---
def get_data(url):
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else {}
    except: return {}

# --- LÓGICA DO PAINEL ADMIN ---
def painel_admin():
    st.header("⚙️ Painel do Operador")
    if st.sidebar.button("🔄 Atualizar Dados"): st.rerun()
    
    solics = get_data(URL_SOLICITACOES)
    
    st.write("### Pedidos Pendentes")
    if solics and isinstance(solics, dict):
        for id_fire, info in solics.items():
            if info.get('estado') == "Pendente":
                user = info.get('usuario')
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"👤 **{user}**")
                
                if c2.button("✅ Aprovar", key=f"apr_{id_fire}"):
                    # Define validade de 3 horas
                    expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                    # Cria token e atualiza pedido
                    requests.put(f"{URL_TOKENS}/{user}.json", json={"expira": expira})
                    requests.patch(f"{URL_SOLICITACOES}/{id_fire}.json", json={"estado": "Aprovado"})
                    st.rerun()
                
                if c3.button("❌ Recusar", key=f"rec_{id_fire}"):
                    requests.patch(f"{URL_SOLICITACOES}/{id_fire}.json", json={"estado": "Recusado"})
                    st.rerun()
    else:
        st.info("Nenhum pedido pendente.")
    
    if st.button("Sair"): st.session_state.clear(); st.rerun()

# --- LÓGICA DO CLIENTE ---
def painel_cliente():
    st.subheader("🔑 Acesso ao Karaoke")
    nome = st.text_input("Seu Nome:")
    senha = st.text_input("Senha/Código:", type="password")
    
    c1, c2 = st.columns(2)
    if c1.button("Entrar"):
        if nome == "ADMIN" and senha == SENHA_ADMIN:
            st.session_state.nome = "ADMIN"
            st.session_state.autenticado = True
            st.rerun()
        else:
            token = get_data(f"{URL_TOKENS}/{nome}.json")
            if token and 'expira' in token:
                expira = datetime.datetime.fromisoformat(token['expira'])
                if datetime.datetime.now() < expira:
                    st.session_state.nome = nome
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Acesso expirado!")
            else: st.error("Acesso negado ou aguardando aprovação.")

    if c2.button("Solicitar Acesso"):
        if nome:
            requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
            st.success("Pedido enviado! Aguarde o Admin.")
        else: st.warning("Digite o nome.")

# --- EXECUÇÃO PRINCIPAL ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if st.session_state.autenticado:
    if st.session_state.nome == "ADMIN":
        painel_admin()
    else:
        st.success(f"Bem-vindo, {st.session_state.nome}!")
        token = get_data(f"{URL_TOKENS}/{st.session_state.nome}.json")
        if token and 'expira' in token:
            expira = datetime.datetime.fromisoformat(token['expira'])
            resta = expira - datetime.datetime.now()
            if resta.total_seconds() > 0:
                st.metric("⏱️ Tempo Restante", str(resta).split('.')[0])
            else:
                st.error("Tempo esgotado!"); st.session_state.autenticado = False
        if st.button("Sair"): st.session_state.clear(); st.rerun()
else:
    painel_cliente()
