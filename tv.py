import streamlit as st
import requests
import time

st.set_page_config(page_title="Tela Karaoke", layout="wide")

# Ocultar elementos visuais padrão do Streamlit para parecer um player de TV limpo
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# Obter o prestador através do link (ex: app.streamlit.app/?prestador=nome-sobrenome)
query_params = st.query_params
prestador = query_params.get("prestador", None)

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"

if not prestador:
    st.error("⚠️ Nenhum prestador associado a esta tela. Verifique o link de acesso.")
else:
    url_status = f"{BASE_URL}/status_{prestador}.json"
    
    # Contentor principal da Tela
    placeholder = st.empty()
    
    # Obter estado atual da nuvem
    try:
        resposta = requests.get(url_status)
        dados = resposta.json() if resposta.status_code == 200 else {}
    except:
        dados = {}
        
    comando = dados.get("comando", "")
    url_video = dados.get("url_video", "")
    cantor = dados.get("cantor", "")
    musica = dados.get("musica", "")
    
    # Se o comando for para parar ou se não houver vídeo, mostra a tela de espera / logo
    if comando == "aguardando_play" or not url_video or url_video == "":
        with placeholder.container():
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background-color: #0e1117; color: white; text-align: center;">
                    <h1 style="font-size: 4rem; color: #ffd700; margin-bottom: 10px;">🎤 GRUPO FF KARAOKE</h1>
                    <p style="font-size: 1.8rem; color: #aaa;">A aguardar o próximo cantor...</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Se houver vídeo e comando ativo, reproduz o vídeo na tela inteira
        with placeholder.container():
            st.markdown(f"""
                <div style="background-color: black; width: 100vw; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <div style="position: absolute; top: 20px; left: 30px; z-index: 999; background: rgba(0,0,0,0.7); padding: 10px 20px; border-radius: 8px; border: 1px solid #ffd700;">
                        <h3 style="color: #ffd700; margin: 0;">🎤 A Cantar: {cantor}</h3>
                        <p style="color: white; margin: 0; font-size: 1.2rem;">🎵 {musica}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Componente de vídeo nativo em HTML5 com autoplay ativado
            st.markdown(f"""
                <video width="100%" height="90%" controls autoplay style="background: black;">
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta a tag de vídeo.
                </video>
            """, unsafe_allow_html=True)

    # Atualiza a tela automaticamente a cada 2 segundos para apanhar o sinal de "Stop" emitido pelo prestador
    time.sleep(2)
    st.rerun()
