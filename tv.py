import streamlit as st
import requests
import time

# Configuração da página para modo tela cheia
st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# Ocultar elementos padrão do Streamlit
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# Captura o slug via URL: ?prestador=...
params = st.query_params
slug = params.get("prestador")

# Verificação de segurança
if not slug:
    st.markdown("<h1 style='text-align: center; color: red;'>ERRO: URL da TV inválida.</h1>", unsafe_allow_html=True)
    st.write("Certifique-se de que o link contém: `?prestador=seu-slug-aqui`")
    st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

display = st.empty()

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            # Verifica se existe um status ativo
            if isinstance(status, dict) and status.get("acao") == "contagem":
                display.markdown(f"""
                    <div style='text-align: center; border: 10px solid #FFD700; padding: 60px; background-color: #111; border-radius: 20px;'>
                        <h1 style='color: yellow; font-size: 100px; margin-bottom: 20px;'>SOLTA A VOZ!</h1>
                        <h2 style='color: white; font-size: 70px; margin-bottom: 10px;'>CANTOR: {status.get('cantor', '').upper()}</h2>
                        <h3 style='color: #00FF00; font-size: 60px;'>🎵 {status.get('musica', '').upper()}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Aguarda 10 segundos para que a mensagem seja lida e depois limpa o sinal
                time.sleep(10)
                requests.put(URL_STATUS, json={"acao": "espera"})
                
            else:
                display.markdown("""
                    <div style='text-align: center; margin-top: 150px;'>
                        <h1 style='color: #555; font-size: 90px;'>AGUARDANDO NOVO CANTOR...</h1>
                    </div>
                """, unsafe_allow_html=True)
        else:
            display.markdown("<h1 style='text-align: center; color: #555;'>Aguardando sinal do sistema...</h1>", unsafe_allow_html=True)
            
    except Exception as e:
        display.warning(f"Conexão instável, tentando reconectar...")
        
    time.sleep(2)
