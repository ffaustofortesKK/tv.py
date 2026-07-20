import streamlit as st
import requests
import time
import cloudinary
import cloudinary.api

# Configuração Cloudinary para ir buscar os clipes da nova pasta
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
        .layout-principal { display: flex; width: 100vw; height: 100vh; padding: 20px; box-sizing: border-box; gap: 20px; }
        .coluna-esquerda { flex: 1; background: rgba(0,0,0,0.85); padding: 30px; border-radius: 15px; border: 2px solid #333; overflow-y: auto; }
        .coluna-direita { width: 450px; background: rgba(0,0,0,0.85); padding: 20px; border-radius: 15px; border: 2px solid #333; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .contador-box { font-size: 8rem; color: yellow; font-weight: bold; text-shadow: 0 0 20px red; text-align: center; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Buscar dados do Firebase
try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

# Função auxiliar para recolher aleatoriamente um vídeo clipe da pasta criada no Cloudinary
def obter_video_clipe_aleatorio():
    try:
        # Altere "Video_Clipes" para o nome exato da pasta que criou no Cloudinary se necessário
        resources = cloudinary.api.resources(type="upload", resource_type="video", prefix="Video_Clipes", max_results=50)
        lista = resources.get('resources', [])
        if lista:
            import random
            return random.choice(lista)['secure_url']
    except:
        pass
    return None

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

# 2. CONTAGEM DECRESCENTE (3, 2, 1, 0) ANTES DE ABRIR O KARAOKE
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:80px; color:white;'>
            <h1 style='font-size: 2.5rem; color: #00ff00;'>A CHAMAR AO PALCO:</h1>
            <h2 style='font-size: 3.5rem;' class="cantor-style">{str(res_status.get('cantor', '')).upper()}</h2>
            <h3 style='font-size: 2rem; color: yellow;'>{str(res_status.get('musica', '')).upper()}</h3>
            <hr style='width: 50%; margin: 20px auto; border-color: #444;'>
            <p style='font-size: 1.5rem; color: #ccc;'>O palco vai abrir em:</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Executa a contagem visual de 3 até 0
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    # Assim que chega a 0, muda automaticamente o comando para "play" para arrancar o vídeo
    requests.patch(URL_STATUS, json={"comando": "play"})
    st.rerun()

# 3. TELA PRINCIPAL: FILA DE ESPERA À ESQUERDA E VÍDEO CLIPE EM MINIATURA À DIREITA
else:
    cl1, cl2 = st.columns([1.3, 1])

    with cl1:
        st.markdown("<h1 style='color:gold; font-size: 2.5rem; margin-bottom: 20px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)
        st.markdown("<div class='coluna-esquerda'>", unsafe_allow_html=True)
        
        if res_pedidos:
            pedidos_lista = list(res_pedidos.items())
            contador_exibicao = 1
            for p_id, p in pedidos_lista:
                if not str(p.get('musica', '')).startswith("PEDIDO:"):
                    st.markdown(f"<h3 style='margin: 15px 0;'>{contador_exibicao}. <span class='cantor-style'>{str(p.get('cantor')).upper()}</span> ➔ <span class='musica-style'>{str(p.get('musica')).upper()}</span></h3>", unsafe_allow_html=True)
                    contador_exibicao += 1
            if contador_exibicao == 1:
                st.info("Ainda sem cantores na fila.")
        else:
            st.info("A fila está vazia. Envie músicas pelo telemóvel!")
            
        st.markdown("</div>", unsafe_allow_html=True)

    with cl2:
        st.markdown("<h3 style='color:white; text-align:center; margin-bottom: 10px;'>📺 VÍDEO CLIPE EM DESTAQUE</h3>", unsafe_allow_html=True)
        st.markdown("<div class='coluna-direita'>", unsafe_allow_html=True)
        
        # Puxa um vídeo clipe da pasta do Cloudinary para passar em miniatura
        url_clipe = obter_video_clipe_aleatorio()
        if url_clipe:
            st.markdown(f"""
                <video width="100%" height="320px" autoplay muted loop playsinline style="border-radius: 10px; border: 2px solid gold; object-fit: cover;">
                    <source src="{url_clipe}" type="video/mp4">
                    Seu navegador não suporta vídeo.
                </video>
            """, unsafe_allow_html=True)
        else:
            st.warning("Adicione vídeos na pasta 'Video_Clipes' no Cloudinary.")
            
        st.markdown("</div>", unsafe_allow_html=True)

    time.sleep(5)
    st.rerun()
