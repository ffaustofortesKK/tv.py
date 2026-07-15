import streamlit as st
import requests
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# CSS para esconder elementos do Streamlit
st.markdown("""<style>
    #MainMenu {visibility: hidden; display: none;} 
    footer {visibility: hidden; display: none;}
    .video-container { text-align: center; margin-top: 50px; }
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
                
                # Usamos st.components.v1.html para melhor controlo sobre o player
                components.html(f"""
                    <div style='text-align: center;'>
                        <h1 style='color: yellow; font-family: sans-serif;'>SOLTA A VOZ: {status.get('cantor', '').upper()}</h1>
                        <video id="v1" width="800" autoplay playsinline controls style="border: 10px solid #FFD700; border-radius: 20px; background: black;">
                            <source src="{video_url}" type="video/mp4">
                        </video>
                    </div>
                    <script>
                        var vid = document.getElementById('v1');
                        // Tenta dar autoplay
                        vid.muted = true; // Inicia mudo para garantir que o autoplay funcione
                        vid.play().then(() => {{
                            // Após iniciar, tira o mute após 1 segundo
                            setTimeout(() => {{ vid.muted = false; }}, 1000);
                        }}).catch(e => console.log("Autoplay bloqueado"));
                        
                        // Garante que o vídeo não para
                        vid.addEventListener('ended', () => {{ vid.play(); }});
                    </script>
                """, height=700)
                
                time.sleep(30) 
                requests.put(URL_STATUS, json={"acao": "espera"})
                
            else:
                display.markdown("<h1 style='text-align: center; color: #555; margin-top: 200px;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
    except Exception as e:
        display.warning("Aguardando conexão...")
        
    time.sleep(2)
