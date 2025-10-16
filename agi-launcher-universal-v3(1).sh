#!/usr/bin/env bash
# --------------------------------------------------------------------------
# AGI Universal Launcher v3 – Cross-Platform (Bash/WSL/Git Bash)
# Uso: ./agi-launcher-universal-v3.sh [--path <caminho>] [--debug] [--dry-run]
# --------------------------------------------------------------------------

set -euo pipefail

# --- CONFIGURAÇÃO ---
REPO_DIR="agi"
BUILD_ROOT="release"
LOG_FILE="launcher-log-$(date +%Y-%m-%d_%H-%M-%S).txt"

# Variáveis de Argumentos
CUSTOM_PATH=""
DEBUG_MODE=0
DRY_RUN=0
INTERACTIVE_MENU=1

# --- FUNÇÕES DE UTILIDADE ---

# Função de Log
log() {
    echo "[$(date +%H:%M:%S)] $1" | tee -a "$LOG_FILE"
}

# Função de erro e saída
die() {
    log "❌ ERRO: $1"
    exit 1
}

# --- PARSING DE ARGUMENTOS ---

parse_args() {
    log "Analisando argumentos..."
    
    # Parâmetros esperados
    local options
    options=$(getopt -o "" --long debug,dry-run,path: -- "$@")
    
    if [ $? -ne 0 ]; then
        die "Falha ao analisar argumentos."
    fi

    eval set -- "$options"

    while true; do
        case "$1" in
            --debug)
                DEBUG_MODE=1
                log "Modo: DEBUG ativado."
                shift
                ;;
            --dry-run)
                DRY_RUN=1
                log "Modo: DRY-RUN ativado (Nenhuma execução real)."
                INTERACTIVE_MENU=0
                shift
                ;;
            --path)
                CUSTOM_PATH="$2"
                log "Caminho customizado definido: $CUSTOM_PATH"
                shift 2
                ;;
            --)
                shift
                break
                ;;
            *)
                die "Argumento desconhecido: $1"
                ;;
        esac
    done
}

# --- DETECÇÃO E RESOLUÇÃO DE CAMINHO ---

detect_platform() {
    local OS_NAME
    OS_NAME=$(uname -s)
    local TARGET_DIR=""
    local EXTENSION=""

    log "Detectando sistema operacional..."

    case "$OS_NAME" in
        Linux*)
            if [[ -n "$WSL_DISTRO_NAME" ]] || [[ "$TERM" == *cygwin* ]]; then
                log "Ambiente Windows (WSL/Git Bash) detectado."
                TARGET_DIR="AGI-win32-x64"
                EXTENSION=".exe"
                # Se for WSL, usamos o .exe do Windows
            else
                log "Ambiente Linux detectado."
                TARGET_DIR="AGI-linux-x64"
                EXTENSION=".AppImage"
            fi
            ;;
        Darwin*)
            log "Ambiente macOS detectado."
            TARGET_DIR="AGI-darwin-x64"
            EXTENSION=".app"
            ;;
        MINGW*|CYGWIN*)
            log "Ambiente Windows (Git Bash nativo) detectado."
            TARGET_DIR="AGI-win32-x64"
            EXTENSION=".exe"
            ;;
        *)
            die "Sistema operacional não suportado: $OS_NAME"
            ;;
    esac

    # Se um caminho customizado foi fornecido, usamos ele
    if [ -n "$CUSTOM_PATH" ]; then
        EXECUTABLE_PATH="$CUSTOM_PATH"
    else
        # Se não, resolvemos o caminho padrão
        if [ "$EXTENSION" == ".app" ]; then
            # No macOS, o .app é uma pasta, e o executável está dentro
            EXECUTABLE_PATH="$BUILD_ROOT/$TARGET_DIR/AGI.app/Contents/MacOS/AGI"
            # O usuário pode querer rodar o open, mas para fins de script, rodamos o binário
        else
            EXECUTABLE_PATH="$BUILD_ROOT/$TARGET_DIR/AGI$EXTENSION"
        fi
    fi

    log "Caminho do executável alvo: $EXECUTABLE_PATH"
    log "Extensão alvo: $EXTENSION"
}

# --- FUNÇÃO DE EXECUÇÃO ---

run_app() {
    log "Iniciando AGI..."

    if [ ! -f "$EXECUTABLE_PATH" ] && [ ! -d "$EXECUTABLE_PATH" ]; then
        die "Executável não encontrado em: $EXECUTABLE_PATH. Rode o build primeiro!"
    fi
    
    local EXEC_COMMAND
    local DEBUG_FLAG=""
    
    if [ "$DEBUG_MODE" -eq 1 ]; then
        DEBUG_FLAG="--debug"
        log "Execução com flag de DEBUG ativo."
    fi

    # Lógica de execução baseada na extensão
    case "$EXTENSION" in
        .app) # macOS
            EXEC_COMMAND="open -a '$BUILD_ROOT/$TARGET_DIR/AGI.app' --args $DEBUG_FLAG"
            ;;
        .AppImage) # Linux
            chmod +x "$EXECUTABLE_PATH"
            EXEC_COMMAND="'$EXECUTABLE_PATH' $DEBUG_FLAG"
            ;;
        .exe) # Windows (via WSL/Git Bash) ou Linux binário
            EXEC_COMMAND="'$EXECUTABLE_PATH' $DEBUG_FLAG"
            ;;
        *)
            # Executa o binário diretamente
            EXEC_COMMAND="'$EXECUTABLE_PATH' $DEBUG_FLAG"
            ;;
    esac

    log "Comando de execução: $EXEC_COMMAND"

    if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY-RUN: Simulação de execução concluída."
    else
        log "Executando..."
        # Usamos eval para garantir que as aspas e comandos complexos funcionem
        eval "$EXEC_COMMAND"
    fi

    log "AGI encerrado."
}

# --- MENU INTERATIVO (Para modo padrão) ---

show_menu() {
    log "Modo Interativo Ativo."
    echo "--------------------------------------------------------"
    echo "       AGI Universal Launcher v3 (Executável: $EXTENSION)"
    echo "--------------------------------------------------------"
    echo "Executável alvo: $EXECUTABLE_PATH"
    echo ""
    echo "Opções:"
    echo "  1) Iniciar AGI (Modo Normal)"
    echo "  2) Iniciar AGI (Modo DEBUG - Logs detalhados)"
    echo "  3) Ver caminho do executável"
    echo "  4) Sair"
    echo "--------------------------------------------------------"
    
    local choice
    read -r -p "Escolha uma opção (1-4): " choice
    
    case $choice in
        1) 
            DEBUG_MODE=0
            run_app
            ;;
        2)
            DEBUG_MODE=1
            run_app
            ;;
        3)
            echo "Caminho: $EXECUTABLE_PATH"
            log "Caminho exibido."
            show_menu
            ;;
        4)
            log "Encerrando script."
            exit 0
            ;;
        *)
            echo "Opção inválida. Tente novamente."
            show_menu
            ;;
    esac
}

# --- EXECUÇÃO PRINCIPAL ---

main() {
    parse_args "$@"
    detect_platform

    if [ "$DRY_RUN" -eq 1 ] || [ "$INTERACTIVE_MENU" -eq 0 ]; then
        # Modo não interativo (Debug ou Dry-Run)
        run_app
    else
        # Modo interativo (padrão)
        show_menu
    fi
    
    log "Execução do launcher finalizada com sucesso."
}

# Inicia o script
main "$@"

# --- FIM DO SCRIPT ---
