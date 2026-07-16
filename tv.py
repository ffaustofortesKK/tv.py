import streamlit as st
import requests
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: url('https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=2074&auto=format&fit=crop'); background-size: cover; background-position: center; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 3px 3px 6px #000; }
        .musica-style { color: yellow; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")
if not slug: st.error("URL Inválida"); st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

try:
    res_status = requests.get(URL_STATUS, timeout=5).json() or {}
    res_pedidos = requests.get(URL_PEDIDOS, timeout=5).json() or {}
except:
    res_status = {}; res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

if comando == "play" and url_video:
    components.html(f"""
        <div style='display:flex; justify-content:center; align-items:center; height:90vh;'>
            <video id="v1" width="80%" autoplay playsinline src="{url_video}" style="border:10px solid gold; border-radius:20px;"></video>
        </div>
        <script>
            var v = document.getElementById('v1');
            v.play();
            v.onended = () => {{ fetch('{URL_STATUS}', {{ method: 'PATCH', body: JSON.stringify({{comando: 'finalizado'}}) }}); }};
        </script>
    """, height=700)

elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; background:rgba(0,0,0,0.7); padding:50px; border-radius:20px; color:white;'>
            <h1>VEZ DE: <span class="cantor-style">{res_status.get('cantor', '').upper()}</span></h1>
            <h3>Aguardando o cantor iniciar a música no telemóvel...</h3>
        </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("<h1 style='text-align:center; color:white; text-shadow: 2px 2px #000;'>FF KARAOKE - AGUARDANDO...</h1>", unsafe_allow_html=True)
    if res_pedidos:
        st.markdown("<div style='background:rgba(0,0,0,0.6); padding:20px; border-radius:15px; color:white; width: 60%; margin: 0 auto;'>", unsafe_allow_html=True)
        st.subheader("🎤 Fila de Espera:")
        for i, (p_id, p) in enumerate(res_pedidos.items(), 1):
            st.markdown(f"### {i}. <span class='cantor-style'>{p.get('cantor')}</span> - <span class='musica-style'>{p.get('musica')}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

time.sleep(3); st.rerun()
