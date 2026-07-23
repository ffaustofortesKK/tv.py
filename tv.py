import streamlit as st
import requests

st.set_page_config(page_title="Tela Karaoke", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            background-color: #0e1117;
            height: 100vh;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

query_params = st.query_params
prestador = query_params.get("prestador", None)

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"

if not prestador:
    st.error("⚠️ Nenhum prestador associado a esta tela. Verifique o link de acesso.")
else:
    url_status = f"{BASE_URL}/status_{prestador}.json"
    
    try:
        resposta = requests.get(url_status)
        dados = resposta.json() if resposta.status_code == 200 else {}
    except:
        dados = {}
        
    comando = dados.get("comando", "")
    url_video = dados.get("url_video", "")
    cantor = dados.get("cantor", "")
    musica = dados.get("musica", "")
    
    # Se explicitamente mandou parar ou se não há URL de vídeo válida, mostra a espera
    if comando == "parar" or not url_video:
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background-color: #0e1117; color: white; text-align: center;">
                <h1 style="font-size: 4rem; color: #ffd700; margin-bottom: 10px;">🎤 GRUPO FF KARAOKE</h1>
                <p style="font-size: 1.8rem; color: #aaa;">A aguardar o próximo cantor...</p>
                <p style="font-size: 0.9rem; color: #444; position: absolute; bottom: 10px;">Estado Firebase - Comando: {comando} | URL: {'Sim' if url_video else 'Não'}</p>
            </div>
            <script>
                setInterval(function() {{
                    fetch("{url_status}")
                        .then(response => response.json())
                        .then(data => {{
                            // Se houver um comando novo ou um URL de vídeo válido, recarrega a página para tocar
                            if (data.url_video && data.url_video !== "" && data.comando !== "parar") {{
                                window.location.reload();
                            }}
                        }});
                }}, 2000);
            </script>
        """, unsafe_allow_html=True)
    else:
        # Exibe o vídeo quando houver dados válidos
        html_content = f"""
            <div style="position: absolute; top: 20px; left: 30px; z-index: 999; background: rgba(0,0,0,0.8); padding: 10px 20px; border-radius: 8px; border: 1px solid #ffd700;">
                <h3 style="color: #ffd700; margin: 0;">🎤 A Cantar: {cantor}</h3>
                <p style="color: white; margin: 0; font-size: 1.2rem;">🎵 {musica}</p>
            </div>
            <div style="width: 100vw; height: 100vh; background: black; display: flex; align-items: center; justify-content: center;">
                <video id="karaoke-video" width="100%" height="100%" controls autoplay style="background: black; object-fit: contain;">
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta a tag de vídeo.
                </video>
            </div>
            <script>
                setInterval(function() {{
                    fetch("{url_status}")
                        .then(response => response.json())
                        .then(data => {{
                            if (data.comando === "parar" || !data.url_video) {{
                                window.location.reload();
                            }}
                        }});
                }}, 2000);
            </script>
        """
        st.markdown(html_content, unsafe_allow_html=True)
