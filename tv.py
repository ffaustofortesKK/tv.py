import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# Ocultar elementos padrão do Streamlit para modo TV
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

query_params = st.query_params
slug = query_params.get("prestador", "geral")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

display = st.empty()

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            if status and status.get("acao") == "contagem":
                display.markdown(f"""
                    <div style='text-align: center; border: 5px solid yellow; padding: 40px; background-color: #111;'>
                        <h1 style='color: yellow; font-size: 80px;'>SOLTA A VOZ!</h1>
                        <h2 style='color: white; font-size: 60px;'>CANTOR: {status.get('cantor', '').upper()}</h2>
                        <h3 style='color: #00FF00; font-size: 50px;'>MÚSICA: {status.get('musica', '').upper()}</h3>
                    </div>
                """, unsafe_allow_html=True)
            else:
                display.markdown("<h1 style='text-align: center; color: #555; margin-top: 100px;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
    except:
        display.write("Aguardando conexão...")
        
    time.sleep(2)
