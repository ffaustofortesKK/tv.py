import streamlit as st
import requests
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# CSS para o fundo da TV e esconder elementos
st.markdown("""
    <style>
        .stApp { background: url('https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=2074&auto=format&fit=crop'); background-size: cover; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")
if not slug: st.error("URL Inválida"); st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

display = st.empty()
video_atual = ""

while True:
    try:
        # Carrega status e lista de pedidos
        status = requests.get(URL_STATUS, timeout=5).json()
        pedidos = requests.get(URL_PEDIDOS, timeout=5).json()
        
        if isinstance(status, dict) and status.get("url_video") and status.get("comando") == "play":
            nova_url = status.get("url_video")
            
            components.html(f"""
                <div style='display:flex; justify-content:center; align-items:center; height:100vh;'>
                    <video id="v1" width="90%" autoplay playsinline src="{nova_url}" style="border:10px solid gold; border-radius:20px;"></video>
                </div>
                <script>
                    var v = document.getElementById('v1');
                    v.play();
                    // Quando acaba, limpa o comando no Firebase para voltar ao ecrã de espera
                    v.onended = () => {{
                        fetch('{URL_STATUS}', {{ method: 'PATCH', body: JSON.stringify({{comando: 'stop'}}) }});
                        location.reload();
                    }};
                </script>
            """, height=600)
        else:
            # Ecrã de Espera com Lista de Pedidos
            with display.container():
                st.markdown("<h1 style='text-align:center; color:white; text-shadow: 2px 2px #000;'>AGUARDANDO PRÓXIMO CANTOR...</h1>", unsafe_allow_html=True)
                if pedidos:
                    st.markdown("<div style='background:rgba(0,0,0,0.6); padding:20px; border-radius:15px; color:white;'>", unsafe_allow_html=True)
                    st.subheader("🎤 Fila de Espera:")
                    for i, (p_id, p) in enumerate(pedidos.items(), 1):
                        st.markdown(f"### {i}. {p.get('cantor')} - {p.get('musica')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("Fila vazia. Faça um pedido!")
    except: 
        time.sleep(2)
    time.sleep(2)
