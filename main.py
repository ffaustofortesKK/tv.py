import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
URL_FIREBASE_TOKENS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/tokens.json"
URL_FIREBASE_PEDIDOS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos.json"
URL_FIREBASE_SOLICITACOES = "https://grupoffkaraoke-default-rtdb.firebaseio.com/solicitacoes.json"

def validar_login(nome, senha):
    if nome == "ADMIN": return True
    try:
        resp = requests.get(f"{URL_FIREBASE_TOKENS}/{nome}.json")
        dados = resp.json()
        if dados and dados.get('senha') == senha:
            expira = datetime.datetime.fromisoformat(dados.get('expira'))
            return datetime.datetime.now() < expira
        return False
    except: return False

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    nome = st.text_input("Nome:")
    senha = st.text_input("Código:", type="password")
    if st.button("Entrar"):
        if validar_login(nome, senha):
            st.session_state.nome = nome
            st.session_state.autenticado = True
            st.rerun()
    if st.button("Solicitar Acesso"):
        requests.post(URL_FIREBASE_SOLICITACOES, json={"usuario": nome, "timestamp": str(datetime.datetime.now())})
        st.success("Pedido enviado!")
else:
    if st.session_state.nome == "ADMIN":
        st.header("⚙️ Painel do Operador")
        if st.button("🔄 Refresh (Atualizar Pedidos)"): st.rerun()
        
        # Leitura de Solicitações
        solics = requests.get(URL_FIREBASE_SOLICITACOES).json()
        st.subheader("📩 Solicitações")
        st.write(solics if solics else "Nenhuma.")
        
        # Campos de Aprovação
        st.subheader("✅ Gerar Código de Acesso")
        user_aprov = st.text_input("Nome do Usuário:")
        code_aprov = st.text_input("Código a atribuir:")
        if st.button("Aprovar e Gerar Token"):
            expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
            payload = {"senha": code_aprov, "expira": expira}
            requests.put(f"{URL_FIREBASE_TOKENS}/{user_aprov}.json", json=payload)
            st.success(f"Acesso liberado para {user_aprov}!")
            
        if st.button("Limpar Tudo"):
            requests.delete(URL_FIREBASE_SOLICITACOES)
            st.rerun()
    else:
        st.title(f"Bem-vindo, {st.session_state.nome}!")
        st.write("Sistema de Karaoke Online Ativo.")
