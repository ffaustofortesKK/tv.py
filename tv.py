import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""<style>
    #MainMenu {visibility: hidden; display: none;} 
    footer {visibility: hidden; display: none;}
    .video-container { text-align: center; margin-top: 50px; }
    video { width: 80%; border: 10px solid #FFD700; border-radius: 20px; background: black; }
</style>""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")

if not slug:
    st.error("ERRO: URL da TV inválida. Use ?prestador=seu-slug")
    st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
display = st.empty()

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            if isinstance(status, dict) and status.get("acao") == "contagem":
                video_url = status.get('url_video', '')
                
                # ATENÇÃO: 'muted' é OBRIGATÓRIO para autoplay. 
                # 'playsinline' é obrigatório para dispositivos móveis/TVs.
                display.markdown(f"""
                    <div class='video-container'>
                        <h1 style='color: yellow;'>SOLTA A VOZ: {status.get('cantor', '').upper()}</h1>
                        <video id="v1" width="800" autoplay muted playsinline controls>
                            <source src="{video_url}" type="video/mp4">
                            Seu navegador não suporta vídeos.
                        </video>
                        <script>
                            document.getElementById('v1').play();
                        </script>
                    </div>
                """, unsafe_allow_html=True)
                
                time.sleep(30) 
                requests.put(URL_STATUS, json={"acao": "espera"})
                
            else:
                display.markdown("<h1 style='text-align: center; color: #555; margin-top: 200px;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
    except Exception as e:
        display.warning("Aguardando conexão...")
        
    time.sleep(2)
