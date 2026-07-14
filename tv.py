import streamlit as st
import requests
import time

# Configuração da página para modo tela cheia
st.set_page_config(page_title="TV KARAOKE", layout="wide")

# Ocultar o menu e o rodapé do Streamlit para parecer uma TV
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# Captura o slug via URL: ?prestador=...
params = st.query_params
slug = params.get("prestador")

if not slug:
    st.error("❌ TV sem prestador configurado. Use: ?prestador=seu-slug-aqui")
    st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

display = st.empty()

# Loop de monitoramento da TV
while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            if data and data.get("acao") == "contagem":
                # Exibição quando há um pedido ativo
                display.markdown(f"""
                    <div style='text-align: center; border: 10px solid #FFD700; padding: 100px; background: #000; border-radius: 20px;'>
                        <h1 style='color: #FFD700; font-size: 120px;'>SOLTA A VOZ!</h1>
                        <h2 style='color: white; font-size: 90px;'>{data.get('cantor', '').upper()}</h2>
                        <h3 style='color: #00FF00; font-size: 70px;'>🎵 {data.get('musica', '').upper()}</h3>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Exibição em espera
                display.markdown("""
                    <div style='text-align: center; margin-top: 200px;'>
                        <h1 style='color: #555; font-size: 80px;'>AGUARDANDO NOVO CANTOR...</h1>
                    </div>
                """, unsafe_allow_html=True)
    except:
        display.write("Aguardando sinal do Firebase...")
        
    time.sleep(2) # Verifica a cada 2 segundos
