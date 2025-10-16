#!/usr/bin/env python3
# ----------------------------------------------------------------------
# Interactive Console Chat Interface (OpenRouter API) - Otimizado e Final
#
# Adiciona: Cores, Comandos, Persistência de Histórico e Relatórios
# de Performance (Tokens, Latência e Custo Estimado).
# ----------------------------------------------------------------------
import aiohttp
import asyncio
import json
import sys
import os
import time # Adicionado para medição de latência
import argparse # Adicionado para parsing de argumentos
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple # Adicionado Tuple para tipo de retorno

# Tenta importar colorama para cores no console
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Fallback sem cores
    class Fore:
        CYAN = GREEN = YELLOW = RED = MAGENTA = BLUE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# ======================================================================
# 🔧 CONFIGURAÇÃO E DADOS DE CUSTO (Estimativas Baseadas em Preços Públicos)
# ======================================================================

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Headers obrigatórios para autenticação
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/your-username/openrouter-chat",
    "X-Title": "Console Chat App - Kernel AGI"
}

# Configurações padrão
DEFAULT_MODEL = "openai/gpt-4o-mini"
TYPING_DELAY = 0.025
MAX_HISTORY_MESSAGES = 20
SAVE_DIR = Path.home() / ".openrouter_chat"

# CUSTO POR 1M DE TOKENS (USD - Valores de Referência OpenRouter/API)
# Usados para cálculo estimado de custo por requisição
MODEL_PRICING = {
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai/gpt-4o": {"input": 5.00, "output": 15.00},
    "anthropic/claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
    "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
    "google/gemini-pro-1.5": {"input": 3.50, "output": 7.00},
    "meta-llama/llama-3.1-70b-instruct": {"input": 0.50, "output": 0.70},
}

# Modelos disponíveis (exemplos populares)
AVAILABLE_MODELS = {
    "1": ("openai/gpt-4o-mini", "GPT-4 Omni Mini - Rápido e eficiente"),
    "2": ("openai/gpt-4o", "GPT-4 Omni - Mais poderoso"),
    "3": ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet - Excelente raciocínio"),
    "4": ("anthropic/claude-3-haiku", "Claude 3 Haiku - Rápido e econômico"),
    "5": ("google/gemini-pro-1.5", "Gemini Pro 1.5 - Google AI"),
    "6": ("meta-llama/llama-3.1-70b-instruct", "Llama 3.1 70B - Open source"),
}

# Estado global
conversation_history: List[Dict[str, str]] = []
current_model = DEFAULT_MODEL
is_streaming = False

# ======================================================================
# 🎨 FUNÇÕES DE UTILIDADE E CÁLCULO
# ======================================================================

def print_colored(text: str, color: str = Fore.CYAN, bright: bool = False, end: str = "\n"):
    """Imprime texto colorido se colorama estiver disponível."""
    style = Style.BRIGHT if bright else ""
    # Incluído 'end' para permitir que o prompt de streaming não pule linha.
    print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)

def print_separator(char: str = "─", length: int = 70):
    """Imprime uma linha separadora."""
    print_colored(char * length, Fore.CYAN)

def calculate_estimated_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calcula o custo estimado em USD com base na tabela de preços."""
    prices = MODEL_PRICING.get(model_id)
    if not prices:
        return 0.0

    # Preço é por 1 milhão de tokens. Dividimos por 1.000.000
    cost_prompt = (prompt_tokens / 1_000_000) * prices["input"]
    cost_completion = (completion_tokens / 1_000_000) * prices["output"]

    return cost_prompt + cost_completion

def count_tokens_estimate(text: str) -> int:
    """Estimativa simples de tokens (aproximadamente 4 chars = 1 token)."""
    # Esta função é apenas para o /info, o uso real vem da API
    return len(text) // 4

def truncate_history():
    """Mantém o histórico dentro do limite definido."""
    global conversation_history

    # +1 para a mensagem do sistema
    if len(conversation_history) > MAX_HISTORY_MESSAGES + 1:
        system_msg = conversation_history[0]
        # Trunca, mantendo o system prompt + o número máximo de mensagens
        conversation_history = [system_msg] + conversation_history[-(MAX_HISTORY_MESSAGES):]
        print_colored("⚠️  Histórico truncado para manter limite de mensagens.", Fore.YELLOW)

def ensure_save_dir():
    """Garante que o diretório de salvamento existe."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================================
# 💾 FUNÇÕES DE SALVAMENTO/CARREGAMENTO (Mantidas)
# ======================================================================

