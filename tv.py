import streamlit as st
import requests
import time
import cloudinary
import cloudinary.api
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
        .contador-box { font-size: 8rem; color: yellow; font-weight: bold; text-shadow: 0 0 20px red; text-align: center; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=3).json() or {}
except:
    res_status = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

@st.cache_data(ttl=120)
def obter_todos_videos_da_pasta():
    urls = []
    try:
        # Busca paginada ou ampla para capturar todos os ficheiros da pasta "video_clipes" no Cloudinary
        next_cursor = None
        while True:
            params_query = {"type": "upload", "resource_type": "video", "max_results": 500}
            if next_cursor:
                params_query["next_cursor"] = next_cursor
            
            result = cloudinary.api.resources(**params_query)
            geral = result.get('resources', [])
            
            for item in geral:
                public_id = item.get('public_id', '')
                secure_url = item.get('secure_url', '')
                # Filtra estritamente por ficheiros que estão dentro da pasta video_clipes
                if ('video_clipes/' in public_id or public_id.startswith('video_clipes')) and secure_url:
                    urls.append(secure_url)
            
            next_cursor = result.get('next_cursor')
            if not next_cursor:
                break
    except Exception as e:
        print("Erro ao buscar vídeos no Cloudinary:", e)
        
    # Fallback caso a busca direta com barra venha vazia por variação de nomenclatura na API
    if not urls:
        try:
            fallback = cloudinary.api.resources(type="upload", resource_type="video", max_results=100)
            for item in fallback.get('resources', []):
                public_id = item.get('public_id', '')
                secure_url = item.get('secure_url', '')
                if 'video_clipes' in public_id and secure_url:
                    urls.append(secure_url)
        except Exception as e2:
            print("Erro no fallback do Cloudinary:", e2)
            
    return urls

# 1. EXIBIÇÃO DO VÍDEO DE KARAOKE EM TELA TOTAL
if comando == "play":
    if url_video:
        st.markdown(f"""
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: black; display: flex; justify-content: center; align-items: center; z-index: 9999;">
                <video id="karaoke-video" autoplay playsinline style="width: 100vw; height: 100vh; object-fit: contain; background: black;">
                    <source src="{url_video}" type="video/mp4">
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
                    }}).finally(() => {{ window.location.reload(); }});
                }}
                vid.play().catch(error => {{ vid.muted = true; vid.play(); }});
                vid.onended = function() {{ fecharKaraoke(); }};
                vid.ontimeupdate = function() {{
                    if (vid.duration && !isNaN(vid.duration)) {{
                        if (vid.currentTime >= (vid.duration - 0.4)) {{ fecharKaraoke(); }}
                    }}
                }};
            </script>
        """, unsafe_allow_html=True)

        while True:
            time.sleep(1)
            try:
                check_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=3).json() or {}
                if check_status.get("comando") != "play":
                    st.rerun()
            except:
                pass
    else:
        st.error("⚠️ Comando 'play' recebido, mas o link do vídeo está vazio.")
        time.sleep(2)
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

