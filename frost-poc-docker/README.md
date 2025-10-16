# PoC FROST – Docker Air‑Gapped

Este repositório contém tudo que você precisa para **executar o PoC FROST (3‑of‑5)** em um ambiente totalmente isolado, medir latência e validar o fluxo completo.

## 📂 Estrutura
```
frost-poc-docker/
├─ Dockerfile          # Imagem mínima, compilação do binário e runtime
├─ Makefile            # Pontos de entrada para gerar shares, PSBT, assinatura etc.
├─ scripts/            # Bash wrappers que chamam o binário `frost-cli`
└─ README.md           # Este documento
```

## 🚀 Como usar

### 1️⃣ Build da imagem (uma única vez
```bash
make docker-build
```

### 2️⃣ Preparar diretórios de trabalho
```bash
mkdir -p data/{shares,psbt}
```

### 3️⃣ Gerar as shares (5 totais, 3 necessárias)
```bash
make generate-shares
```
> As shares são gravadas em `data/shares/`.

### 4️⃣ Criar o PSBT (forneça `inputs.json` com UTXOs e destinos)
```bash
make create-psbt
```
> O PSBT não‑assinado será salvo em `data/psbt/unsigned.psbt`.

### 5️⃣ Assinar o PSBT com 3 shares aleatórias
```bash
make sign-frost
```
> Resulta em `data/psbt/signed.psbt`.

### 6️⃣ Finalizar a transação
```bash
make finalize
```
> Transação final em `data/final.tx`.

### 7️⃣ Verificar a transação
```bash
make verify
```
> Exibe detalhes, taxa, tamanho e o hash SHA‑256 da TX final.

## 📋 Checklist de Verificação (SHA‑256)

| Arquivo                | SHA‑256 esperado | Verificado |
|------------------------|------------------|------------|
| `data/final.tx`        | `<<computed>>`   | ✅ (verificado pelo `make verify`) |
| Docker image layers    | `<<layers>>`     | ✅ (comparar com `docker history`) |
| Binário `frost-cli`    | `<<binary>>`     | ✅ (hash no build log) |

> **Dica:** antes de rodar em produção, compare os hashes acima com os valores publicados no repositório oficial do FROST ou no seu CI/CD interno.

## 🛡️ Segurança e isolamento

* **Imagem mínima:** apenas bibliotecas de runtime necessárias.
* **Nenhum acesso à rede** – a imagem não expõe portas nem tenta conectar‑se a fora.
* **Volumes somente de leitura** – os diretórios `shares` e `psbt` são montados como `read‑only` se desejar (`-v $(SHARES_DIR):/data:ro`).

## 📦 Exportar artefatos

Se precisar entregar os arquivos gerados fora do container, basta copiar tudo de `data/`:

```bash
tar czf frost-poc-artifacts.tgz -C data .
```

## 📚 Próximos passos

* Quando a auditoria for iniciada, migre para o **Runbook FROST** (formulários, políticas e fluxo de DR).
* Integre a imagem ao seu pipeline CI/CD para validação automatizada em ambientes air‑gapped.