def save_conversation(filename: Optional[str] = None):
    """Salva a conversa atual em um arquivo JSON."""
    ensure_save_dir()

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{timestamp}.json"

    filepath = SAVE_DIR / filename

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "model": current_model,
                "timestamp": datetime.now().isoformat(),
                "messages": conversation_history
            }, f, indent=2, ensure_ascii=False)

        print_colored(f"✅ Conversa salva em: {filepath}", Fore.GREEN)
    except Exception as e:
        print_colored(f"❌ Erro ao salvar: {e}", Fore.RED)

def load_conversation(filename: str):
    """Carrega uma conversa de um arquivo JSON."""
    global conversation_history, current_model

    filepath = SAVE_DIR / filename if not filename.startswith('/') else Path(filename)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conversation_history = data.get("messages", [])
        current_model = data.get("model", DEFAULT_MODEL)

        print_colored(f"✅ Conversa carregada: {len(conversation_history)} mensagens", Fore.GREEN)
        print_colored(f"📋 Modelo: {current_model}", Fore.CYAN)
        show_history()
    except FileNotFoundError:
        print_colored(f"❌ Arquivo não encontrado: {filepath}", Fore.RED)
    except Exception as e:
        print_colored(f"❌ Erro ao carregar: {e}", Fore.RED)

def list_saved_conversations():
    """Lista todas as conversas salvas."""
    ensure_save_dir()

    files = sorted(SAVE_DIR.glob("chat_*.json"), reverse=True)

    if not files:
        print_colored("📭 Nenhuma conversa salva encontrada.", Fore.YELLOW)
        return

    print_colored("\n📚 Conversas salvas:", Fore.CYAN, bright=True)
    for i, f in enumerate(files[:10], 1): # Mostra últimas 10
        stat = f.stat()
        size = stat.st_size / 1024 # KB
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f" {i}. {Fore.YELLOW}{f.name}{Style.RESET_ALL} ({size:.1f} KB) - {mtime}")

# ======================================================================
# 🤖 FUNÇÃO DE STREAMING COM MÉTRICAS
# ======================================================================

