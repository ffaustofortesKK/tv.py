import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
URL_FIREBASE_TOKENS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/tokens.json"
URL_FIREBASE_PEDIDOS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos.json"
URL_FIREBASE_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"
URL_FIREBASE_SOLICITACOES = "https://grupoffkaraoke-default-rtdb.firebaseio.com/solicitacoes.json"
URL_SOM_PALMAS = "https://www.soundjay.com/misc/sounds/applause-2.mp3"

# --- FUNÇÃO DE VALIDAÇÃO ---
def validar_senha_no_firebase(nome, senha_input):
    try:
        resp = requests.get(URL_FIREBASE_TOKENS)
        dados = resp.json()
        if dados and nome in dados:
            token_data = dados[nome]
            if token_data.get('senha') == senha_input:
                expira = datetime.datetime.fromisoformat(token_data.get('expira'))
                if datetime.datetime.now() < expira:
                    return True
        return False
    except: 
        return False

# --- LÓGICA DE ESTADO ---
if 'autenticado' not in st.session_state: 
    st.session_state.autenticado = False

# --- INTERFACE DE LOGIN ---
if not st.session_state.autenticado:
    st.subheader("🔑 Acesso ao Karaoke")
    nome_usuario = st.text_input("Nome:")
    senha_usuario = st.text_input("Código de Acesso:", type="password")
    
    if st.button("Entrar"):
        if validar_senha_no_firebase(nome_usuario, senha_usuario):
            st.session_state.nome = nome_usuario
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Código inválido ou expirado!")
            if st.button("Solicitar Acesso"):
                requests.post(URL_FIREBASE_SOLICITACOES, 
                              json={"usuario": nome_usuario, "timestamp": str(datetime.datetime.now())})
                st.info("Pedido enviado! Aguarde o operador gerar o seu código.")
else:
    # --- APP DE KARAOKE (APÓS LOGIN) ---
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    busca = st.text_input("🔍 Pesquisar Música no catálogo:")
    escolha = None
    
    if busca:
        try:
            resp = requests.get(URL_FIREBASE_CATALOGO, timeout=5)
            dados = resp.json()
            cat = list(dados.keys()) if isinstance(dados, dict) else dados
            resultados = [m for m in cat if busca.lower() in m.lower()]
            escolha = st.selectbox("Selecione:", resultados)
        except: 
            st.error("Erro ao carregar catálogo.")

    if escolha:
        st.write(f"Música: **{escolha}**")
        if st.button("Confirmar Pedido"):
            requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": escolha})
            st.audio(URL_SOM_PALMAS, autoplay=True)
            st.success("Pedido enviado!")
            st.rerun()

    st.divider()
    st.subheader("Manual")
    pedido_manual = st.text_input("Não achou? Digite o nome da música:")
    if st.button("Confirmar Pedido Manual"):
        if pedido_manual:
            requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": pedido_manual, "status": "manual"})
            st.warning("O seu pedido foi enviado, mas verifique se a música existe no sistema.")
            st.balloons()
