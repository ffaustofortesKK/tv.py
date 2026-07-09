import streamlit as st
import requests
import datetime

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- PAINEL DO ADMIN ---
if st.session_state.get('nome') == "ADMIN":
    st.header("⚙️ Painel do Operador")
    if st.button("🔄 Atualizar"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if solics:
        for key, info in solics.items():
            if info.get('estado') == "Pendente":
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {info.get('usuario')}")
                if col2.button("✅ Aprovar", key=f"apr_{key}"):
                    expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                    requests.patch(f"{BASE_URL}/tokens/{info['usuario']}.json", json={"expira": expira})
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Aprovado"})
                    st.rerun()
                if col3.button("❌ Recusar", key=f"rec_{key}"):
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Recusado"})
                    st.rerun()
            else:
                st.write(f"📄 {info.get('usuario')} - Status: {info.get('estado')}")
    else: st.write("Nenhuma solicitação.")

# --- ÁREA DO CLIENTE ---
else:
    if not st.session_state.autenticado:
        if 'nome_temp' not in st.session_state:
            st.subheader("🔑 Acesso ao Karaoke")
            nome = st.text_input("Seu Nome:")
            if st.button("Solicitar Acesso"):
                requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
                st.session_state.nome_temp = nome
                st.rerun()
        else:
            st.info(f"Aguardando aprovação para {st.session_state.nome_temp}...")
            # BOTÃO PARA FORÇAR A VERIFICAÇÃO
            if st.button("🔄 Verificar se fui aprovado"):
                solics = requests.get(URL_SOLICITACOES).json()
                for key, info in (solics or {}).items():
                    if info.get('usuario') == st.session_state.nome_temp:
                        if info.get('estado') == "Aprovado":
                            st.session_state.autenticado = True
                            st.session_state.nome = st.session_state.nome_temp
                            del st.session_state.nome_temp
                            st.rerun()
                        elif info.get('estado') == "Recusado":
                            st.error("Pedido recusado.")
                            if st.button("Tentar novamente"):
                                del st.session_state.nome_temp
                                st.rerun()
    else:
        # Acesso Liberado
        token_data = requests.get(f"{URL_TOKENS}/{st.session_state.nome}.json").json()
        if token_data:
            expira = datetime.datetime.fromisoformat(token_data.get('expira'))
            if datetime.datetime.now() < expira:
                st.success(f"Bem-vindo, {st.session_state.nome}!")
                resta = expira - datetime.datetime.now()
                st.metric("Tempo restante", str(resta).split('.')[0])
                if st.button("Sair"):
                    st.session_state.autenticado = False
                    st.rerun()
            else:
                st.error("Tempo esgotado!")
                st.session_state.autenticado = False
                st.rerun()
