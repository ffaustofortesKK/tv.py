import streamlit as st
import requests
import time
import cloudinary
import cloudinary.search
import random

# Configuração Cloudinary
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; margin: 0; padding: 0; overflow: hidden; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        
        /* VÍDEO DE KARAOKE EM TELA TOTAL (100vw x 100vh) */
        .video-container { 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            background: black; display: flex; justify-content: center; align-items: center; z-index: 9999; 
        }
        .video-container video { 
            width: 100vw; height: 100vh; object-fit: contain; background: black; 
        }
        
        /* MINI TELA DE VÍDEO CLIPE: EXATAMENTE 430x306px */
        .video-clipe-box { 
            width: 430px; 
            height: 306px;
            background: black; 
            padding: 0px; 
            border-radius: 4px; 
            border: 2px solid #ffd700; 
            overflow: hidden;
            position: relative;
        }
        .video-clipe-box video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: fill;
            opacity: 0;
            transition: opacity 1s ease-in-out;
        }
        .video-clipe-box video.ativo {
            opacity: 1;
            z-index: 2;
        }
        
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

# Função para ir buscar a lista completa de vídeos da pasta "video_clipes" para a transição cruzada
def obter_lista_videos_clipes():
    try:
        search_result = cloudinary.search.Search()\
            .expression('folder=video_clipes AND resource_type:video')\
            .max_results(50)\
            .execute()
        
        lista = search_result.get('resources', [])
        if lista:
            urls = [item['secure_url'] for item in lista]
            random.shuffle(urls)
            return urls
    except Exception as e:
        print("Erro na busca avançada Cloudinary:", e)
    
    try:
        fallback = cloudinary.api.resources(type="upload", resource_type="video", max_results=50)
        geral = fallback.get('resources', [])
        if geral:
            urls = [item['secure_url'] for item in geral]
            random.shuffle(urls)
            return urls
    except:
        pass
        
    return []

# 1. EXIBIÇÃO DO VÍDEO DE KARAOKE EM TELA TOTAL (EFEITO PLAY)
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

                // Assim que o karaoke terminar, avisa o Firebase para fechar e voltar à fila
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

# 2. CONTAGEM DECRESCENTE (3, 2, 1, 0) - Disparada APENAS quando o comando é 'aguardando_play'
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
    
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    requests.patch(URL_STATUS, json={"comando": "play"})
    st.rerun()

# 3. TELA PRINCIPAL: FILA DE ESPERA À ESQUERDA E MINI TELA 430x306px À DIREITA COM VÍDEOS ALEATÓRIOS E TRANSIÇÃO DE 5s
else:
    cl1, cl2 = st.columns([1.4, 1.2])

    with cl1:
        st.markdown("<h1 style='color:gold; font-size: 2.2rem; margin-bottom: 15px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)
        
        if res_pedidos:
            pedidos_lista = list(res_pedidos.items())
            contador_exibicao = 1
            for p_id, p in pedidos_lista:
                if not str(p.get('musica', '')).startswith("PEDIDO:"):
                    st.markdown(f"<h3 style='margin: 10px 0; font-size: 1.3rem;'>{contador_exibicao}. <span class='cantor-style'>{str(p.get('cantor')).upper()}</span> ➔ <span class='musica-style'>{str(p.get('musica')).upper()}</span></h3>", unsafe_allow_html=True)
                    contador_exibicao += 1
            if contador_exibicao == 1:
                st.info("Ainda sem cantores na fila.")
        else:
            st.info("A fila está vazia. Envie músicas pelo telemóvel!")

    with cl2:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        
        # Obtém a lista aleatória de clips
        lista_urls = obter_lista_videos_clipes()
        
        if lista_urls:
            # Constrói o elemento com dois motores de vídeo em loop cruzado para transição suave de 5 segundos antes do fim
            urls_js = str(lista_urls).replace("'", '"')
            st.markdown(f"""
                <div class="video-clipe-box" id="box-player">
                    <video id="vA" autoplay muted playsinline></video>
                    <video id="vB" muted playsinline></video>
                </div>
                <script>
                    const playlist = {urls_js};
                    let currentIndex = 0;
                    
                    const vA = document.getElementById('vA');
                    const vB = document.getElementById('vB');
                    
                    let activeV = vA;
                    let nextV = vB;
                    
                    function playVideo(vidElement, url, callbackWhenDone) {{
                        vidElement.src = url;
                        vidElement.load();
                        vidElement.play().catch(e => console.log("Autoplay bloqueado:", e));
                        
                        vidElement.ontimeupdate = function() {{
                            // Se faltarem 5 segundos para o fim e ainda não disparou a transição
                            if (vidElement.duration && (vidElement.duration - vidElement.currentTime <= 5) && !vidElement.transitionTriggered) {{
                                vidElement.transitionTriggered = true;
                                if (callbackWhenDone) callbackWhenDone();
                            }}
                        }};
                        
                        vidElement.onended = function() {{
                            // Segurança caso acabe sem passar pelos 5s
                            if (!vidElement.transitionTriggered && callbackWhenDone) {{
                                vidElement.transitionTriggered = true;
                                callbackWhenDone();
                            }}
                        }};
                    }}
                    
                    function nextStep() {{
                        currentIndex = (currentIndex + 1) % playlist.length;
                        let nextUrl = playlist[currentIndex];
                        
                        // Configura o próximo vídeo em background
                        nextV.src = nextUrl;
                        nextV.load();
                        nextV.play().catch(e => {{}});
                        nextV.pause();
                        nextV.currentTime = 0;
                        nextV.transitionTriggered = false;
                        
                        // Inicia a reprodução do próximo e faz o crossfade trocando as classes
                        nextV.play();
                        nextV.classList.add('ativo');
                        activeV.classList.remove('ativo');
                        
                        // Troca os ponteiros
                        let temp = activeV;
                        activeV = nextV;
                        nextV = temp;
                        
                        // Prepara o próximo evento de transição para o novo vídeo ativo
                        activeV.ontimeupdate = function() {{
                            if (activeV.duration && (activeV.duration - activeV.currentTime <= 5) && !activeV.transitionTriggered) {{
                                activeV.transitionTriggered = true;
                                nextStep();
                            }}
                        }};
                    }}
                    
                    // Inicialização do primeiro vídeo
                    if (playlist.length > 0) {{
                        activeV.src = playlist[0];
                        activeV.classList.add('ativo');
                        activeV.play().catch(e => {{}});
                        activeV.ontimeupdate = function() {{
                            if (activeV.duration && (activeV.duration - activeV.currentTime <= 5) && !activeV.transitionTriggered) {{
                                activeV.transitionTriggered = true;
                                nextStep();
                            }}
                        }};
                    }}
                </script>
            """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum vídeo encontrado na pasta 'video_clipes'.")

    # Atualiza a página a cada 5 segundos para verificar novos pedidos no Firebase sem interromper a mini tela
    time.sleep(5)
    st.rerun()
