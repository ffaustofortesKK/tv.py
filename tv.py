import streamlit as st

import requests

import time



st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")



st.markdown("""

    <style>

        .stApp { background: black; }

        #MainMenu {visibility: hidden;} footer {visibility: hidden;}

        .cantor-style { color: white; font-weight: bold; text-shadow: 3px 3px 6px #000; }

        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }

        .video-container { display:flex; justify-content:center; align-items:center; flex-direction: column; height:75vh; }

        .fila-container { background:rgba(0,0,0,0.8); padding:20px; border-radius:15px; color:white; width: 80%; margin: 20px auto; }

    </style>

""", unsafe_allow_html=True)



params = st.query_params

slug = params.get("prestador", "geral")



URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"



# Buscar dados

try:

    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}

    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}

except:

    res_status = {}

    res_pedidos = {}



comando = res_status.get("comando")

url_video = res_status.get("url_video")



# 1. EXIBIÇÃO DO VÍDEO SE HOUVER URL VÁLIDA E COMANDO PLAY

if comando == "play":

    if url_video: # Verifica se realmente existe um link vindo do Cloudinary

        st.markdown(f'<div class="video-container"><video width="80%" autoplay playsinline controls src="{url_video}" style="border:10px solid gold; border-radius:20px;"></video></div>', unsafe_allow_html=True)

        st.info("🎤 A música está a tocar...")

        

        # --- A ARMADILHA SILENCIOSA ---

        # Fica a verificar o Firebase a cada 3 segundos em background.

        # Não destrói a tela. Só dá rerun quando o DJ mudar o status!

        while True:

            time.sleep(3)

            try:

                check_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}

                if check_status.get("comando") != "play":

                    st.rerun() # Só recarrega quando a música parar ou mudar

            except:

                pass

    else:

        st.error("⚠️ A música foi iniciada, mas o vídeo não foi encontrado no servidor (URL vazia).")

        time.sleep(4)

        st.rerun()



# 2. VEZ DO CANTOR (AGUARDANDO START)

elif comando == "aguardando_play":

    st.markdown(f"""

        <div style='text-align:center; padding:30px; color:white;'>

            <h1>VEZ DE: <span class="cantor-style">{str(res_status.get('cantor', '')).upper()}</span></h1>

            <h3>Música: <span class="musica-style">{str(res_status.get('musica', '')).upper()}</span></h3>

            <h3>Aguardando o cantor carregar no botão no telemóvel...</h3>

        </div>

    """, unsafe_allow_html=True)

    time.sleep(2)

    st.rerun()



# 3. CABEÇALHO PADRÃO E FILA DE ESPERA

else:

    st.markdown("<h1 style='text-align:center; color:white; margin-top: 20px;'>FF KARAOKE</h1>", unsafe_allow_html=True)



    if res_pedidos:

        st.markdown("<div class='fila-container'>", unsafe_allow_html=True)

        st.subheader("🎤 Fila de Espera:")

        pedidos_lista = list(res_pedidos.items())

        for i, (p_id, p) in enumerate(pedidos_lista, 1):

            if not str(p.get('musica', '')).startswith("PEDIDO:"):

                st.markdown(f"### {i}. <span class='cantor-style'>{p.get('cantor')}</span> - <span class='musica-style'>{p.get('musica')}</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        

    time.sleep(2)

    st.rerun()
