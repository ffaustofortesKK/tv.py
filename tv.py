import streamlit as st
import requests
import time
import streamlit.components.v1 as components

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
slug = params.get("prestador")
if not slug: st.error("URL Inválida"); st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Busca de dados com tratamento de erro
try:
    res_status = requests.get(f"{URL_STATUS}?t={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?t={time.time()}", timeout=5).json() or {}
except:
    res_status = {}; res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

# 1. EXIBIÇÃO DO VÍDEO
if comando == "play" and url_video:
    components.html(f"""
        <div class="video-container">
            <video id="v1" width="80%" autoplay playsinline controls src="{url_video}" style="border:10px solid gold; border-radius:20px;"></video>
        </div>
        <script>
            var v = document.getElementById('v1');
            v.onended = () => {{ 
                fetch('{URL_STATUS}', {{ method: 'PATCH', body: JSON.stringify({{comando: 'finalizado'}}) }});
            }};
        </script>
    """, height=650)

# 2. VEZ DO CANTOR
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:30px; color:white;'>
            <h1>VEZ DE: <span class="cantor-style">{res_status.get('cantor', '').upper()}</span></h1>
            <h3>Aguardando o cantor carregar no botão no telemóvel...</h3>
        </div>
    """, unsafe_allow_html=True)

# 3. CABEÇALHO
else:
    st.markdown("<h1 style='text-align:center; color:white; margin-top: 20px;'>FF KARAOKE</h1>", unsafe_allow_html=True)

# 4. LISTA DE PEDIDOS
if res_pedidos:
    st.markdown("<div class='fila-container'>", unsafe_allow_html=True)
    st.subheader("🎤 Fila de Espera:")
    # Converte dicionário em lista para exibição ordenada
    pedidos_lista = list(res_pedidos.items())
    for i, (p_id, p) in enumerate(pedidos_lista, 1):
        st.markdown(f"### {i}. <span class='cantor-style'>{p.get('cantor')}</span> - <span class='musica-style'>{p.get('musica')}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# LÓGICA DE LIMPEZA APÓS MÚSICA TERMINAR
if comando == "finalizado":
    # 1. Remove o pedido da fila (o primeiro da lista)
    if res_pedidos:
        primeiro_id = list(res_pedidos.keys())[0]
        requests.delete(f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}/{primeiro_id}.json")
    
    # 2. Reseta o status para "aguardando"
    requests.patch(URL_STATUS, json={"comando": "aguardando", "cantor": "", "musica": ""})
    st.rerun()

time.sleep(2)
st.rerun()
