# AO Research Controller – versão 1.0.0

## Objetivo
Fornecer um **framework de pesquisa reproduzível** para controle adaptativo
baseado em Lyapunov e publicar os resultados de maneira **imutável** no IPFS,
de forma que o artigo possa citar o CID e garantir que os dados não serão
alterados.

## Como usar

### 1. Preparar o ambiente
```bash
git clone <seu-repo>
cd ao_research_controller
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Instalar e iniciar o IPFS
```bash
# Ubuntu/Debian
wget https://dist.ipfs.io/go-ipfs/v0.18.1/go-ipfs_v0.18.1_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.18.1_linux-amd64.tar.gz
sudo mv go-ipfs/ipfs /usr/local/bin/
ipfs init
ipfs daemon   # mantenha esse terminal aberto
```

> O daemon escuta em `127.0.0.1:5001`, que é onde o código Python conecta.

### 3. Iniciar a interface web
```bash
python web_interface.py
```
Acesse `http://localhost:5000` no navegador.
- **Iniciar experimento** → gera a simulação, salva CSV + JSON e faz *pin* no IPFS.
- O JSON de resposta contém:
  ```json
  {
    "status": "completed",
    "cid": "<CID-do-conjunto>",
    "gateway_url": "https://ipfs.io/ipfs/<CID>",
    "config": { ... }
  }
  ```

### 4. Citar no paper
Use o CID retornado (`<CID-do-conjunto>`) como referência permanente:
```
Dataset de experimentos: https://ipfs.io/ipfs/<CID-do-conjunto>
```
Qualquer leitor pode baixar o CSV e verificar a reproducibilidade usando a mesma semente (`rng_seed = 42`) e a mesma configuração (armazenada no `metadata.json`).

## Extensões (opcional)

* **Parametrizar via URL** – adicione `?duration=10&gamma=30` e modifique `TrialConfig(**request.args)` dentro de `web_interface.run`.
* **Plotagem automática** – inclua `matplotlib` e retorne imagens PNG no endpoint `/plot`.
* **Armazenar múltiplas execuções** – crie uma pasta `runs/<timestamp>` e faça upload de cada sub‑diretório individualmente.

## Licença
MIT – livre para uso acadêmico e comercial, desde que a atribuição seja mantida.

---

**Pronto!** Você tem agora um controlador adaptativo de pesquisa, um pequeno front‑end para disparar experimentos e um mecanismo de publicação imutável no IPFS, tudo em um único repositório pequeno e **sem** “scope creep”. Boa pesquisa e boa publicação! 🚀