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
        .video-container { display:flex; justify-content:center; align-items:center; height:70vh; }
        .fila-container { background:rgba(0,0,0,0.8); padding:20px; border-radius:15px; color:white; width: 80%; margin: 20px auto; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")
if not slug: st.error("URL Inválida"); st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}; res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

# 1. EXIBIÇÃO DO VÍDEO
if comando == "play" and url_video:
    components.html(f"""
        <div class="video-container">
            <video id="v1" width="80%" autoplay playsinline muted src="{url_video}" style="border:10px solid gold; border-radius:20px;"></video>
        </div>
        <script>
            var v = document.getElementById('v1');
            v.muted = false;
            v.play().catch(() => {{
                document.body.innerHTML += '<button onclick="v.muted=false; v.play(); this.remove();" style="position:fixed; top:50%; left:50%; padding:20px; font-size:24px; cursor:pointer;">CLIQUE PARA INICIAR O SOM</button>';
            }});
            v.onended = () => {{ fetch('{URL_STATUS}', {{ method: 'PATCH', body: JSON.stringify({{comando: 'finalizado'}}) }}); }};
        </script>
    """, height=600)

# 2. VEZ DO CANTOR
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:30px; color:white;'>
            <h1>VEZ DE: <span class="cantor-style">{res_status.get('cantor', '').upper()}</span></h1>
            <h3>Aguardando o cantor carregar no botão no telemóvel...</h3>
        </div>
    """, unsafe_allow_html=True)

# 3. CABEÇALHO PADRÃO
else:
    st.markdown("<h1 style='text-align:center; color:white; margin-top: 20px;'>FF KARAOKE</h1>", unsafe_allow_html=True)

# 4. LISTA DE PEDIDOS (Sempre visível abaixo)
if res_pedidos:
    st.markdown("<div class='fila-container'>", unsafe_allow_html=True)
    st.subheader("🎤 Fila de Espera:")
    # Converte o dicionário em lista para iterar
    pedidos_lista = list(res_pedidos.items())
    for i, (p_id, p) in enumerate(pedidos_lista, 1):
        st.markdown(f"### {i}. <span class='cantor-style'>{p.get('cantor')}</span> - <span class='musica-style'>{p.get('musica')}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if comando == "finalizado":
    requests.patch(URL_STATUS, json={"comando": "aguardando"})

time.sleep(2)
st.rerun()
