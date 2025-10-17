#!/usr/bin/env bash
# --------------------------------------------------------------------------
#  AGI Universal Launcher v3 – Cross-Platform (Bash/WSL/Git Bash)
#  Uso: ./agi-launcher-universal-v3.sh [--Path <caminho>] [--Debug] [--DryRun]
# --------------------------------------------------------------------------

set -euo pipefail

# ---------- config ----------
LOG_FILE="launcher-log-$(date +%F_%H-%M-%S).txt"
exec > >(tee -a "$LOG_FILE") 2>&1

DEFAULT_PATHS=(
    "$HOME/agi-build/agi/release/AGI-win32-x64/AGI.exe"
    "$HOME/agi-build/agi/release/AGI-linux-x64/AGI.AppImage"
    "$HOME/agi-build/agi/release/AGI-darwin-x64/AGI.app"
    "./release/AGI-win32-x64/AGI.exe"
    "./release/AGI-linux-x64/AGI.AppImage"
    "./release/AGI-darwin-x64/AGI.app"
)

# ---------- parse args ----------
PATH_ARG=""
DEBUG_FLAG=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --Path) PATH_ARG="$2"; shift 2 ;;
        --Debug) DEBUG_FLAG=true; shift ;;
        --DryRun) DRY_RUN=true; shift ;;
        --help) echo "Uso: $0 [--Path <caminho>] [--Debug] [--DryRun]"; exit 0 ;;
        *) echo "Opção desconhecida: $1"; exit 1 ;;
    esac
done

# ---------- detect SO ----------
case "$(uname -s)" in
    Linux*)     OS="linux" ;;
    Darwin*)    OS="mac" ;;
    MINGW*|CYGWIN*|MSYS*) OS="win" ;;
    *)          OS="unknown" ;;
esac

# ---------- extensões por SO ----------
case "$OS" in
    linux) EXT="AppImage" ;;
    mac)   EXT="app" ;;
    win)   EXT="exe" ;;
    *)     EXT="*" ;;
esac

# ---------- caminhos candidatos ----------
if [[ -n "$PATH_ARG" ]]; then
    if [[ -d "$PATH_ARG" ]]; then
        CANDIDATES=($(find "$PATH_ARG" -maxdepth 1 -type f -iname "*.$EXT" | head -n 1))
    else
        CANDIDATES=("$PATH_ARG")
    fi
else
    CANDIDATES=("${DEFAULT_PATHS[@]}")
fi

# ---------- funções ----------
function find_build() {
    for c in "${CANDIDATES[@]}"; do
        [[ -f "$c" ]] && echo "$c" && return
    done
    return 1
}

function show_menu() {
    echo "┌─────────────── AGI Universal Launcher v3 ───────────────┐"
    echo "│ SO detectado: $OS │ Extensão esperada: *.$EXT │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│ 1) Executar AGI                                         │"
    echo "│ 2) Executar com logs (--Debug)                          │"
    echo "│ 3) Validar ambiente (--DryRun)                          │"
    echo "│ 0) Sair                                                 │"
    echo "└─────────────────────────────────────────────────────────┘"
    read -p "Escolha: " opt
    case $opt in
        1) return 0 ;;
        2) DEBUG_FLAG=true; return 0 ;;
        3) DRY_RUN=true; return 0 ;;
        0) exit 0 ;;
        *) echo "Opção inválida"; exit 1 ;;
    esac
}

# ---------- lógica ----------
if [[ $# -eq 0 ]]; then
    show_menu
fi

build=$(find_build)
if [[ -z "$build" ]]; then
    echo "❌ Build não encontrado para $OS (*.$EXT)"
    echo "Caminhos verificados:"
    printf '  → %s\n' "${CANDIDATES[@]}"
    exit 1
fi

if $DRY_RUN; then
    echo "✅ Build localizado: $build"
    exit 0
fi

echo "🚀 Iniciando AGI..."
case "$EXT" in
    AppImage)
        chmod +x "$build" 2>/dev/null
        if $DEBUG_FLAG; then
            x-terminal-emulator -e "$build" || gnome-terminal -- "$build" || "$build"
        else
            "$build" &
        fi
        ;;
    app)
        if $DEBUG_FLAG; then
            open -a "$build"
        else
            open "$build"
        fi
        ;;
    exe)
        if $DEBUG_FLAG; then
            powershell -NoExit -Command "\"$build\""
        else
            cmd /c start "" "$build"
        fi
        ;;
    *)
        echo "⚠️ Tipo de build desconhecido: $build"
        exit 1
        ;;
esac

echo "✅ Launcher finalizado. Log: $LOG_FILE"
