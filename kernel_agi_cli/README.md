# Kernel AGI - Chat de Console Interativo

Esta é uma ferramenta de linha de comando (CLI) para interagir com a API da OpenRouter. Ela oferece uma experiência de chat rica em recursos, diretamente do seu terminal, incluindo:

-   **Streaming de Respostas:** Veja a resposta do modelo sendo "digitada" em tempo real.
-   **Histórico de Conversa:** Salve e carregue sessões de chat para continuar de onde parou.
-   **Comandos Especiais:** Mude de modelo, limpe o histórico, veja informações da sessão e muito mais, sem sair da interface.
-   **Métricas de Performance:** Monitore o uso de tokens, a latência e o custo estimado de cada chamada.
-   **Interface Colorida:** Saída formatada e fácil de ler.

## Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Uma chave de API da [OpenRouter](https://openrouter.ai/keys)

### Passos

1.  **Clone o repositório (ou tenha acesso a esta pasta):**
    ```bash
    # Exemplo, se o projeto estivesse em um repositório git
    # git clone https://github.com/your-username/kernel-agi-cli.git
    # cd kernel-agi-cli
    ```

2.  **Instale o pacote em modo editável:**
    O modo editável (`-e`) é recomendado, pois permite que você modifique o código-fonte e veja as alterações imediatamente, sem precisar reinstalar.
    ```bash
    pip install -e .
    ```
    Isso instalará as dependências (`aiohttp`, `colorama`) e criará o comando `kernel-chat` no seu ambiente.

## Configuração

A ferramenta requer que sua chave de API da OpenRouter esteja configurada como uma variável de ambiente.

### Linux / macOS
```bash
export OPENROUTER_API_KEY="sua-chave-aqui"
```

### Windows (PowerShell)
```powershell
$env:OPENROUTER_API_KEY="sua-chave-aqui"
```
Você pode adicionar esta linha ao seu arquivo de perfil do shell (como `.bashrc`, `.zshrc` ou `profile.ps1`) para que a variável seja configurada permanentemente.

## Uso

Após a instalação, você pode iniciar o chat simplesmente executando:
```bash
kernel-chat
```

### Argumentos de Linha de Comando

Você pode iniciar o chat com configurações específicas:

-   **Especificar um modelo:**
    ```bash
    kernel-chat --model "anthropic/claude-3.5-sonnet"
    ```

-   **Carregar uma conversa salva:**
    Os arquivos de conversa são salvos em `~/.openrouter_chat/`.
    ```bash
    kernel-chat --load "chat_20240728_103000.json"
    ```

### Comandos Internos

Dentro do chat, você pode usar os seguintes comandos:

-   `/help`: Mostra a lista de todos os comandos disponíveis.
-   `/model`: Permite que você troque o modelo de IA durante a sessão.
-   `/save [nome_opcional]`: Salva a conversa atual. Se nenhum nome for fornecido, um nome com timestamp será gerado.
-   `/load <nome_do_arquivo>`: Carrega uma sessão de chat anterior.
-   `/list`: Lista as últimas 10 conversas salvas.
-   `/history`: Mostra o histórico completo da sessão atual.
-   `/info`: Exibe informações sobre a sessão, como o modelo atual e a contagem de tokens.
-   `/clear`: Limpa o histórico da conversa atual, mantendo o prompt do sistema.
-   `/exit` ou `/quit`: Encerra a sessão de chat.

## Contribuição

Sinta-se à vontade para abrir issues ou pull requests para melhorar esta ferramenta.