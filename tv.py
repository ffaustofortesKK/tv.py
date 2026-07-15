import streamlit as st
import requests
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")
if not slug: st.error("URL Inválida"); st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
display = st.empty()
video_atual = ""

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            if isinstance(status, dict) and status.get("acao") == "contagem":
                nova_url = status.get('url_video', '')
                if nova_url != video_atual:
                    video_atual = nova_url
                    components.html(f"""
                        <div style='text-align: center; background: black; height: 100vh;'>
                            <h1 style='color: yellow;'>SOLTA A VOZ: {status.get('cantor', '').upper()}</h1>
                            <video id="v1" width="800" autoplay playsinline style="border: 10px solid #FFD700;">
                                <source src="{nova_url}" type="video/mp4">
                            </video>
                        </div>
                        <script>
                            var vid = document.getElementById('v1');
                            vid.muted = true;
                            vid.play().then(() => {{ setTimeout(() => {{ vid.muted = false; }}, 1000); }});
                            
                            // Monitoramento de Comandos em tempo real
                            setInterval(() => {{
                                fetch('{URL_STATUS}').then(r => r.json()).then(data => {{
                                    if(data.comando === 'pause') vid.pause();
                                    if(data.comando === 'play') vid.play();
                                    if(data.comando === 'repeat') {{ vid.currentTime = 0; vid.play(); }}
                                    if(data.comando === 'voltar') vid.currentTime -= 10;
                                    if(data.comando === 'avancar') vid.currentTime += 10;
                                }});
                            }}, 1000);
                            
                            vid.onended = function() {{ window.location.reload(); }};
                        </script>
                    """, height=800)
            else:
                display.markdown("<h1 style='text-align: center; color: white; margin-top: 200px;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
    except: display.warning("Conectando...")
    time.sleep(2)
