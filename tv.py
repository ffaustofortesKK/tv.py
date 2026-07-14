import streamlit as st
import requests
import time

st.set_page_config(page_title="Ecrã TV", layout="wide")

# O slug é passado pela URL (ex: tv.py?prestador=nome-do-slug)
query_params = st.query_params
slug = query_params.get("prestador", "geral")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

st.markdown("<h1 style='text-align: center;'>AGUARDANDO PEDIDO...</h1>", unsafe_allow_html=True)

# Lógica simples de monitorização
status = requests.get(URL_STATUS).json()
if status and status.get("acao") == "contagem":
    st.markdown(f"<h1 style='text-align: center; color: yellow;'>SOLTA A VOZ, {status['cantor']}!</h1>", unsafe_allow_html=True)
    # Aqui você poderia adicionar o áudio de palmas ou contagem regressiva
    # time.sleep(5)
    # requests.delete(URL_STATUS) # Reseta o status
