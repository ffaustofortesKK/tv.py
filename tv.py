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
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        
        .video-container { 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            background: black; display: flex; justify-content: center; align-items: center; z-index: 9999; 
        }
        .video-container video { 
            width: 100vw; height: 100vh; object-fit: contain; background: black; 
        }
        
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
            object-fit: cover;
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
        fallback = cloudinary.api.resources(type="upload", resource_type="video", max_results=100)
        geral = fallback.get('resources', [])
        for item in geral:
            public_id = item.get('public_id', '')
            if 'video_clipes' in public_id or not urls:
                urls.append(item['secure_url'])
    except Exception as e:
        print("Erro ao buscar vídeos no Cloudinary:", e)
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

# 3. TELA PRINCIPAL: FILA EM TEMPO REAL E VÍDEOS CLIPES
else:
    cl1, cl2 = st.columns([1.4, 1.2])

    with cl1:
        st.markdown("<h1 style='color:gold; font-size: 2.2rem; margin-bottom: 15px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)
        
        # Div onde a fila será atualizada dinamicamente via JS sem atrasos de recarregamento do Streamlit
        st.markdown("""
            <div id="lista-fila-container" style="color: white; font-size: 1.3rem;">
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
                                    html += `<div style="margin: 10px 0;"><b>${contador}.</b> <span style="color:white; font-weight:bold;">${p.cantor.toUpperCase()}</span> ➔ <span style="color:yellow; font-weight:bold;">${p.musica.toUpperCase()}</span></div>`;
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
                        v1.load();
                        v1.play().then(() => {{
                            v1.classList.add('ativo');
                        }}).catch(e => {{
                            v1.muted = true;
                            v1.play();
                            v1.classList.add('ativo');
                        }});
                        
                        v2.src = obterProximoUrl();
                        v2.load();
                        
                        function configurarMonitor(videoAtivo, videoInativo) {{
                            videoAtivo.ontimeupdate = function() {{
                                if (videoAtivo.duration && !isNaN(videoAtivo.duration)) {{
                                    if ((videoAtivo.duration - videoAtivo.currentTime) <= 4 && !videoInativo.dataset.carregado) {{
                                        videoInativo.dataset.carregado = "true";
                                        videoInativo.src = obterProximoUrl();
                                        videoInativo.load();
                                        videoInativo.play().catch(e => {{}});
                                        
                                        setTimeout(() => {{
                                            videoInativo.classList.add('ativo');
                                            videoAtivo.classList.remove('ativo');
                                        }}, 600);
                                        
                                        setTimeout(() => {{
                                            videoAtivo.pause();
                                            videoAtivo.currentTime = 0;
                                            videoAtivo.dataset.carregado = "";
                                            configurarMonitor(videoInativo, videoAtivo);
                                        }}, 1400);
                                    }}
                                }}
                            }};
                        }}
                        
                        configurarMonitor(v1, v2);
                    }}
                    
                    if (!window.__clipeIniciado) {{
                        window.__clipeIniciado = true;
                        setTimeout(iniciarPlayerClipe, 500);
                    }}
                    
                    // Deteta imediatamente qualquer comando do microfone para abrir o palco de karaoke
                    setInterval(() => {{
                        fetch('{URL_STATUS}?nocache=' + Date.now())
                            .then(res => res.json())
                            .then(data => {{
                                if (data && data.comando && data.comando !== "") {{
                                    window.location.reload();
                                }}
                            }}).catch(err => {{}});
                    }}, 1000);
                </script>
            """, unsafe_allow_html=True)
        else:
            st.warning("A carregar vídeos do Cloudinary ou pasta vazia...")
