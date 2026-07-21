import streamlit as st
import requests
import time
import cloudinary
import cloudinary.search

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
            background: black; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 99999; 
        }
        
        .custom-controls {
            position: absolute;
            bottom: 25px;
            width: 90%;
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #ffd700;
            padding: 12px 20px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 15px;
            z-index: 2147483647;
            box-shadow: 0 4px 20px rgba(0,0,0,0.9);
            pointer-events: auto;
        }
        .custom-controls button {
            background: #ffd700;
            border: none;
            color: black;
            font-weight: bold;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.1rem;
        }
        .custom-controls button:hover {
            background: #ffc700;
        }
        .custom-controls input[type=range] {
            cursor: pointer;
            accent-color: #ffd700;
        }
        .time-display {
            color: white;
            font-family: monospace;
            font-size: 1.1rem;
            min-width: 120px;
            text-align: center;
        }
        
        .video-clipe-box { 
            width: 430px; 
            height: 306px;
            background: black; 
            padding: 0px; 
            border-radius: 4px; 
            border: 2px solid #ffd700; 
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .video-clipe-box video {
            width: 100%;
            height: 100%;
            object-fit: fill; 
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

# 1. EXIBIÇÃO DO VÍDEO DE KARAOKE EM TELA CHEIA COM CONTROLES COMPLETOS
if comando == "play":
    if url_video:
        html_code = f"""
            <div class="video-container" id="container-video">
                <video id="karaoke-video" playsinline style="width: 100%; height: 100%; object-fit: contain;">
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta reprodução de vídeo.
                </video>
                
                <div class="custom-controls" id="controls-bar">
                    <button id="btn-play-pause" onclick="togglePlayPause()">⏸️ Pausa</button>
                    <span id="current-time" class="time-display">00:00 / 00:00</span>
                    <input type="range" id="seek-bar" value="0" min="0" max="100" step="0.1" style="flex-grow: 1;" oninput="mudarProgresso(this.value)">
                    <span style="color: white; font-weight: bold;">🔊 Som</span>
                    <input type="range" id="volume-bar" min="0" max="1" step="0.05" value="1" style="width: 120px;" oninput="mudarVolume(this.value)">
                    <button onclick="proximaMusicaForçada()" style="background: #ff4444; color: white;">⏭️ Avançar</button>
                </div>
            </div>
            
            <script>
                const vid = document.getElementById('karaoke-video');
                const seekBar = document.getElementById('seek-bar');
                const volumeBar = document.getElementById('volume-bar');
                const timeDisplay = document.getElementById('current-time');
                const btnPlayPause = document.getElementById('btn-play-pause');

                vid.muted = false;
                vid.volume = 1.0;
                
                vid.play().catch(function(error) {{
                    vid.muted = true;
                    vid.play().then(() => {{
                        vid.muted = false;
                        volumeBar.value = 1;
                    }});
                }});

                function formatarTempo(segundos) {{
                    let m = Math.floor(segundos / 60);
                    let s = Math.floor(segundos % 60);
                    return (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                }

                vid.ontimeupdate = function() {{
                    if (vid.duration) {{
                        let progressoPercentual = (vid.currentTime / vid.duration) * 100;
                        seekBar.value = progressoPercentual;
                        timeDisplay.innerText = formatarTempo(vid.currentTime) + " / " + formatarTempo(vid.duration);
                    }}
                }};

                function togglePlayPause() {{
                    if (vid.paused) {{
                        vid.play();
                        btnPlayPause.innerText = "⏸️ Pausa";
                    }} else {{
                        vid.pause();
                        btnPlayPause.innerText = "▶️ Play";
                    }}
                }}

                function mudarProgresso(valor) {{
                    if (vid.duration) {{
                        let tempoNovo = (valor * vid.duration) / 100;
                        vid.currentTime = tempoNovo;
                    }}
                }}

                function mudarVolume(valor) {{
                    vid.volume = parseFloat(valor);
                    vid.muted = (vid.volume === 0);
                }}

                function proximaMusicaForçada() {{
                    fetch('{URL_STATUS}', {{
                        method: 'PATCH',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ comando: 'fim', url_video: '', musica: '', cantor: '' }})
                    }}).then(function() {{
                        window.location.reload();
                    }});
                }}

                vid.onended = function() {{
                    proximaMusicaForçada();
                }};
            </script>
        """
        st.markdown(html_code, unsafe_allow_html=True)

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
    
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    requests.patch(URL_STATUS, json={"comando": "play"})
    st.rerun()

# 3. TELA PRINCIPAL: FILA DE ESPERA À ESQUERDA E VÍDEO CLIPE DE FUNDO
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
        st.markdown("<h1 style='color:gold; font-size: 1.8rem; margin-bottom: 5px;'>📺 VÍDEO CLIPE (FUNDO)</h1>", unsafe_allow_html=True)
        
        url_clipe = res_status.get("url_video")
        nome_clipe_atual = res_status.get("musica")

        if url_clipe and nome_clipe_atual and res_status.get("cantor") == "VÍDEO CLIPE":
            st.markdown(f"<p style='color: #00ff00; font-weight: bold; margin-bottom: 5px;'>▶️ Reproduzindo: {nome_clipe_atual}</p>", unsafe_allow_html=True)
            video_id_unico = f"vid_{abs(hash(url_clipe))}"
            st.markdown(f"""
                <div class="video-clipe-box">
                    <video id="p-{video_id_unico}" autoplay muted loop playsinline>
                        <source src="{url_clipe}" type="video/mp4">
                        Seu navegador não suporta vídeo.
                    </video>
                </div>
                <script>
                    const vElement = document.getElementById('p-{video_id_unico}');
                    if (vElement) {{
                        vElement.currentTime = 0;
                        vElement.play().catch(function(e) {{ console.log("Autoplay bloqueado:", e); }});
                    }}
                </script>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="video-clipe-box" style="display: flex; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px;">
                    <p style="margin: 0; font-size: 1rem;">Aguardando o prestador selecionar um vídeo clipe no painel de controle...</p>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(3)
    st.rerun()
