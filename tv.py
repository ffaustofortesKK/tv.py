import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# Captura o slug via URL: ?prestador=nome-do-slug
query_params = st.query_params
slug = query_params.get("prestador", "geral")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

st.markdown("<h1 style='text-align: center;'>CONECTADO AO: " + slug.upper() + "</h1>", unsafe_allow_html=True)

# Área de exibição
display = st.empty()

# Loop de verificação
while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            if status and status.get("acao") == "contagem":
                display.markdown(f"""
                    <div style='text-align: center; border: 5px solid yellow; padding: 50px;'>
                        <h1 style='color: yellow; font-size: 100px;'>SOLTA A VOZ!</h1>
                        <h2 style='color: white; font-size: 70px;'>{status.get('cantor', '').upper()}</h2>
                    </div>
                """, unsafe_allow_html=True)
            else:
                display.markdown("<h1 style='text-align: center; color: #555; margin-top: 100px;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
    except:
        display.write("Erro de conexão com Firebase.")
        
    time.sleep(2) # Verifica o status a cada 2 segundos
