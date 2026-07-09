import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- PAINEL DO ADMIN ---
if st.session_state.get('nome') == "ADMIN":
    st.header("⚙️ Painel do Operador")
    if st.button("🔄 Atualizar Lista"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if solics:
        st.write("### Pedidos Pendentes")
        for key, info in solics.items():
            if info.get('estado') == "Pendente":
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {info.get('usuario')}")
                
                # Botões de ação
                if col2.button("✅ Aprovar", key=f"apr_{key}"):
                    # Define expiração para 3 horas a partir de agora
                    expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                    requests.patch(f"{URL_TOKENS}/{info['usuario']}.json", json={"expira": expira})
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Aprovado"})
                    st.rerun()
                if col3.button("❌ Recusar", key=f"rec_{key}"):
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Recusado"})
                    st.rerun()
    else: st.write("Nenhuma solicitação pendente.")
    
    if st.button("Sair do Painel"): st.session_state.autenticado = False; st.rerun()

# --- ÁREA DO CLIENTE ---
else:
    if not st.session_state.autenticado:
        st.subheader("🔑 Acesso ao Karaoke")
        nome = st.text_input("Seu Nome:")
        senha = st.text_input("Senha (se já aprovado):", type="password")
        
        col1, col2 = st.columns(2)
        if col1.button("Entrar"):
            if nome == "ADMIN" and senha == "1234":
                st.session_state.nome = "ADMIN"
                st.session_state.autenticado = True
                st.rerun()
            else:
                # Verifica aprovação
                token_data = requests.get(f"{URL_TOKENS}/{nome}.json").json()
                if token_data:
                    expira = datetime.datetime.fromisoformat(token_data.get('expira'))
                    if datetime.datetime.now() < expira:
                        st.session_state.nome = nome
                        st.session_state.autenticado = True
                        st.rerun()
                    else: st.error("Acesso expirado!")
                else: st.error("Utilizador não aprovado.")

        if col2.button("Solicitar Acesso"):
            if nome:
                requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
                st.info("Pedido enviado! Aguarde aprovação e atualize a página.")
            else: st.warning("Digite seu nome!")
    
    else:
        # --- ACESSO LIBERADO (CONTAGEM) ---
        st.success(f"Bem-vindo, {st.session_state.nome}!")
        token_data = requests.get(f"{URL_TOKENS}/{st.session_state.nome}.json").json()
        expira = datetime.datetime.fromisoformat(token_data.get('expira'))
        
        tempo_restante = expira - datetime.datetime.now()
        if tempo_restante.total_seconds() > 0:
            st.metric("⏱️ Tempo Restante", str(tempo_restante).split('.')[0])
            st.write("O sistema encerrará automaticamente quando o tempo acabar.")
        else:
            st.error("Tempo esgotado!"); st.session_state.autenticado = False; st.rerun()
