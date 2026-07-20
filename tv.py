import streamlit as st
import requests
import time
import cloudinary
import cloudinary.api

# Configuração Cloudinary para buscar os videoclipes de fundo
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; margin: 0; padding: 0; overflow: hidden; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        
        .video-container { 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            background: black; display: flex; justify-content: center; align-items: center; z-index: 9999; 
        }
        video { width: 100vw; height: 100vh; object-fit: contain; background: black; }
        
        /* Layout dividido da Tela de Espera */
        .main-layout { display: flex; width: 100vw; height: 100vh; padding: 30px; box-sizing: border-box; gap: 30px; }
        .escola-fila { flex: 1; background: rgba(20,20,20,0.85); padding: 30px; border-radius: 20px; border: 2px solid #333; overflow-y: auto; }
        .lado-clips { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; background: rgba(10,10,10,0.9); border-radius: 20px; border: 2px solid #333; padding: 20px; }
        
        /* Contagem Decrescente */
        .countdown-container {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.95); display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 9998; color: white;
        }
        .countdown-number { font-size: 12rem; color: yellow; font-weight: bold; animation: pulse 1s infinite; text-shadow: 0 0 30px rgba(255,255,0,0.7); }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Função para buscar um videoclip aleatório da pasta "Video_Clipes" no Cloudinary
@st.cache_data(ttl=60)
def obter_videoclip_aleatorio():
    try:
        # Tenta buscar recursos na pasta Video_Clipes ou com prefixo geral
        resources = cloudinary.api.resources(type="upload", resource_type="video", max_results=50)
        clips = [r['secure_url'] for r in resources.get('resources', []) if 'video' in r.get('public_id', '').lower() or 'clipe' in r.get('public_id', '').lower() or 'clip' in r.get('public_id', '').lower()]
        if not clips and resources.get('resources'):
            clips = [r['secure_url'] for r in resources.get('resources', [])]
        if clips:
            import random
            return random.choice(clips)
    except:
        pass
    return None

# Buscar dados do Firebase
try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

# 1. EXIBIÇÃO DO VÍDEO DE KARAOKE EM TELA CHEIA
if comando == "play":
    if url_video:
        st.markdown(f"""
            <div class="video-container" id="container-video">
                <video id="karaoke-video" autoplay playsinline controls>
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta reprodução de vídeo.
                </video>
            </div>
            <script>
                const vid = document.getElementById('karaoke-video');
                vid.play().catch(error => {{
                    vid.muted = true;
                    vid.play();
                }});

                vid.onended = function() {{
                    fetch('{URL_STATUS}', {{
                        method: 'PATCH',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ comando: 'fim', url_video: '', musica: '', cantor: '' }})
                    }}).then(() => {{
                        window.location.reload();
                    }});
                }};
            </script>
        """, unsafe_allow_html=True)

        while True:
            time.sleep(3)
            try:
                check_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
                if check_status.get("comando") != "play":
                    st.rerun()
            except:
                pass
    else:
        st.error("⚠️ Comando 'play' recebido, mas o link do vídeo está vazio.")
        time.sleep(3)
        requests.patch(URL_STATUS, json={"comando": "fim"})
        st.rerun()

# 2. CONTAGEM DECRESCENTE (3, 2, 1) ANTES DE ABRIR O KARAOKE
elif comando == "aguardando_play":
    cantor_atual = str(res_status.get('cantor', '')).upper()
    musica_atual = str(res_status.get('musica', '')).upper()
    
    st.markdown(f"""
        <div class="countdown-container">
            <h1 style="font-size: 2.5rem; color: #00ff00; margin-bottom: 10px;">PRÓXIMO CANTOR: {cantor_atual}</h1>
            <h2 style="font-size: 1.8rem; color: yellow; margin-bottom: 40px;">{musica_atual}</h2>
            <p style="font-size: 1.2rem; letter-spacing: 2px; color: #aaa; text-transform: uppercase;">O palco é seu em:</p>
            <div class="countdown-number" id="relogio">3</div>
        </div>
        <script>
            let segundos = 3;
            const elem = document.getElementById('relogio');
            const timer = setInterval(() => {{
                segundos--;
                if (segundos > 0) {{
                    elem.innerHTML = segundos;
                }} else if (segundos === 0) {{
                    elem.innerHTML = "JÁ!";
                }} else {{
                    clearInterval(timer);
                    // Dispara automaticamente o comando play no firebase via JS quando o timer acaba
                    fetch('{URL_STATUS}', {{
                        method: 'PATCH',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ comando: 'play' }})
                    }}).then(() => {{
                        window.location.reload();
                    }});
                }}
            }}, 1000);
        </script>
    """, unsafe_allow_html=True)
    time.sleep(4.5)
    st.rerun()

# 3. TELA PRINCIPAL DIVIDIDA: FILA DE ESPERA (ESQUERDA) + VIDEOCLIPE (DIREITA)
else:
    clipe_url = obter_videoclip_aleatorio()
    
    # Monta a estrutura em duas colunas visuais via HTML/CSS e Streamlit
    col_esq, col_dir = st.columns([1.1, 0.9])
    
    with col_esq:
        st.markdown("<h1 style='color: gold; font-size: 2.2rem; margin-bottom: 20px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)
        st.markdown("<div class='escola-fila'>", unsafe_allow_html=True)
        
        if res_pedidos:
            pedidos_lista = list(res_pedidos.items())
            contador_exibicao = 1
            for p_id, p in pedidos_lista:
                if not str(p.get('musica', '')).startswith("PEDIDO:"):
                    st.markdown(f"""
                        <div style='margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;'>
                            <h3 style='margin:0; font-size: 1.3rem; color: #00ff00;'>{contador_exibicao}. {str(p.get('cantor')).upper()}</h3>
                            <p style='margin:5px 0 0 0; font-size: 1.1rem;'><span class='musica-style'>🎵 {str(p.get('musica')).upper()}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                    contador_exibicao += 1
            if contador_exibicao == 1:
                st.markdown("<h3 style='color: #888;'>Nenhum cantor na fila de momento.</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='color: #888;'>A fila está vazia. Faça o seu pedido pelo telemóvel! 📱</h3>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col_dir:
        st.markdown("<h2 style='color: #00ffff; font-size: 1.8rem; text-align: center; margin-bottom: 15px;'>🎬 VIDEOCLIPES</h2>", unsafe_allow_html=True)
        st.markdown("<div class='lado-clips'>", unsafe_allow_html=True)
        
        if clipe_url:
            st.markdown(f"""
                <video width="100%" autoplay loop muted playsinline style="border-radius: 15px; border: 2px solid #444; max-height: 60vh; object-fit: cover;">
                    <source src="{clipe_url}" type="video/mp4">
                    Seu navegador não suporta vídeos.
                </video>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #aaa; text-align: center;'>Adicione vídeos à pasta do Cloudinary para exibir aqui.</p>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    time.sleep(4)
    st.rerun()
