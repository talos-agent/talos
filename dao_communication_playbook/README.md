# Playbook de Comunicação da DAO e Verificação de Artefatos

![Verified](badge-verified-256-gpg.svg)

Este repositório contém o playbook de comunicação para as propostas de governança da DAO, bem como os scripts para verificar a integridade dos artefatos.

## Playbook de Comunicação (`communication_playbook.json`)

O arquivo `communication_playbook.json` é um recurso centralizado que contém todos os templates de copy para as campanhas de comunicação da DAO. Ele está estruturado por plataforma de mídia social e por estágio da campanha (anúncio, lembrete, última chamada, resultados).

Este arquivo foi projetado para ser "pronto para a máquina", permitindo que scripts de automação usem esses templates para gerar e postar conteúdo dinamicamente.

## Verificação de Integridade

Para garantir que os artefatos de comunicação não foram adulterados, você pode usar os scripts de verificação fornecidos.

### Para Linux/macOS:

```bash
./verify.sh
```

### Para Windows (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File verify.ps1
```

Esses scripts verificam o checksum SHA-256 do arquivo `communication_playbook.json` contra o valor armazenado em `SHA256SUMS`. No futuro, eles também incluirão a verificação de assinatura GPG para uma camada adicional de segurança.