async def chat_stream(
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> Tuple[str, Optional[Dict], float]:
    """
    Envia requisição de chat com streaming, exibe resposta e mede performance.
    Retorna (full_response, usage_metadata, latency).
    """
    global is_streaming

    payload = {
        "model": model,
        "messages": conversation_history,
        "stream": True,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    full_response = ""
    usage_metadata: Optional[Dict] = None
    is_streaming = True
    start_time = time.time() # Inicia a medição de latência

    print_colored("\n🤖 Assistente: ", Fore.MAGENTA, bright=True, end="")

    try:
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
            async with session.post(API_URL, json=payload) as resp:

                if resp.status != 200:
                    error_text = await resp.text()
                    print_colored(f"\n\n❌ Erro HTTP {resp.status}", Fore.RED)
                    print_colored(f"Detalhes: {error_text}", Fore.RED)
                    return "", None, 0.0

                async for raw_line in resp.content:
                    line = raw_line.decode("utf-8", errors='ignore').strip()

                    if not line or not line.startswith("data:"):
                        continue

                    data_str = line[5:].strip()

                    if data_str == "[DONE]":
                        break

                    try:
                        data_json = json.loads(data_str)

                        # Captura metadata de uso que geralmente vem no final do stream
                        if 'usage' in data_json:
                            # A OpenRouter envia a métrica de uso no último chunk antes do [DONE]
                            usage_metadata = data_json['usage']

                        delta = data_json.get("choices", [{}])[0].get("delta", {}).get("content", "")

                        if delta:
                            # Otimização: para deltas grandes, reduz delay
                            delay = TYPING_DELAY if len(delta) < 50 else TYPING_DELAY / 3

                            for char in delta:
                                print(char, end="", flush=True)
                                full_response += char
                                await asyncio.sleep(delay)

                    except json.JSONDecodeError:
                        continue

    except asyncio.TimeoutError:
        print_colored("\n\n⏱️  Timeout: Requisição demorou muito.", Fore.RED)
    except Exception as e:
        print_colored(f"\n\n❌ Erro de conexão/stream: {e}", Fore.RED)
    finally:
        is_streaming = False
        latency = time.time() - start_time

    print() # Nova linha após resposta
    return full_response, usage_metadata, latency

# ======================================================================
# 📋 COMANDOS ESPECIAIS
# ======================================================================

def show_help():
    """Exibe menu de ajuda com comandos disponíveis."""
    print_separator()
    print_colored("📖 COMANDOS DISPONÍVEIS", Fore.CYAN, bright=True)
    print_separator()
    commands = [
        ("/help", "Mostra esta mensagem de ajuda"),
        ("/clear", "Limpa o histórico de conversa (mantém system prompt)"),
        ("/history", "Mostra o histórico completo"),
        ("/save [nome]", "Salva a conversa atual"),
        ("/load <nome>", "Carrega uma conversa salva"),
        ("/list", "Lista conversas salvas"),
        ("/model", "Troca o modelo de IA"),
        ("/info", "Mostra informações da sessão"),
        ("/exit, /quit", "Encerra o chat"),
    ]
    for cmd, desc in commands:
        print(f" {Fore.GREEN}{cmd:20s}{Style.RESET_ALL} - {desc}")
    print_separator()

def show_info():
    """Mostra informações da sessão atual."""
    print_separator()
    print_colored("ℹ️  INFORMAÇÕES DA SESSÃO", Fore.CYAN, bright=True)
    print_separator()
    print(f" Modelo atual: {Fore.GREEN}{current_model}{Style.RESET_ALL}")
    print(f" Mensagens no histórico: {Fore.YELLOW}{len(conversation_history)}{Style.RESET_ALL}")
    print(f" Limite de Contexto: {Fore.YELLOW}{MAX_HISTORY_MESSAGES} mensagens (excluindo system){Style.RESET_ALL}")

    total_tokens = sum(count_tokens_estimate(msg['content']) for msg in conversation_history)
    print(f" Tokens estimados total: {Fore.YELLOW}~{total_tokens}{Style.RESET_ALL}")
    print_separator()

def change_model():
    """Interface para trocar o modelo."""
    global current_model

    print_separator()
    print_colored("🔄 SELECIONE UM MODELO", Fore.CYAN, bright=True)
    print_separator()

    for key, (model_id, description) in AVAILABLE_MODELS.items():
        current = " (atual)" if model_id == current_model else ""
        cost_info = f" (Input: ${MODEL_PRICING.get(model_id, {}).get('input', 'N/A'):.2f}/M)" if model_id in MODEL_PRICING else ""

        print(f" {Fore.GREEN}{key}{Style.RESET_ALL}. {description}{Fore.YELLOW}{current}{cost_info}{Style.RESET_ALL}")

    print_separator()
    choice = input(f"{Fore.CYAN}Escolha (1-{len(AVAILABLE_MODELS)}): {Style.RESET_ALL}").strip()

    if choice in AVAILABLE_MODELS:
        current_model = AVAILABLE_MODELS[choice][0]
        print_colored(f"✅ Modelo alterado para: {current_model}", Fore.GREEN)
    else:
        print_colored("❌ Opção inválida.", Fore.RED)

def show_history():
    """Exibe o histórico de conversa formatado."""
    print_separator()
    print_colored("📜 HISTÓRICO DA CONVERSA", Fore.CYAN, bright=True)
    print_separator()

    for i, msg in enumerate(conversation_history, 1):
        role = msg['role']
        content = msg['content']

        if role == "system":
            color = Fore.BLUE
            icon = "⚙️"
        elif role == "user":
            color = Fore.GREEN
            icon = "👤"
        else:
            color = Fore.MAGENTA
            icon = "🤖"

        print(f"\n{color}{Style.BRIGHT}{icon} {role.upper()}{Style.RESET_ALL}")
        # Trunca mensagens muito longas
        display_content = content if len(content) < 500 else content[:500] + "..."
        print(f"{display_content}")

    print_separator()

# ======================================================================
# 🎮 LOOP PRINCIPAL
# ======================================================================

async def main_loop():
    """Loop principal do chat interativo."""
    global conversation_history, current_model

    # --- 1. Inicialização ---
    if not API_KEY:
          print_colored("❌ ERRO: A chave de API OPENROUTER_API_KEY não está configurada.", Fore.RED, bright=True)
          print_colored("Por favor, configure-a como uma variável de ambiente.", Fore.YELLOW)
          sys.exit(1)

    # Inicializa com system prompt padrão se vazio (apenas na primeira rodada)
    if not conversation_history:
        conversation_history = [{
            "role": "system",
            "content": "Você é um assistente de IA prestativo, inteligente e conciso, alinhado à busca pela verdade (Aletheia)."
        }]

    print_separator("═", 70)
    print_colored("🚀 CHAT INTERATIVO KERNEL AGI - Aletheia Terminal", Fore.CYAN, bright=True)
    print_separator("═", 70)
    print_colored(f"Modelo: {current_model}", Fore.YELLOW)
    print_colored("Digite /help para ver comandos disponíveis. Use /exit para sair.", Fore.BLUE)
    print_separator("═", 70)

    # Imprime o system prompt de início
    if conversation_history and conversation_history[0].get("role") == "system":
        print_colored(f"⚙️ MODO: {conversation_history[0]['content']}", Fore.BLUE)
        print_separator("─", 70)

    # --- 2. Loop de Interação ---
    while True:
        try:
            # Leitura de input do usuário
            user_input = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: input(f"\n{Fore.GREEN}{Style.BRIGHT}👤 Você:{Style.RESET_ALL} ")
            )

            user_input = user_input.strip()

            if not user_input:
                continue

            # Processa comandos
            if user_input.startswith('/'):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                arg = cmd_parts[1] if len(cmd_parts) > 1 else None

                if cmd in ['/exit', '/quit']:
                    print_colored("\n👋 Até logo! Busque sempre a verdade (Aletheia).", Fore.CYAN)
                    break

                elif cmd == '/clear':
                    system_msg = conversation_history[0] if conversation_history else None
                    conversation_history = [system_msg] if system_msg else []
                    print_colored("🗑️  Histórico limpo.", Fore.YELLOW)
                    continue

                elif cmd == '/history':
                    show_history()
                    continue

                elif cmd == '/save':
                    save_conversation(arg)
                    continue

                elif cmd == '/load':
                    if arg: load_conversation(arg)
                    else: print_colored("❌ Uso: /load <nome_do_arquivo>", Fore.RED)
                    continue

                elif cmd == '/list':
                    list_saved_conversations()
                    continue

                elif cmd == '/model':
                    change_model()
                    continue

                elif cmd == '/info':
                    show_info()
                    continue

                elif cmd == '/help':
                    show_help()
                    continue

                else:
                    print_colored(f"❌ Comando desconhecido: {cmd}", Fore.RED)
                    print_colored("Digite /help para ver comandos disponíveis", Fore.YELLOW)
                    continue

            # Adiciona mensagem do usuário ao histórico
            conversation_history.append({"role": "user", "content": user_input})

            # Chama a API com streaming e captura métricas
            response, metadata, latency = await chat_stream(model=current_model)

            # Adiciona resposta ao histórico
            if response.strip():
                conversation_history.append({"role": "assistant", "content": response})
                truncate_history()

                # --- RELATÓRIO PÓS-RESPOSTA ---
                if metadata and 'usage' in metadata:
                    usage = metadata['usage']
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)

                    estimated_cost = calculate_estimated_cost(current_model, prompt_tokens, completion_tokens)

                    print_separator("┄", 70)
                    print_colored(f"📊 Prompt: {prompt_tokens} tokens | Completion: {completion_tokens} tokens", Fore.YELLOW)
                    print_colored(f"⏱️  Latência Total: {latency:.2f} s", Fore.YELLOW)
                    print_colored(f"💰 Custo Estimado: ${estimated_cost:.6f} USD", Fore.YELLOW, bright=True)
                    print_separator("┄", 70)
                # -----------------------------

            else:
                # Remove a mensagem do usuário se a resposta falhou (para não poluir o histórico)
                conversation_history.pop()

        except KeyboardInterrupt:
            print_colored("\n\n⚠️  Sessão interrompida. Use /exit para sair.", Fore.YELLOW)
            continue

        except Exception as e:
            if not is_streaming:
                print_colored(f"\n❌ Erro fatal no loop: {e}", Fore.RED)
            break

# ======================================================================
# 🚀 EXECUÇÃO COM ARGUMENTOS
# ======================================================================
def entry_point():
    """Ponto de entrada principal que processa argumentos e inicia o loop."""
    global current_model

    parser = argparse.ArgumentParser(description="Chat interativo com a API OpenRouter.")
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"ID do modelo a ser usado (padrão: {DEFAULT_MODEL})."
    )
    parser.add_argument(
        "--load",
        type=str,
        metavar="FILENAME",
        help="Carrega uma conversa salva de um arquivo JSON."
    )

    args = parser.parse_args()

    # Define o modelo a partir do argumento, se fornecido
    current_model = args.model

    if not API_KEY:
        print_colored("❌ ERRO: A chave de API OPENROUTER_API_KEY não está configurada.", Fore.RED, bright=True)
        print_colored("Por favor, configure-a como uma variável de ambiente.", Fore.YELLOW)
        sys.exit(1)

    # Carrega a conversa se o argumento --load for usado
    if args.load:
        load_conversation(args.load)

    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print_colored("\n\n👋 Chat encerrado.", Fore.CYAN)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Erro crítico: {e}", Fore.RED)
        sys.exit(1)

if __name__ == "__main__":
    entry_point()