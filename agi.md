## Como “sync‑ar” (re‑transmitir) ao vivo o canal **Twitch** de **`rafael_null`**  

Abaixo está um guia completo – do **acesso à API** até a **re‑transmissão** usando ferramentas open‑source (OBS Studio + FFmpeg / Streamlink) – que você pode rodar em qualquer máquina (desktop, VM ou servidor) que tenha acesso à internet.  
Todo o fluxo pode ser orquestrado via **scripts** e, se quiser, integrado ao **Protocolo $Z(n)** usando a camada de comunicação *Lattica* para anunciar o início/fim da retransmissão.

> **⚠️ Aviso legal**  
> Re‑transmitir conteúdo de terceiros só é permitido quando o proprietário do canal concedeu permissão explícita (ex.: parceria, acordo de *rebroadcast* ou licença Creative‑Commons). Certifique‑se de ter a autorização de **`rafael_null`** antes de colocar o stream em público.

---

## 1️⃣ Obter credenciais da Twitch API  

Para consultar o estado da transmissão (online/offline) e obter a URL de ingestão, você precisará de um **Client ID** e **Client Secret**.

| Passo | O que fazer |
|------|-------------|
| **A.** Crie um aplicativo em <https://dev.twitch.tv/console/apps> | • Nome: *ex.: `sync‑rafael‑null`*<br>• OAuth Redirect URL: `http://localhost` (ou outro que você usar)<br>• Categorias: `Chat Bot` (não importa) |
| **B.** Copie o **Client ID** e **Client Secret**. |
| **C.** Troque o *client secret* por um **Access Token** (OAuth Client‑Credentials). Use o seguinte *curl* (substitua `<client_id>` e `<client_secret>`): |

```bash
curl -X POST 'https://id.twitch.tv/oauth2/token' \
  -d 'client_id=<client_id>' \
  -d 'client_secret=<client_secret>' \
  -d 'grant_type=client_credentials'
```

A resposta será algo como:

```json
{
  "access_token": "eyJhbGciOi...",
  "expires_in": 5270400,
  "token_type": "bearer"
}
```

Guarde o **access_token** (válido ~60 dias).

---

## 2️⃣ Verificar se o canal está ao vivo  

Endpoint: `https://api.twitch.tv/helix/streams?user_login=rafael_null`

```bash
curl -H "Client-ID: <client_id>" \
     -H "Authorization: Bearer <access_token>" \
     "https://api.twitch.tv/helix/streams?user_login=rafael_null"
```

- **Resposta com `data: []`** → o canal está offline.  
- **Resposta com um objeto dentro de `data`** → está online; o campo `type` será `"live"` e `started_at` indica o horário de início.

> **Automatização:** Crie um pequeno script (bash, python ou node) que faça polling a cada 30 s e dispare a ação de captura assim que o stream aparecer.

---

## 3️⃣ Capturar o fluxo ao vivo  

Existem duas abordagens comuns:

### 3.1 Usando **Streamlink** (mais simples)  

```bash
# Instalação (Linux/macOS)
pip install streamlink   # ou: brew install streamlink / apt-get install streamlink

# Comando de captura → pipe para FFmpeg (re‑encode ou repack)
streamlink "twitch.tv/rafael_null" best -O | \
ffmpeg -i - -c:v copy -c:a aac -b:a 128k -f flv rtmp://<seu-ingest>/live/streamkey
```

- `-O` faz o Streamlink escrever o fluxo **para stdout**.  
- O `ffmpeg` lê da *pipe* (`-i -`) e envia para seu servidor de ingestão (RTMP, SRT, etc.) usando **copy** (sem recodificação) para o vídeo e **AAC** para o áudio.

### 3.2 Usando **FFmpeg** direto (via HLS)  

Twitch disponibiliza HLS (`.m3u8`). Você pode apontar o FFmpeg diretamente:

