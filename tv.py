import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# Ocultar menu do Streamlit para parecer uma tela de TV profissional
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .css-15zrgzn {display: none;}
    </style>
    """, unsafe_allow_html=True)

# Captura o slug do prestador via URL: tv.py?prestador=nome-do-slug
query_params = st.query_params
slug = query_params.get("prestador", "geral")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

st.markdown("<h1 style='text-align: center; color: white;'>AGUARDANDO PEDIDOS...</h1>", unsafe_allow_html=True)

# Lógica de atualização a cada 2 segundos
placeholder = st.empty()

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        status = response.json()
        
        if status and status.get("acao") == "contagem":
            placeholder.markdown(f"""
                <div style='text-align: center; margin-top: 100px;'>
                    <h1 style='color: yellow; font-size: 80px;'>SOLTA A VOZ!</h1>
                    <h2 style='color: white; font-size: 60px;'>CANTOR: {status.get('cantor', '').upper()}</h2>
                </div>
            """, unsafe_allow_html=True)
        else:
            placeholder.markdown("<h1 style='text-align: center; color: #555;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
            
    except:
        pass
        
    time.sleep(2)
