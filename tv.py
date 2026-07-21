import streamlit as st
import requests
import time
import cloudinary
import cloudinary.search
import random
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
        
        /* VÍDEO DE KARAOKE EM TELA TOTAL (100% W / 100% H) */
        .video-container { 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            background: black; display: flex; justify-content: center; align-items: center; z-index: 9999; 
        }
        .video-container video { 
            width: 100vw; height: 100vh; object-fit: contain; background: black; 
        }
        
        /* DIMENSÃO EXATA DO VÍDEO CLIPE: 430x306px */
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

# Função robusta para listar todos os vídeos da pasta "video_clipes"
def obter_todos_videos_da_pasta():
    urls = []
    try:
        search_result = cloudinary.search.Search()\
            .expression('folder=video_clipes AND resource_type:video')\
            .max_results(50)\
            .execute()
        
        lista = search_result.get('resources', [])
        if lista:
            urls = [item['secure_url'] for item in lista]
    except Exception as e:
        print("Erro na busca avançada Cloudinary:", e)
    
    if not urls:
        try:
            fallback = cloudinary.api.resources(type="upload", resource_type="video", max_results=50)
            geral = fallback.get('resources', [])
            if geral:
                urls = [item['secure_url'] for item in geral]
        except Exception as e:
            print("Erro no fallback Cloudinary:", e)
            
    return urls

# 1. EXIBIÇÃO DO VÍDEO DE KARAOKE EM TELA TOTAL
if comando == "play":
    if url_video:
        st.markdown(f"""
            <div class="video-container" id="container-video">
                <video id="karaoke-video" autoplay playsinline>
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta reprodução de vídeo.
                </video>
            </div>
            <script>
                const vid = document.getElementById('karaoke-video');
                let fechado = false;
                
                function fecharKaraoke() {{
                    if (fechado) return;
                    fechado = true;

                    fetch('{URL_STATUS}', {{
                        method: 'PATCH',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ comando: '', url_video: '', musica: '', cantor: '' }})
                    }}).finally(() => {{
                        window.location.reload();
                    }});
                }}

                vid.play().catch(error => {{
                    vid.muted = true;
                    vid.play();
                }});

                vid.onended = function() {{
                    fecharKaraoke();
                }};

                vid.ontimeupdate = function() {{
                    if (vid.duration && !isNaN(vid.duration)) {{
                        if (vid.currentTime >= (vid.duration - 0.4)) {{
                            fecharKaraoke();
                        }}
                    }}
                }}
            </script>
        """, unsafe_allow_html=True)

        while True:
            time.sleep(2)
            try:
                check_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
                if check_status.get("comando") != "play":
                    st.rerun()
            except:
                pass
    else:
        st.error("⚠️ Comando 'play' recebido, mas o link do vídeo está vazio.")
        time.sleep(3)
        requests.patch(URL_STATUS, json={"comando": ""})
        st.rerun()

# 2. CONTAGEM DECRESCENTE (3, 2, 1, 0)
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

# 3. TELA PRINCIPAL: FILA DE ESPERA E VÍDEOS CLIPES ALEATÓRIOS CONTÍNUOS
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
        
        lista_videos = obter_todos_videos_da_pasta()
        if lista_videos:
            random.shuffle(lista_videos)
            videos_json = json.dumps(lista_videos)
            
            st.markdown(f"""
                <div class="video-clipe-box" id="caixa-clipes">
                    <video id="vc-player-1" muted playsinline></video>
                    <video id="vc-player-2" muted playsinline></video>
                </div>
                
                <script>
                    const listaUrls = {videos_json};
                    let indiceAtual = 0;
                    
                    const v1 = document.getElementById('vc-player-1');
                    const v2 = document.getElementById('vc-player-2');
                    
                    function obterProximoUrl() {{
                        if (indiceAtual >= listaUrls.length) {{
                            indiceAtual = 0;
                            listaUrls.sort(() => Math.random() - 0.5);
                        }}
                        return listaUrls[indiceAtual++];
                    }}
                    
                    function iniciarPlayerClipe() {{
                        if (!listaUrls || listaUrls.length === 0) return;
                        
                        v1.src = obterProximoUrl();
                        v1.play().catch(e => console.log("Autoplay bloqueado:", e));
                        v1.classList.add('ativo');
                        
                        v2.src = obterProximoUrl();
                        
                        function configurarMonitor(videoAtivo, videoInativo) {{
                            videoAtivo.ontimeupdate = function() {{
                                if (videoAtivo.duration && !isNaN(videoAtivo.duration)) {{
                                    if ((videoAtivo.duration - videoAtivo.currentTime) <= 5 && !videoInativo.dataset.carregado) {{
                                        videoInativo.dataset.carregado = "true";
                                        videoInativo.src = obterProximoUrl();
                                        videoInativo.load();
                                        videoInativo.play().catch(e => {{}});
                                        
                                        setTimeout(() => {{
                                            videoInativo.classList.add('ativo');
                                            videoAtivo.classList.remove('ativo');
                                        }}, 500);
                                        
                                        setTimeout(() => {{
                                            videoAtivo.pause();
                                            videoAtivo.currentTime = 0;
                                            videoAtivo.dataset.carregado = "";
                                            configurarMonitor(videoInativo, videoAtivo);
                                        }}, 1200);
                                    }}
                                }}
                            }};
                        }}
                        
                        configurarMonitor(v1, v2);
                    }}
                    
                    if (!window.__clipeIniciado) {{
                        window.__clipeIniciado = true;
                        iniciarPlayerClipe();
                    }}
                    
                    setInterval(() => {{
                        fetch('{URL_STATUS}?nocache=' + Date.now())
                            .then(res => res.json())
                            .then(data => {{
                                if (data && data.comando && data.comando !== "") {{
                                    window.location.reload();
                                }}
                            }}).catch(err => {{}});
                    }}, 2500);
                </script>
            """, unsafe_allow_html=True)
        else:
            st.warning("A carregar vídeos do Cloudinary ou pasta vazia...")

    time.sleep(5)
    st.rerun()
