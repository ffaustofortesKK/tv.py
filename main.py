import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- PAINEL DO ADMIN ---
def render_admin():
    st.header("⚙️ Painel do Operador")
    if st.button("🔄 Refresh Manual"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if not solics:
        st.write("Nenhuma solicitação pendente.")
        return

    # Cabeçalho da Planilha
    col_head1, col_head2, col_head3 = st.columns([2, 2, 1])
    col_head1.write("**Utilizador**")
    col_head2.write("**Ação/Status**")
    col_head3.write("**Código**")

    for key, info in solics.items():
        usuario = info.get('usuario')
        estado = info.get('estado', 'Pendente')
        
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(f"👤 {usuario}")
        
        if estado == "Pendente":
            # Campos para gerar o código
            codigo_gerado = c3.text_input("Cod", key=f"cod_{key}", value="1234")
            if c2.button("✅ Aprovar", key=f"apr_{key}"):
                # Grava o token
                expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                requests.patch(f"{URL_TOKENS}/{usuario}.json", json={"senha": codigo_gerado, "expira": expira})
                # Atualiza estado do pedido
                requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Aprovado"})
                st.rerun()
            if c2.button("❌ Recusar", key=f"rec_{key}"):
                requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Recusado"})
                st.rerun()
        else:
            c2.write(f"**{estado}**")

# --- ÁREA DO CLIENTE ---
def render_cliente():
    if not st.session_state.autenticado:
        st.subheader("🔑 Acesso ao Karaoke")
        nome = st.text_input("Nome:")
        
        if 'pendente' not in st.session_state:
            if st.button("Solicitar Acesso"):
                requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
                st.session_state.pendente = nome
                st.rerun()
        else:
            st.info(f"Olá {st.session_state.pendente}, aguardando aprovação do operador...")
            if st.button("🔄 Verificar Acesso"):
                solics = requests.get(URL_SOLICITACOES).json()
                for key, info in (solics or {}).items():
                    if info.get('usuario') == st.session_state.pendente:
                        if info.get('estado') == "Aprovado":
                            st.session_state.autenticado = True
                            st.session_state.nome = st.session_state.pendente
                            del st.session_state.pendente
                            st.rerun()
                        elif info.get('estado') == "Recusado":
                            st.error("Seu pedido foi recusado pelo operador.")
                            del st.session_state.pendente
                            st.rerun()
    else:
        st.success(f"Bem-vindo, {st.session_state.nome}!")
        # Lógica de Karaoke aqui...

# --- LÓGICA PRINCIPAL ---
nome_input = st.sidebar.text_input("Nome para Login (ADMIN se for você)")
senha_input = st.sidebar.text_input("Senha", type="password")

if nome_input == "ADMIN" and senha_input == "1234":
    render_admin()
else:
    render_cliente()
