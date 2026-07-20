import streamlit as st
import requests
import time
import cloudinary
import cloudinary.search
import json

# Configuração Cloudinary
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; margin: 0; padding: 0; overflow: hidden; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        
        /* Karaoke em Tela Cheia Absoluta */
        .video-container { 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            background: black; display: flex; justify-content: center; align-items: center; z-index: 9999; 
        }
        .video-container video { width: 100vw; height: 100vh; object-fit: contain; background: black; }
        
        /* Moldura exata 430x306px para o Vídeo Clipe */
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
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            object-fit: fill;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        }
        .video-clipe-box video.ativo {
            opacity: 1;
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

# Função para obter a lista de vídeos da pasta "video_clipes" para a transição automática
def obter_lista_videos_clipes():
    try:
        search_result = cloudinary.search.Search()\
            .expression('folder=video_clipes AND resource_type:video')\
            .max_results(50)\
            .execute()
        
        lista = [r['secure_url'] for r in search_result.get('resources', [])]
        if lista:
            return lista
    except Exception as e:
        print("Erro na busca Cloudinary:", e)
    
    try:
        fallback = cloudinary.api.resources(type="upload", resource_type="video", max_results=50)
        return [r['secure_url'] for r in fallback.get('resources', [])]
    except:
        pass
        
    return []

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

                // Assim que o karaoke termina, limpa o estado no Firebase e recarrega para voltar à fila
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

# 2. CONTAGEM DECRESCENTE (3, 2, 1, 0) SÓ COMEÇA QUANDO O CLIENTE ESTÁ PRONTO NO PALCO
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:50px; color:white;'>
            <h1 style='font-size: 2.2rem; color: #00ff00;'>A CHAMAR AO PALCO:</h1>
            <h2 style='font-size: 3rem;' class="cantor-style">{str(res_status.get('cantor', '')).upper()}</h2>
            <h3 style='font-size: 1.8rem; color: yellow;'>{str(res_status.get('musica', '')).upper()}</h3>
            <hr style='width: 40%; margin: 15px auto; border-color: #444;'>
            <p style='font-size: 1.3rem; color: #ccc;'>A preparar o instrumental...</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Aguarda o carregamento técnico inicial do link do vídeo antes de iniciar a contagem para o cliente cantar
    time.sleep(1.5)
    
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    requests.patch(URL_STATUS, json={"comando": "play"})
    st.rerun()

# 3. TELA PRINCIPAL: FILA DE ESPERA E MINIATURA DE VÍDEOS CLI PES EM LOOP ALEATÓRIO
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
        
        lista_videos = obter_lista_videos_clipes()
        if lista_videos:
            # Passa a lista em formato JSON seguro para o script gerir a aleatoriedade e os 5 segundos finais
            lista_json = json.dumps(lista_videos)
            
            st.markdown(f"""
                <div class="video-clipe-box" id="box-clipe">
                    <!-- Dois elementos de vídeo internos para alternância cruzada sem cortes secos -->
                    <video id="vidA" autoplay muted playsinline class="ativo"></video>
                    <video id="vidB" autoplay muted playsinline></video>
                </div>
                <script>
                    const playlist = {lista_json};
                    let currentIndex = Math.floor(Math.random() * playlist.length);
                    
                    const vA = document.getElementById('vidA');
                    const vB = document.getElementById('vidB');
                    
                    let activeVid = vA;
                    let nextVid = vB;
                    let isTransitioning = false;

                    function getRandomVideoUrl(excludeUrl) {{
                        if (playlist.length <= 1) return playlist[0];
                        let rand;
                        do {{
                            rand = playlist[Math.floor(Math.random() * playlist.length)];
                        }} while (rand === excludeUrl);
                        return rand;
                    }}

                    // Inicializa o primeiro vídeo
                    activeVid.src = playlist[currentIndex];
                    activeVid.play().catch(e => console.log("Autoplay bloqueado:", e));

                    function setupVideoHandlers(videoElement) {{
                        videoElement.ontimeupdate = function() {{
                            // Quando faltarem 5 segundos para o fim, dispara a troca antecipada para o próximo vídeo
                            if (!isTransitioning && videoElement.duration && (videoElement.duration - videoElement.currentTime <= 5)) {{
                                isTransitioning = true;
                                triggerNextVideo();
                            }};
                        }};

                        videoElement.onended = function() {{
                            if (!isTransitioning) {{
                                triggerNextVideo();
                            }}
                        }};
                    }}

                    function triggerNextVideo() {{
                        let nextUrl = getRandomVideoUrl(activeVid.src);
                        nextVid.src = nextUrl;
                        nextVid.load();
                        nextVid.play().then(() => {{
                            // Alterna as classes CSS para transição suave de opacidade
                            nextVid.classList.add('ativo');
                            activeVid.classList.remove('ativo');
                            
                            // Troca as referências de elementos ativos
                            let temp = activeVid;
                            activeVid = nextVid;
                            nextVid = temp;
                            
                            isTransitioning = false;
                            setupVideoHandlers(activeVid);
                        }}).catch(e => {{
                            isTransitioning = false;
                        }});
                    }}

                    setupVideoHandlers(activeVid);
                </script>
            """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum vídeo encontrado na pasta 'video_clipes'.")

    # Atualiza a página a cada 10 segundos apenas para sincronizar alterações de novas senhas na Fila de Espera
    time.sleep(10)
    st.rerun()