```bash
ffmpeg -re -i "https://usher.ttvnw.net/api/channel/hls/rafael_null.m3u8?allow_source=true&player=twitchweb&sig=<sig>&token=<token>" \
       -c copy -f flv rtmp://<seu-ingest>/live/streamkey
```

> **Como conseguir `sig` e `token`?**  
> Eles são parte da URL que o próprio Twitch entrega ao navegador. Uma maneira prática é abrir o stream no navegador, abrir *Network* nas DevTools, filtrar por `*.m3u8` e copiar a URL completa. Para automação, o **Streamlink** já resolve isso por você.

---

## 4️⃣ Seu ponto de ingestão (onde o fluxo será enviado)

| Opção | Descrição | Como criar |
|------|-----------|------------|
| **RTMP (YouTube, Twitch, custom)** | O padrão mais usado. Precisa de URL `rtmp://...` + *stream key*. | - YouTube Live: `rtmp://a.rtmp.youtube.com/live2` + sua chave.<br>- Twitch (para *re‑broadcast*): `rtmp://live.twitch.tv/app` + chave da sua conta. |
| **SRT** | Mais resiliente a perdas, ideal para servidores próprios. | Use um servidor como **Wowza**, **NGINX‑RTMP**, ou **Haivision** e configure `srt://host:port?streamid=...`. |
| **LLHLS / WebRTC** | Para entrega direta a navegadores via Lattica/Parallax. | Precisa de um *origin server* que converta RTMP → LLHLS (ex.: **media‑server** do projeto **Livepeer**) e depois exponha via **Lattica**. |

> **Dica:** Se quiser que o stream fique **disponível no seu próprio domínio** (ex.: `live.seusite.com/rafael_null`), configure um **NGINX‑RTMP** como ingestão e habilite o módulo HLS para servir arquivos `.m3u8` que podem ser reproduzidos em qualquer player HTML5.

---

## 5️⃣ Automatizar o ciclo completo (script Bash)

```bash
#!/usr/bin/env bash
# ---------------------------------------------------------
# sync‑live‑twitch.sh  –  re‑transmite rafael_null ao vivo
# ---------------------------------------------------------

# ==== CONFIGURAÇÃO ==================================================
CLIENT_ID="<seu_client_id>"
CLIENT_SECRET="<seu_client_secret>"
CHANNEL="rafael_null"

# URL do seu ponto de ingestão (RTMP) + stream key
INGEST_URL="rtmp://live.seusite.com/app"
STREAM_KEY="seustreamkey123"

# Intervalo de polling (segundos)
POLL_INTERVAL=30
# ====================================================================

# 1️⃣ Obter access token (client‑credentials)
TOKEN=$(curl -s -X POST "https://id.twitch.tv/oauth2/token \
  ?client_id=${CLIENT_ID} \
  &client_secret=${CLIENT_SECRET} \
  &grant_type=client_credentials" | jq -r .access_token)

# Função que checa se o canal está ao vivo
is_live() {
  curl -s -H "Client-ID: ${CLIENT_ID}" \
       -H "Authorization: Bearer ${TOKEN}" \
       "https://api.twitch.tv/helix/streams?user_login=${CHANNEL}" |
    jq -e '.data | length > 0'
}

# Loop de polling -------------------------------------------------
while true; do
  if is_live; then
    echo "[$(date)] → ${CHANNEL} está AO VIVO! Iniciando captura…"

    # 2️⃣ Captura com Streamlink → pipe para FFmpeg
    streamlink "https://twitch.tv/${CHANNEL}" best -O |
      ffmpeg -re -i - -c copy -f flv "${INGEST_URL}/${STREAM_KEY}"

    # Quando o stream terminar, o FFmpeg sai e o loop reinicia.
    echo "[$(date)] ← Captura finalizada. Esperando nova transmissão…"
  else
    echo "[$(date)] → ${CHANNEL} OFFLINE. Aguardando ${POLL_INTERVAL}s…"
  fi
  sleep ${POLL_INTERVAL}
done
```