# 3. TELA PRINCIPAL: FILA EM TEMPO REAL E VÍDEOS CLIPES COM CONTROLOS
else:
    cl1, cl2 = st.columns([1.2, 1.3])

    with cl1:
        st.markdown("<h1 style='color:gold; font-size: 2rem; margin-bottom: 10px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)
        
        st.markdown("""
            <div id="lista-fila-container" style="color: white; font-size: 1.2rem;">
                A carregar fila...
            </div>
            <script>
                function atualizarFilaRealTime() {
                    fetch('""" + URL_PEDIDOS + """?nocache=' + Date.now())
                        .then(res => res.json())
                        .then(data => {
                            const container = document.getElementById('lista-fila-container');
                            if (!data) {
                                container.innerHTML = "<div style='color: #aaa;'>A fila está vazia. Envie músicas pelo telemóvel!</div>";
                                return;
                            }
                            let html = "";
                            let contador = 1;
                            for (const [p_id, p] of Object.entries(data)) {
                                if (p.musica && !p.musica.startsWith("PEDIDO:")) {
                                    html += `<div style="margin: 8px 0;"><b>${contador}.</b> <span style="color:white; font-weight:bold;">${p.cantor.toUpperCase()}</span> ➔ <span style="color:yellow; font-weight:bold;">${p.musica.toUpperCase()}</span></div>`;
                                    contador++;
                                }
                            }
                            if (contador === 1) {
                                container.innerHTML = "<div style='color: #aaa;'>Ainda sem cantores na fila.</div>";
                            } else {
                                container.innerHTML = html;
                            }
                        }).catch(err => {});
                }
                atualizarFilaRealTime();
                setInterval(atualizarFilaRealTime, 1500);
            </script>
        """, unsafe_allow_html=True)

    with cl2:
        st.markdown("<h2 style='color:gold; font-size: 1.5rem; margin-bottom: 10px;'>📺 VÍDEOS EM DESTAQUE</h2>", unsafe_allow_html=True)
        
        lista_videos = obter_todos_videos_da_pasta()
        if not lista_videos:
            lista_videos = ["https://res.cloudinary.com/yhwgjh7g/video/upload/v1/video_clipes/amostra.mp4"]
        
        # Embaralha os vídeos para garantir variedade na reprodução
        random.shuffle(lista_videos)
        videos_json = json.dumps(lista_videos)
        
        html_player = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ background: black; margin: 0; padding: 0; overflow: hidden; font-family: sans-serif; }}
                .video-clipe-box {{ 
                    width: 100%; 
                    max-width: 650px;
                    height: 380px;
                    background: black; 
                    border-radius: 8px; 
                    border: 2px solid #ffd700; 
                    overflow: hidden;
                    position: relative;
                    box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
                }}
                .video-clipe-box video {{
                    position: absolute;
                    top: 0; left: 0;
                    width: 100%; height: 100%;
                    object-fit: cover;
                    opacity: 0;
                    transition: opacity 1s ease-in-out;
                }}
                .video-clipe-box video.ativo {{
                    opacity: 1;
                    z-index: 2;
                }}
                .video-controls-overlay {{
                    position: absolute;
                    bottom: 0; left: 0;
                    width: 100%;
                    background: linear-gradient(transparent, rgba(0,0,0,0.85));
                    z-index: 10;
                    padding: 10px 15px;
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                    opacity: 0.2;
                    transition: opacity 0.3s ease;
                }}
                .video-clipe-box:hover .video-controls-overlay {{
                    opacity: 1;
                }}
                .progress-bar-container {{
                    width: 100%;
                    height: 6px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 3px;
                    cursor: pointer;
                    position: relative;
                }}
                .progress-bar-fill {{
                    height: 100%;
                    background: #ffd700;
                    border-radius: 3px;
                    width: 0%;
                }}
                .controls-buttons {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .btn-ctrl {{
                    background: rgba(0, 0, 0, 0.6);
                    border: 1px solid #ffd700;
                    color: #ffd700;
                    padding: 4px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.85rem;
                    font-weight: bold;
                }}
                .btn-ctrl:hover {{
                    background: #ffd700;
                    color: black;
                }}
            </style>
        </head>
        <body>
            <div class="video-clipe-box" id="caixa-clipes">
                <video id="vc-player-1" muted playsinline></video>
                <video id="vc-player-2" muted playsinline></video>
                
                <div class="video-controls-overlay">
                    <div class="progress-bar-container" id="progress-container">
                        <div class="progress-bar-fill" id="progress-fill"></div>
                    </div>
                    <div class="controls-buttons">
                        <div>
                            <button class="btn-ctrl" id="btn-play-pause">⏸ Pausa</button>
                            <button class="btn-ctrl" id="btn-sound">🔇 Som</button>
                        </div>
                        <div id="video-timer" style="color: white; font-size: 0.8rem; font-weight: bold;">00:00 / 00:00</div>
                    </div>
                </div>
            </div>
            
            <script>
                const listaUrls = {videos_json};
                let indiceAtual = 0;
                
                const v1 = document.getElementById('vc-player-1');
                const v2 = document.getElementById('vc-player-2');
                const btnPlayPause = document.getElementById('btn-play-pause');
                const btnSound = document.getElementById('btn-sound');
                const progressFill = document.getElementById('progress-fill');
                const progressContainer = document.getElementById('progress-container');
                const videoTimer = document.getElementById('video-timer');
                
                let ativoAtual = v1;
                
                function obterProximoUrl() {{
                    if (indiceAtual >= listaUrls.length) {{
                        indiceAtual = 0;
                        listaUrls.sort(() => Math.random() - 0.5);
                    }}
                    return listaUrls[indiceAtual++];
                }}
                
                function formatarTempo(segundos) {{
                    let m = Math.floor(segundos / 60);
                    let s = Math.floor(segundos % 60);
                    return (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                }}
                
                function iniciarPlayerClipe() {{
                    if (!listaUrls || listaUrls.length === 0) return;
                    
                    v1.src = obterProximoUrl();
                    v1.load();
                    v1.muted = true;
                    v1.play().then(() => {{
                        v1.classList.add('ativo');
                    }}).catch(e => {{
                        v1.play();
                        v1.classList.add('ativo');
                    }});
                    
                    v2.src = obterProximoUrl();
                    v2.load();
                    
                    function configurarMonitor(videoAtivo, videoInativo) {{
                        ativoAtual = videoAtivo;
                        
                        videoAtivo.ontimeupdate = function() {{
                            if (videoAtivo === ativoAtual && videoAtivo.duration && !isNaN(videoAtivo.duration)) {{
                                let progresso = (videoAtivo.currentTime / videoAtivo.duration) * 100;
                                progressFill.style.width = progresso + "%";
                                videoTimer.innerText = formatarTempo(videoAtivo.currentTime) + " / " + formatarTempo(videoAtivo.duration);
                                
                                if ((videoAtivo.duration - videoAtivo.currentTime) <= 4 && !videoInativo.dataset.carregado) {{
                                    videoInativo.dataset.carregado = "true";
                                    videoInativo.src = obterProximoUrl();
                                    videoInativo.load();
                                    videoInativo.muted = videoAtivo.muted;
                                    videoInativo.play().catch(e => {{}});
                                    
                                    setTimeout(() => {{
                                        videoInativo.classList.add('ativo');
                                        videoAtivo.classList.remove('ativo');
                                    }}, 600);
                                    
                                    setTimeout(() => {{
                                        videoAtivo.pause();
                                        videoAtivo.currentTime = 0;
                                        videoAtivo.dataset.carregado = "";
                                        configurarMonitor(videoInativo, videoInativo === v1 ? v2 : v1);
                                    }}, 1400);
                                }}
                            }}
                        }};
                    }}
                    
                    configurarMonitor(v1, v2);
                }}
                
                btnPlayPause.onclick = function() {{
                    if (ativoAtual.paused) {{
                        ativoAtual.play();
                        btnPlayPause.innerText = "⏸ Pausa";
                    }} else {{
                        ativoAtual.pause();
                        btnPlayPause.innerText = "▶ Play";
                    }}
                }};
                
                btnSound.onclick = function() {{
                    if (ativoAtual.muted) {{
                        ativoAtual.muted = false;
                        v1.muted = false;
                        v2.muted = false;
                        btnSound.innerText = "🔊 Som";
                    }} else {{
                        ativoAtual.muted = true;
                        v1.muted = true;
                        v2.muted = true;
                        btnSound.innerText = "🔇 Mudo";
                    }}
                }};
                
                progressContainer.onclick = function(e) {{
                    let rect = progressContainer.getBoundingClientRect();
                    let posClick = (e.clientX - rect.left) / rect.width;
                    if (ativoAtual.duration) {{
                        ativoAtual.currentTime = posClick * ativoAtual.duration;
                    }}
                }};
                
                setTimeout(iniciarPlayerClipe, 200);
                
                setInterval(() => {{
                    fetch('{URL_STATUS}?nocache=' + Date.now())
                        .then(res => res.json())
                        .then(data => {{
                            if (data && data.comando && data.comando !== "") {{
                                window.parent.location.reload();
                            }}
                        }}).catch(err => {{}});
                }}, 1000);
            </script>
        </body>
        </html>
        """
        
        st.components.v1.html(html_player, height=400)