- **Dependências:** `curl`, `jq`, `streamlink`, `ffmpeg`.  
- **Comportamento:** Quando o canal fica online, o script inicia a captura; ao terminar (ou cair), volta a ficar em espera.

> **Integrar ao Parallax/Lattica:**  
> Dentro do bloco `if is_live; then …` você pode inserir um envio de mensagem Lattica, por exemplo:

```bash
lattica send --channel ritual \
   --msg "Ritual de sync iniciado: rafael_null ao vivo (Sincronia Impossível ativada)."
```

---

## 6️⃣ Exibir o stream re‑transmitido  

### 6.1 Player HTML5 (HLS)

Se o seu servidor converte RTMP → HLS (NGINX‑RTMP ou outro), basta usar:

```html
<video id="livePlayer" controls autoplay playsinline muted
       src="https://live.seusite.com/hls/rafael_null.m3u8"
       type="application/vnd.apple.mpegurl">
  Seu navegador não suporta reprodução de streams ao vivo.
</video>
```

### 6.2 Player embutido via **iframe** (YouTube/Twitch)

Caso tenha escolhido re‑broadcast para outra conta Twitch ou YouTube, pode usar os players nativos:

```html
<!-- Twitch embed -->
<div id="twitch-embed"></div>
<script src="https://embed.twitch.tv/embed/v1.js"></script>
<script>
  new Twitch.Embed("twitch-embed", {
    channel: "seu_canal_rebroadcast",
    width: "100%",
    height: "480",
    autoplay: true
  });
</script>
```

---

## 7️⃣ Monitoramento & Logs (opcional)

- **Prometheus + Grafana**: exponha métricas do FFmpeg (`-progress pipe:1`) para observar bitrate, frames dropped, etc.  
- **Alertas Lattica**: envie mensagens de “offline”, “erro de ingestão”, etc., para um canal de monitoramento.

```bash
ffmpeg -re -i - -c copy -f flv "${INGEST_URL}/${STREAM_KEY}" \
  -progress pipe:1 2>&1 | while read line; do
    if [[ $line == *"frame="* ]]; then
      echo "[ffmpeg] $line"
    elif [[ $line == *"error"* ]]; then
      lattica send --channel alerts --msg "⚠️ FFmpeg error: $line"
    fi
  done
```

---

## 📌 Resumo rápido (passo a passo)

1. **Crie app na Twitch → obtenha Client ID/Secret.**  
2. **Troque por Access Token** (OAuth Client‑Credentials).  
3. **Poll API** (`/helix/streams`) para detectar quando `rafael_null` está ao vivo.  
4. **Capture** com **Streamlink** (ou FFmpeg direto) → **pipe** para **FFmpeg**.  
5. **Re‑encode ou copy** e **envie** ao seu ponto de ingestão (RTMP/SRT/LLHLS).  
6. **Opcional:** notifique via **Lattica** que o ritual de sync começou/terminou.  
7. **Distribua** o stream re‑transmitido em sua plataforma (HTML5 player, embed Twitch/YouTube, etc.).  

Com esse pipeline, seu “ritual de **Sincronia Impossível**” está completo: você captura o fluxo ao vivo de `rafael_null`, o re‑transmite sob seu próprio ponto de ingestão e, ao mesmo tempo, anuncia a ação na rede **Parallax/Lattica**, permitindo que a comunidade siga o evento em tempo real.

> **Próximos passos**  
> - Integrar o script ao **Parallax** como um *service node* que roda 24 h e publica seu estado via Lattica.  
> - Criar um **evento de “Dia da Fundação”** que, ao iniciar o sync, dispare efeitos visuais (metáforas visuais) em um dashboard coletivo.  

Qualquer dúvida sobre algum dos passos (ex.: configuração NGINX‑RTMP, criação de token Lattica ou ajustes de bitrate) é só chamar! 🚀
