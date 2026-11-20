#!/usr/bin/env bash
# ==============================================================================
# ARI-DEV OLLAMA LOCAL AI MANAGER — NEURAL CYBER EDITION (FLICKER-FREE TUI)
# Dependencies: bash, curl, awk, sed, grep, stty (optional: jq, xclip/wl-copy)
# ==============================================================================

set -u
shopt -s checkwinsize 2>/dev/null || true

APP_NAME="ARI-DEV // NEURAL OLLAMA ENGINE"
APP_SUB="LOCAL LLM ORCHESTRATOR • BASH TUI"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="${SCRIPT_DIR}/models_db.json"
CONFIG_PATH="${SCRIPT_DIR}/config.json"
OLLAMA_BASE_URL="http://127.0.0.1:11434"

TMP_DIR="$(mktemp -d /tmp/ari-neural-tui.XXXXXX)"
MAIN_PID="$$"
HAS_JQ=0
command -v jq >/dev/null 2>&1 && HAS_JQ=1

# ==============================================================================
# 1. 24-BIT TRUECOLOR CYBER-NEURAL PALETTE & TERMINAL CONTROL
# ==============================================================================
RST=$'\033[0m'
BOLD=$'\033[1m'
ITALIC=$'\033[3m'

# Foreground RGB
FG_TEXT=$'\033[38;2;226;232;240m'      # #E2E8F0 Slate White
FG_MUTED=$'\033[38;2;100;116;139m'     # #64748B Muted Slate
FG_DIM=$'\033[38;2;71;85;105m'         # #475569 Dark Slate
FG_CYAN=$'\033[38;2;0;240;255m'        # #00F0FF Neon Cyber Cyan
FG_SKY=$'\033[38;2;56;189;248m'        # #38BDF8 Electric Sky
FG_VIOLET=$'\033[38;2;167;139;250m'    # #A78BFA Neural Violet
FG_GREEN=$'\033[38;2;16;185;129m'      # #10B981 Emerald Pulse
FG_AMBER=$'\033[38;2;245;158;11m'      # #F59E0B Amber Warning
FG_RED=$'\033[38;2;244;63;94m'         # #F43F5E Rose Alert
FG_DARK=$'\033[38;2;10;15;28m'         # #0A0F1C Deep Obsidian

# Background RGB
BG_MAIN=$'\033[48;2;9;13;22m'          # #090D16 Obsidian Canvas
BG_CARD=$'\033[48;2;15;23;42m'         # #0F172A Deep Slate Card
BG_SEL=$'\033[48;2;22;38;68m'          # #162644 Active Neon Tint
BG_PILL_CYAN=$'\033[48;2;0;240;255m'   # #00F0FF Highlight Pill
BG_PILL_VIO=$'\033[48;2;139;92;246m'   # #8B5CF6 Violet Pill
BG_BADGE_OK=$'\033[48;2;6;78;59m'      # #064E3B Emerald Badge BG
BG_BADGE_ERR=$'\033[48;2;127;29;29m'   # #7F1D1D Crimson Badge BG

# Terminal Control Sequences
ALT_ON=$'\033[?1049h'
ALT_OFF=$'\033[?1049l'
CUR_HIDE=$'\033[?25l'
CUR_SHOW=$'\033[?25h'
SYNC_START=$'\033[?2026h'
SYNC_END=$'\033[?2026l'
CLR_EOL=$'\033[K'

IN_ALT_SCREEN=0
FRAME_BUF=""
RET_LEN=0
RET_STR=""

enter_tui() {
    if [[ ${IN_ALT_SCREEN} -eq 0 ]]; then
        printf "%s%s%s\033[H\033[2J" "${ALT_ON}" "${CUR_HIDE}" "${BG_MAIN}"
        stty -echo -icanon min 1 time 0 2>/dev/null || true
        IN_ALT_SCREEN=1
    fi
}

leave_tui() {
    if [[ ${IN_ALT_SCREEN} -eq 1 ]]; then
        stty sane 2>/dev/null || true
        printf "%s%s%s" "${RST}" "${CUR_SHOW}" "${ALT_OFF}"
        IN_ALT_SCREEN=0
    fi
}

cleanup() {
    if [[ "${BASHPID:-$$}" -eq "${MAIN_PID}" ]]; then
        leave_tui
        rm -rf "${TMP_DIR}"
    fi
}
trap cleanup EXIT INT TERM

# ==============================================================================
# 2. DATABASE (models_db.json) & CONFIG (config.json)
# ==============================================================================
init_files() {
    if [[ ! -f "${DB_PATH}" ]]; then
        cat > "${DB_PATH}" << 'EOF'
[
  {
    "name": "qwen2.5-coder:1.5b-instruct",
    "min_ram_gb": 4,
    "min_vram_gb": 2,
    "size": "986 MB",
    "description_id": "Sangat cepat & ringan untuk autocomplete & coding harian.",
    "description_en": "Ultra-fast & lightweight for daily coding & autocomplete.",
    "category": "Coding / Light"
  },
  {
    "name": "gemma2:2b",
    "min_ram_gb": 6,
    "min_vram_gb": 3,
    "size": "1.6 GB",
    "description_id": "Responsif, general chat & pemahaman bahasa Indonesia bagus.",
    "description_en": "Responsive general chat with strong Indonesian comprehension.",
    "category": "General / Light"
  },
  {
    "name": "qwen2.5-coder:3b",
    "min_ram_gb": 8,
    "min_vram_gb": 3,
    "size": "1.9 GB",
    "description_id": "Seimbang untuk code completion, refactoring & debugging.",
    "description_en": "Balanced for code completion, refactoring & debugging.",
    "category": "Coding / Medium"
  },
  {
    "name": "phi3:3.8b",
    "min_ram_gb": 8,
    "min_vram_gb": 4,
    "size": "2.2 GB",
    "description_id": "Kuat untuk penalaran logika, matematika & analisis kode.",
    "description_en": "Strong for logical reasoning, math & code analysis.",
    "category": "Reasoning / Medium"
  },
  {
    "name": "llama3.2:3b",
    "min_ram_gb": 8,
    "min_vram_gb": 4,
    "size": "2.0 GB",
    "description_id": "Cerdas untuk asisten teks umum, ringkasan & instruksi.",
    "description_en": "Smart general text assistant, summaries & instructions.",
    "category": "General / Medium"
  },
  {
    "name": "qwen2.5:7b-instruct",
    "min_ram_gb": 16,
    "min_vram_gb": 6,
    "size": "4.7 GB",
    "description_id": "Performa tinggi untuk tugas kompleks (hybrid GPU+RAM).",
    "description_en": "High capability for complex tasks (hybrid GPU+RAM).",
    "category": "General / Heavy"
  },
  {
    "name": "deepseek-r1:7b",
    "min_ram_gb": 16,
    "min_vram_gb": 6,
    "size": "4.7 GB",
    "description_id": "Model deep-reasoning dengan alur berpikir bertahap.",
    "description_en": "Deep-reasoning model with step-by-step chain of thought.",
    "category": "Reasoning / Heavy"
  }
]
EOF
    fi

    if [[ ! -f "${CONFIG_PATH}" ]]; then
        echo '{"lang": "id"}' > "${CONFIG_PATH}"
    fi
}

get_lang() {
    if [[ -f "${CONFIG_PATH}" ]] && grep -q '"en"' "${CONFIG_PATH}"; then
        echo "en"
    else
        echo "id"
    fi
}

set_lang() {
    echo "{\"lang\": \"$1\"}" > "${CONFIG_PATH}"
}

# ==============================================================================
# 3. SYSTEM HARDWARE, GPU TELEMETRY & OLLAMA STATE DETECTION
# ==============================================================================
CPU_CORES=4
RAM_TOTAL_GB="8.0"
RAM_USED_GB="0.0"
RAM_PCT=0
GPU_NAME="Integrated / CPU Compute"
VRAM_TOTAL_GB="0.0"
VRAM_USED_GB="0.0"
VRAM_PCT=0
GPU_TEMP=""
HAS_NVIDIA=0

detect_hardware() {
    CPU_CORES="$(nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 4)"

    if [[ -r /proc/meminfo ]]; then
        local mem_tot_kb mem_avail_kb
        mem_tot_kb="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
        mem_avail_kb="$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)"
        [[ -z "${mem_avail_kb}" ]] && mem_avail_kb="${mem_tot_kb}"
        RAM_TOTAL_GB="$(awk -v t="${mem_tot_kb}" 'BEGIN {printf "%.1f", t / 1048576}')"
        RAM_USED_GB="$(awk -v t="${mem_tot_kb}" -v a="${mem_avail_kb}" 'BEGIN {printf "%.1f", (t - a) / 1048576}')"
        RAM_PCT="$(awk -v t="${mem_tot_kb}" -v a="${mem_avail_kb}" 'BEGIN {if(t>0) printf "%d", ((t-a)/t)*100; else print 0}')"
    fi

    HAS_NVIDIA=0
    GPU_TEMP=""
    if command -v nvidia-smi >/dev/null 2>&1; then
        local nv_out
        nv_out="$(nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>/dev/null | head -n 1)"
        if [[ -n "${nv_out}" ]]; then
            HAS_NVIDIA=1
            GPU_NAME="$(echo "${nv_out}" | cut -d',' -f1 | xargs)"
            local v_used v_tot v_temp
            v_used="$(echo "${nv_out}" | cut -d',' -f2 | xargs)"
            v_tot="$(echo "${nv_out}" | cut -d',' -f3 | xargs)"
            v_temp="$(echo "${nv_out}" | cut -d',' -f4 | xargs)"
            if [[ "${v_tot}" =~ ^[0-9]+$ && "${v_tot}" -gt 0 ]]; then
                VRAM_TOTAL_GB="$(awk -v m="${v_tot}" 'BEGIN {printf "%.1f", m / 1024}')"
                VRAM_USED_GB="$(awk -v m="${v_used:-0}" 'BEGIN {printf "%.1f", m / 1024}')"
                VRAM_PCT="$(awk -v u="${v_used:-0}" -v t="${v_tot}" 'BEGIN {printf "%d", (u / t) * 100}')"
            fi
            [[ "${v_temp}" =~ ^[0-9]+$ ]] && GPU_TEMP="${v_temp}°C"
        fi
    elif command -v lspci >/dev/null 2>&1; then
        local pci_gpu
        pci_gpu="$(lspci 2>/dev/null | grep -iE 'VGA compatible controller|3D controller' | head -n 1 | awk -F': ' '{print $2}' | cut -c1-38)"
        [[ -n "${pci_gpu}" ]] && GPU_NAME="${pci_gpu}"
    fi
}

OLLAMA_INSTALLED=0
OLLAMA_RUNNING=0
OLLAMA_VERSION="-"
INSTALLED_MODELS=() # "name|size|modified"

detect_ollama_state() {
    OLLAMA_INSTALLED=0
    OLLAMA_RUNNING=0
    OLLAMA_VERSION="-"
    INSTALLED_MODELS=()

    if command -v ollama >/dev/null 2>&1; then
        OLLAMA_INSTALLED=1
        local v_raw
        v_raw="$(ollama --version 2>/dev/null | head -n 1)"
        OLLAMA_VERSION="$(echo "${v_raw}" | sed -E 's/.*version is /v/; s/ollama version /v/')"
        [[ -z "${OLLAMA_VERSION}" ]] && OLLAMA_VERSION="installed"

        local tags_json
        tags_json="$(curl -sf --max-time 2 "${OLLAMA_BASE_URL}/api/tags" 2>/dev/null || true)"
        if [[ -n "${tags_json}" ]]; then
            OLLAMA_RUNNING=1
            if [[ "${HAS_JQ}" -eq 1 ]]; then
                while IFS= read -r line; do
                    [[ -n "${line}" ]] && INSTALLED_MODELS+=("${line}")
                done < <(echo "${tags_json}" | jq -r '.models[]? | "\(.name)|\((.size / 1073741824 * 100 | round) / 100) GB|\(.modified_at[0:10])"')
            else
                while IFS= read -r line; do
                    [[ -n "${line}" ]] && INSTALLED_MODELS+=("${line}")
                done < <(ollama list 2>/dev/null | tail -n +2 | awk '{print $1 "|" $3 " " $4 "|" $5}')
            fi
        elif ollama list >/dev/null 2>&1; then
            OLLAMA_RUNNING=1
            while IFS= read -r line; do
                [[ -n "${line}" ]] && INSTALLED_MODELS+=("${line}")
            done < <(ollama list 2>/dev/null | tail -n +2 | awk '{print $1 "|" $3 " " $4 "|" $5}')
        fi
    fi
}

evaluate_fit() {
    local min_ram="$1"
    local min_vram="$2"
    awk -v r="${RAM_TOTAL_GB}" -v v="${VRAM_TOTAL_GB}" -v mr="${min_ram}" -v mv="${min_vram}" '
    BEGIN {
        if (v >= mv && r >= mr) { print "3|optimal"; exit }
        if (r >= mr * 1.25)      { print "2|compat";  exit }
        if (r >= mr)             { print "1|compat";  exit }
        print "0|heavy"
    }'
}

copy_to_clipboard() {
    local content="$1"
    if command -v wl-copy >/dev/null 2>&1; then
        printf "%s" "${content}" | wl-copy && return 0
    elif command -v xclip >/dev/null 2>&1; then
        printf "%s" "${content}" | xclip -selection clipboard && return 0
    elif command -v xsel >/dev/null 2>&1; then
        printf "%s" "${content}" | xsel --clipboard --input && return 0
    fi
    return 1
}

# ==============================================================================
# 4. ZERO-FLICKER DOUBLE-BUFFERED RENDERING ENGINE (PURE BASH, NO SUBSHELLS)
# ==============================================================================
BOX_W=96
PAD_L=2
PAD_L_STR="  "

calc_layout() {
    local cols="${COLUMNS:-0}"
    if [[ ${cols} -le 0 ]]; then
        cols="$(tput cols 2>/dev/null || echo 100)"
    fi
    if [[ ${cols} -ge 104 ]]; then
        BOX_W=98
    elif [[ ${cols} -ge 80 ]]; then
        BOX_W=$((cols - 4))
    else
        BOX_W=76
    fi
    PAD_L=$(( (cols - BOX_W) / 2 ))
    [[ ${PAD_L} -lt 0 ]] && PAD_L=0
    PAD_L_STR=""
    [[ ${PAD_L} -gt 0 ]] && printf -v PAD_L_STR "%*s" "${PAD_L}" ""
}

# Pure-Bash ANSI length counter (zero sed / zero subshells)
strip_ansi_len() {
    local s="$1"
    while [[ "$s" == *$'\033['* ]]; do
        local prefix="${s%%$'\033['*}"
        local rest="${s#*$'\033['}"
        if [[ "$rest" == *m* ]]; then
            rest="${rest#*m}"
            s="${prefix}${rest}"
        else
            break
        fi
    done
    RET_LEN=${#s}
}

repeat_char_var() {
    local ch="$1"
    local count="$2"
    RET_STR=""
    [[ ${count} -le 0 ]] && return
    printf -v RET_STR "%*s" "${count}" ""
    RET_STR="${RET_STR// /${ch}}"
}

truncate_plain_var() {
    local str="$1"
    local max_len="$2"
    if [[ ${#str} -gt ${max_len} ]]; then
        if [[ ${max_len} -gt 3 ]]; then
            RET_STR="${str:0:$((max_len - 3))}..."
        else
            RET_STR="${str:0:${max_len}}"
        fi
    else
        RET_STR="${str}"
    fi
}

make_gauge_var() {
    local pct="$1"
    local width="${2:-10}"
    local fill_color="${3:-${FG_CYAN}}"
    [[ ${pct} -lt 0 ]] && pct=0
    [[ ${pct} -gt 100 ]] && pct=100

    local filled=$(( (pct * width + 50) / 100 ))
    local empty=$(( width - filled ))
    local f_str="" e_str=""
    repeat_char_var "■" "${filled}"
    f_str="${RET_STR}"
    repeat_char_var "□" "${empty}"
    e_str="${RET_STR}"
    RET_STR="${fill_color}${f_str}${FG_DIM}${e_str}"
}

buf_blank_line() {
    FRAME_BUF+="${BG_MAIN}${CLR_EOL}"$'\n'
}

buf_box_top() {
    local border_col="${1:-${FG_CYAN}}"
    local inner=$((BOX_W - 2))
    repeat_char_var "─" "${inner}"
    FRAME_BUF+="${BG_MAIN}${PAD_L_STR}${BG_CARD}${border_col}╭${RET_STR}╮${BG_MAIN}${CLR_EOL}"$'\n'
}

buf_box_sep() {
    local border_col="${1:-${FG_DIM}}"
    local inner=$((BOX_W - 2))
    repeat_char_var "─" "${inner}"
    FRAME_BUF+="${BG_MAIN}${PAD_L_STR}${BG_CARD}${border_col}├${RET_STR}┤${BG_MAIN}${CLR_EOL}"$'\n'
}

buf_box_bottom() {
    local border_col="${1:-${FG_CYAN}}"
    local inner=$((BOX_W - 2))
    repeat_char_var "─" "${inner}"
    FRAME_BUF+="${BG_MAIN}${PAD_L_STR}${BG_CARD}${border_col}╰${RET_STR}╯${BG_MAIN}${CLR_EOL}"$'\n'
}

buf_box_line() {
    local content="$1"
    local border_col="${2:-${FG_CYAN}}"
    local row_bg="${3:-${BG_CARD}}"
    local inner=$((BOX_W - 4))
    strip_ansi_len "${content}"
    local vlen=${RET_LEN}
    local pad_r=$((inner - vlen))
    [[ ${pad_r} -lt 0 ]] && pad_r=0

    local pad_r_str=""
    [[ ${pad_r} -gt 0 ]] && printf -v pad_r_str "%*s" "${pad_r}" ""

    FRAME_BUF+="${BG_MAIN}${PAD_L_STR}${row_bg}${border_col}│ ${FG_TEXT}${content}${row_bg}${pad_r_str} ${border_col}│${BG_MAIN}${CLR_EOL}"$'\n'
}

buf_footer_hints() {
    local hints="$1"
    FRAME_BUF+="${BG_MAIN}${PAD_L_STR}${FG_MUTED}  ${hints}${BG_MAIN}${CLR_EOL}"$'\n'
}

flush_frame() {
    printf "%s\033[H%s%s\033[J%s" "${SYNC_START}" "${FRAME_BUF}" "${BG_MAIN}" "${SYNC_END}"
}

begin_neural_frame() {
    local subtitle="${1:-${APP_SUB}}"
    calc_layout
    FRAME_BUF=""
    buf_blank_line

    local badge
    if [[ ${OLLAMA_INSTALLED} -eq 0 ]]; then
        badge="${BG_BADGE_ERR}${FG_RED}${BOLD} ✕ RUNTIME MISSING ${BG_CARD}"
    elif [[ ${OLLAMA_RUNNING} -eq 1 ]]; then
        badge="${BG_BADGE_OK}${FG_GREEN}${BOLD} ● NEURAL CORE ONLINE (${OLLAMA_VERSION}) ${BG_CARD}"
    else
        badge="${BG_BADGE_ERR}${FG_AMBER}${BOLD} ○ ENGINE STANDBY (${OLLAMA_VERSION}) ${BG_CARD}"
    fi

    buf_box_top "${FG_CYAN}"
    local title_left="${FG_CYAN}${BOLD}◈ ${APP_NAME}${RST}${BG_CARD}"
    strip_ansi_len "${title_left}"
    local l_len=${RET_LEN}
    strip_ansi_len "${badge}"
    local r_len=${RET_LEN}
    local gap=$((BOX_W - 4 - l_len - r_len))
    [[ ${gap} -lt 1 ]] && gap=1
    repeat_char_var " " "${gap}"
    buf_box_line "${title_left}${RET_STR}${badge}" "${FG_CYAN}"

    local sub_left="${FG_VIOLET}${ITALIC}  ${subtitle}${RST}${BG_CARD}"
    local endpoint_right="${FG_MUTED}API: ${FG_SKY}127.0.0.1:11434${RST}${BG_CARD}"
    strip_ansi_len "${sub_left}"
    l_len=${RET_LEN}
    strip_ansi_len "${endpoint_right}"
    r_len=${RET_LEN}
    gap=$((BOX_W - 4 - l_len - r_len))
    [[ ${gap} -lt 1 ]] && gap=1
    repeat_char_var " " "${gap}"
    buf_box_line "${sub_left}${RET_STR}${endpoint_right}" "${FG_CYAN}"
    buf_box_sep "${FG_DIM}"

    # Telemetry Strip (reads cached RAM/GPU metrics)
    make_gauge_var "${RAM_PCT}" 10 "${FG_SKY}"
    local ram_gauge="${RET_STR}"
    truncate_plain_var "${GPU_NAME}" 34
    local gpu_short="${RET_STR}"

    local vram_info=""
    if [[ ${HAS_NVIDIA} -eq 1 ]]; then
        make_gauge_var "${VRAM_PCT}" 10 "${FG_VIOLET}"
        local vram_gauge="${RET_STR}"
        local temp_tag=""
        [[ -n "${GPU_TEMP}" ]] && temp_tag=" ${FG_AMBER}${GPU_TEMP}"
        vram_info="${FG_VIOLET}${BOLD}VRAM${RST}${BG_CARD} ${vram_gauge} ${FG_TEXT}${VRAM_USED_GB}/${VRAM_TOTAL_GB}G${temp_tag}"
    else
        vram_info="${FG_VIOLET}${BOLD}GPU${RST}${BG_CARD} ${FG_TEXT}${gpu_short}"
    fi

    local hw_line="${FG_SKY}${BOLD}RAM${RST}${BG_CARD} ${ram_gauge} ${FG_TEXT}${RAM_USED_GB}/${RAM_TOTAL_GB}G  ${FG_DIM}│${BG_CARD}  ${vram_info}  ${FG_DIM}│${BG_CARD}  ${FG_CYAN}${BOLD}CPU${RST}${BG_CARD} ${FG_TEXT}${CPU_CORES}T  ${FG_DIM}│${BG_CARD}  ${FG_GREEN}${BOLD}MODELS${RST}${BG_CARD} ${FG_TEXT}${#INSTALLED_MODELS[@]}"
    buf_box_line "${hw_line}" "${FG_CYAN}"

    if [[ ${HAS_NVIDIA} -eq 1 ]]; then
        buf_box_line "${FG_MUTED}ACCEL ${FG_DIM}▸ ${FG_TEXT}${gpu_short} ${FG_DIM}(CUDA Ready)${RST}${BG_CARD}" "${FG_CYAN}"
    fi
    buf_box_bottom "${FG_CYAN}"
    buf_blank_line
}

read_key() {
    local key=""
    IFS= read -rsn1 key 2>/dev/null || { echo "ESC"; return; }
    if [[ "${key}" == $'\x1b' ]]; then
        local seq=""
        IFS= read -rsn2 -t 0.02 seq 2>/dev/null || true
        case "${seq}" in
            "[A"|"OA") echo "UP" ;;
            "[B"|"OB") echo "DOWN" ;;
            "[C"|"OC") echo "RIGHT" ;;
            "[D"|"OD") echo "LEFT" ;;
            "")        echo "ESC" ;;
            *)         echo "OTHER" ;;
        esac
    elif [[ "${key}" == "" ]]; then
        echo "ENTER"
    elif [[ "${key}" == $'\x7f' || "${key}" == $'\x08' ]]; then
        echo "BACK"
    else
        echo "${key}"
    fi
}

show_notice() {
    local title="$1"
    local body="$2"
    local accent="${3:-${FG_CYAN}}"

    enter_tui
    begin_neural_frame "${title}"
    buf_box_top "${accent}"
    buf_box_line "${accent}${BOLD}◆ ${title}${RST}${BG_CARD}" "${accent}"
    buf_box_sep "${FG_DIM}"

    while IFS= read -r line; do
        buf_box_line "${FG_TEXT}${line}${RST}${BG_CARD}" "${accent}"
    done <<< "$(printf "%b" "${body}")"

    buf_box_sep "${FG_DIM}"
    buf_box_line "${BG_PILL_CYAN}${FG_DARK}${BOLD}  [ ENTER / ESC ] CONTINUE  ${RST}${BG_CARD}" "${accent}"
    buf_box_bottom "${accent}"
    flush_frame

    while true; do
        local k
        k="$(read_key)"
        [[ "${k}" == "ENTER" || "${k}" == "ESC" || "${k}" == " " || "${k}" == "q" ]] && break
    done
}

ask_confirm() {
    local title="$1"
    local body="$2"
    local sel=0

    enter_tui
    while true; do
        begin_neural_frame "${title}"
        buf_box_top "${FG_AMBER}"
        buf_box_line "${FG_AMBER}${BOLD}▲ ${title}${RST}${BG_CARD}" "${FG_AMBER}"
        buf_box_sep "${FG_DIM}"

        while IFS= read -r line; do
            buf_box_line "${FG_TEXT}${line}${RST}${BG_CARD}" "${FG_AMBER}"
        done <<< "$(printf "%b" "${body}")"

        buf_box_sep "${FG_DIM}"
        local btn_yes btn_no
        if [[ ${sel} -eq 0 ]]; then
            btn_yes="${BG_PILL_CYAN}${FG_DARK}${BOLD} ▸ CONFIRM (YES) ${RST}${BG_CARD}"
            btn_no="${FG_MUTED}   CANCEL (NO)   ${RST}${BG_CARD}"
        else
            btn_yes="${FG_MUTED}   CONFIRM (YES)   ${RST}${BG_CARD}"
            btn_no="${BG_PILL_VIO}${FG_TEXT}${BOLD} ▸ CANCEL (NO)   ${RST}${BG_CARD}"
        fi
        buf_box_line "${btn_yes}    ${btn_no}" "${FG_AMBER}"
        buf_box_bottom "${FG_AMBER}"
        buf_footer_hints "[←/→] Toggle   [Enter] Confirm   [Esc] Cancel"
        flush_frame

        local k
        k="$(read_key)"
        case "${k}" in
            LEFT|RIGHT|UP|DOWN) sel=$((1 - sel)) ;;
            y|Y) return 0 ;;
            n|N|ESC|q) return 1 ;;
            ENTER) return ${sel} ;;
        esac
    done
}

RET_INPUT=""

prompt_input() {
    local title="$1"
    local prompt_txt="$2"
    local default_val="${3:-}"
    local is_secret="${4:-0}"
    RET_INPUT=""

    enter_tui
    begin_neural_frame "${title}"
    buf_box_top "${FG_VIOLET}"
    buf_box_line "${FG_VIOLET}${BOLD}◈ ${title}${RST}${BG_CARD}" "${FG_VIOLET}"
    buf_box_sep "${FG_DIM}"

    while IFS= read -r line; do
        buf_box_line "${FG_TEXT}${line}${RST}${BG_CARD}" "${FG_VIOLET}"
    done <<< "$(printf "%b" "${prompt_txt}")"

    buf_box_line "" "${FG_VIOLET}"
    buf_box_line "${FG_MUTED}Tekan [Enter] untuk lanjut, atau kosongkan lalu [Enter] untuk batal.${RST}${BG_CARD}" "${FG_VIOLET}"
    buf_box_bottom "${FG_VIOLET}"
    flush_frame

    # Aktifkan mode ketik normal & tampilkan kursor
    stty sane 2>/dev/null || true
    printf "%s%s\n" "${BG_MAIN}" "${CUR_SHOW}"

    local user_val=""
    local rl_prompt=$'\001'"${BG_MAIN}${FG_CYAN}${BOLD}"$'\002'"${PAD_L_STR}▸ Input: "$'\001'"${RST}${BG_MAIN}${FG_TEXT}"$'\002'

    if [[ ${is_secret} -eq 1 ]]; then
        printf "%s%s%s▸ Input: %s" "${PAD_L_STR}" "${FG_CYAN}" "${BOLD}" "${RST}${BG_MAIN}${FG_TEXT}"
        IFS= read -rs user_val < /dev/tty || {
            stty -echo -icanon min 1 time 0 2>/dev/null || true
            printf "%s" "${CUR_HIDE}"
            return 1
        }
        echo ""
    else
        if [[ -n "${default_val}" ]]; then
            IFS= read -e -i "${default_val}" -p "${rl_prompt}" -r user_val < /dev/tty || {
                stty -echo -icanon min 1 time 0 2>/dev/null || true
                printf "%s" "${CUR_HIDE}"
                return 1
            }
        else
            IFS= read -e -p "${rl_prompt}" -r user_val < /dev/tty || {
                stty -echo -icanon min 1 time 0 2>/dev/null || true
                printf "%s" "${CUR_HIDE}"
                return 1
            }
        fi
    fi

    # Kembalikan mode raw TUI agar navigasi panah menu tidak memunculkan ^[[A
    stty -echo -icanon min 1 time 0 2>/dev/null || true
    printf "%s" "${CUR_HIDE}"

    RET_INPUT="${user_val}"
    return 0
}

# ==============================================================================
# 5. INTERACTIVE OLLAMA INSTALLER & SERVICE CONTROLLER
# ==============================================================================
workflow_install_ollama() {
    local lang
    lang="$(get_lang)"

    local title prompt_pw
    if [[ "${lang}" == "id" ]]; then
        title="NEURAL RUNTIME INSTALLER"
        prompt_pw="Installer resmi Ollama akan dijalankan:\n  curl -fsSL https://ollama.com/install.sh | sh\n\nMasukkan password sudo Linux Anda (kosongkan jika passwordless sudo):"
    else
        title="NEURAL RUNTIME INSTALLER"
        prompt_pw="The official Ollama installer will execute:\n  curl -fsSL https://ollama.com/install.sh | sh\n\nEnter your Linux sudo password (leave blank if passwordless sudo):"
    fi

    local sudo_pw=""
    if ! sudo -n true 2>/dev/null; then
        prompt_input "${title}" "${prompt_pw}" "" 1 || return
        sudo_pw="${RET_INPUT}"
    fi

    leave_tui
    printf "%s\033[H\033[2J" "${BG_MAIN}"
    echo -e "${BG_PILL_CYAN}${FG_DARK}${BOLD}  ◈ ARI-DEV NEURAL RUNTIME INSTALLER  ${RST}\n"

    if [[ -n "${sudo_pw}" ]]; then
        if ! printf "%s\n" "${sudo_pw}" | sudo -S -v 2>/dev/null; then
            echo -e "${FG_RED}[✕] Password sudo salah / Incorrect sudo password.${RST}"
            read -rp "Press Enter to continue..."
            enter_tui
            return
        fi
    fi

    echo -e "${FG_CYAN}[1/3] Downloading & executing official Ollama runtime installer...${RST}"
    curl -fsSL https://ollama.com/install.sh | sh
    local install_rc=$?

    if [[ ${install_rc} -ne 0 ]]; then
        echo -e "\n${FG_RED}[✕] Installer exited with code ${install_rc}.${RST}"
        read -rp "Press Enter to continue..."
        enter_tui
        return
    fi

    echo -e "\n${FG_CYAN}[2/3] Enabling & starting systemd neural daemon...${RST}"
    if [[ -n "${sudo_pw}" ]]; then
        printf "%s\n" "${sudo_pw}" | sudo -S systemctl enable --now ollama 2>/dev/null || true
    else
        sudo -n systemctl enable --now ollama 2>/dev/null || true
    fi

    sleep 1
    if ! curl -sf --max-time 2 "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
        echo -e "${FG_MUTED}  Launching fallback daemon: ollama serve &${RST}"
        nohup ollama serve >/dev/null 2>&1 &
    fi

    echo -e "\n${FG_CYAN}[3/3] Handshaking with local API http://127.0.0.1:11434 ...${RST}"
    local ready=0
    for _ in $(seq 1 15); do
        if curl -sf --max-time 2 "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
            ready=1
            break
        fi
        sleep 1
    done

    if [[ ${ready} -eq 1 ]]; then
        echo -e "\n${FG_GREEN}${BOLD}✓ SUCCESS! Neural Engine active at ${OLLAMA_BASE_URL}.${RST}"
    else
        echo -e "\n${FG_AMBER}▲ Installed, but daemon did not respond yet. Toggle service from dashboard.${RST}"
    fi
    sleep 1.5
    enter_tui
}

toggle_ollama_service() {
    local force_start="${1:-0}"
    detect_ollama_state

    if [[ ${OLLAMA_INSTALLED} -eq 0 ]]; then
        workflow_install_ollama
        return
    fi

    leave_tui
    printf "%s\033[H\033[2J" "${BG_MAIN}"
    echo -e "${BG_PILL_VIO}${FG_TEXT}${BOLD}  ◈ ARI-DEV NEURAL SERVICE CONTROLLER  ${RST}\n"

    if [[ ${OLLAMA_RUNNING} -eq 0 || ${force_start} -eq 1 ]]; then
        echo -e "${FG_CYAN}[▸] Igniting Ollama background service...${RST}"
        sudo -n systemctl start ollama 2>/dev/null || true
        sleep 1
        if ! curl -sf --max-time 2 "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
            nohup ollama serve >/dev/null 2>&1 &
            sleep 2
        fi
        echo -e "${FG_GREEN}[✓] Neural Engine is now ONLINE.${RST}"
    else
        echo -e "${FG_AMBER}[▸] Suspending Ollama background service...${RST}"
        sudo -n systemctl stop ollama 2>/dev/null || pkill -x ollama 2>/dev/null || true
        sleep 1
        echo -e "${FG_AMBER}[✓] Neural Engine is now STANDBY.${RST}"
    fi
    sleep 1
    enter_tui
}

pull_model_live() {
    local model_name="$1"
    [[ -z "${model_name}" ]] && return

    leave_tui
    printf "%s\033[H\033[2J" "${BG_MAIN}"
    echo -e "${BG_PILL_CYAN}${FG_DARK}${BOLD}  ◈ NEURAL WEIGHTS DOWNLOADER: ${model_name}  ${RST}\n"

    echo -e "${FG_CYAN}[1/4] Memeriksa runtime Ollama...${RST}"
    detect_ollama_state
    if [[ ${OLLAMA_INSTALLED} -eq 0 ]]; then
        echo -e "${FG_AMBER}  ▸ Ollama belum terpasang, membuka installer...${RST}"
        workflow_install_ollama
        detect_ollama_state
        if [[ ${OLLAMA_INSTALLED} -eq 0 ]]; then
            echo -e "${FG_RED}[✕] Runtime Ollama tidak tersedia. Proses dibatalkan.${RST}"
            read -rp "Tekan Enter untuk kembali..."
            enter_tui
            return
        fi
    fi
    echo -e "${FG_GREEN}  ✓ Runtime terdeteksi (${OLLAMA_VERSION})${RST}"

    echo -e "\n${FG_CYAN}[2/4] Memeriksa status daemon Ollama (${OLLAMA_BASE_URL})...${RST}"
    if [[ ${OLLAMA_RUNNING} -eq 0 ]]; then
        echo -e "${FG_AMBER}  ▸ Daemon standby, menyalakan service Ollama...${RST}"
        sudo -n systemctl start ollama 2>/dev/null || true
        if ! curl -sf --max-time 2 "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
            nohup ollama serve >/dev/null 2>&1 &
        fi

        local ready=0
        for sec in $(seq 1 10); do
            printf "\r${FG_MUTED}  ▸ Menunggu API siap (%ds/10s)...${RST}" "${sec}"
            if curl -sf --max-time 1 "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
                ready=1
                break
            fi
            sleep 1
        done
        echo ""

        if [[ ${ready} -eq 0 ]]; then
            echo -e "${FG_RED}[✕] Daemon Ollama gagal merespons di ${OLLAMA_BASE_URL}.${RST}"
            read -rp "Tekan Enter untuk kembali..."
            enter_tui
            return
        fi
    fi
    echo -e "${FG_GREEN}  ✓ Neural Daemon ONLINE${RST}"

    echo -e "\n${FG_CYAN}[3/4] Menghubungi Ollama Registry & mengunduh '${model_name}'...${RST}"
    echo -e "${FG_MUTED}  ▸ Mengambil manifest & layer dari registry.ollama.ai (tekan Ctrl+C untuk batal)${RST}\n"

    local pull_aborted=0
    trap 'pull_aborted=1' INT
    ollama pull "${model_name}"
    local rc=$?
    trap cleanup EXIT INT TERM

    echo -e "\n${FG_CYAN}[4/4] Verifikasi akhir...${RST}"
    if [[ ${pull_aborted} -eq 1 ]]; then
        echo -e "${FG_AMBER}[!] Proses unduh dibatalkan oleh pengguna.${RST}"
    elif [[ ${rc} -eq 0 ]]; then
        detect_ollama_state
        echo -e "${FG_GREEN}${BOLD}[✓] Model '${model_name}' siap digunakan! (Total lokal: ${#INSTALLED_MODELS[@]} model)${RST}"
    else
        echo -e "${FG_RED}${BOLD}[✕] Gagal mengunduh '${model_name}' (exit code: ${rc}). Pastikan nama tag valid.${RST}"
    fi

    echo ""
    read -rp "Tekan Enter untuk kembali ke dashboard..."
    enter_tui
}

delete_model_prompt() {
    local model_name="$1"
    local lang
    lang="$(get_lang)"

    local title msg
    if [[ "${lang}" == "id" ]]; then
        title="PURGE MODEL WEIGHTS"
        msg="Hapus permanen model berikut dari penyimpanan lokal?\n\n  ◆ ${model_name}"
    else
        title="PURGE MODEL WEIGHTS"
        msg="Permanently remove this model from local storage?\n\n  ◆ ${model_name}"
    fi

    if ask_confirm "${title}" "${msg}"; then
        leave_tui
        printf "%s\033[H\033[2J" "${BG_MAIN}"
        echo -e "${FG_AMBER}[▸] Purging ${model_name}...${RST}"
        ollama rm "${model_name}"
        sleep 1
        enter_tui
    fi
}

# ==============================================================================
# 6. FUTURISTIC STREAMING NEURAL CHAT (MARKDOWN FORMATTER & CODE COPY)
# ==============================================================================
style_inline_md() {
    local s="$1"
    local tick=$'\x60'
    while [[ "$s" == *"**"*"**"* ]]; do
        local before="${s%%\*\**}"
        local rest="${s#*\*\*}"
        local mid="${rest%%\*\**}"
        local after="${rest#*\*\*}"
        s="${before}${BOLD}${FG_TEXT}${mid}${RST}${FG_TEXT}${after}"
    done
    while [[ "$s" == *"${tick}"*"${tick}"* ]]; do
        local before="${s%%"${tick}"*}"
        local rest="${s#*"${tick}"}"
        local mid="${rest%%"${tick}"*}"
        local after="${rest#*"${tick}"}"
        s="${before}${FG_AMBER}${mid}${FG_TEXT}${after}"
    done
    RET_STR="${s}"
}

open_local_chat() {
    local model_name="$1"
    local lang
    lang="$(get_lang)"

    detect_ollama_state
    if [[ ${OLLAMA_RUNNING} -eq 0 ]]; then
        show_notice "ENGINE STANDBY" "Ollama service sedang berhenti.\nJalankan 'Start / Stop Ollama Service' terlebih dahulu." "${FG_AMBER}"
        return
    fi

    leave_tui
    printf "%s\033[H\033[2J" "${BG_MAIN}"
    echo -e "${FG_CYAN}${BOLD}╭──────────────────────────────────────────────────────────────────────────────────────╮${RST}"
    echo -e "${FG_CYAN}${BOLD}│ ◈ NEURAL STREAMING SESSION  ${FG_DIM}•  ${FG_VIOLET}MODEL: ${FG_TEXT}${model_name}${RST}"
    if [[ "${lang}" == "id" ]]; then
        echo -e "${FG_CYAN}${BOLD}│ ${FG_MUTED}Perintah: ${FG_SKY}/copy [n]${FG_MUTED} (salin kode) • ${FG_SKY}/last${FG_MUTED} (salin teks) • ${FG_SKY}/clear${FG_MUTED} • ${FG_SKY}/exit${RST}"
    else
        echo -e "${FG_CYAN}${BOLD}│ ${FG_MUTED}Commands: ${FG_SKY}/copy [n]${FG_MUTED} (copy code) • ${FG_SKY}/last${FG_MUTED} (copy reply) • ${FG_SKY}/clear${FG_MUTED} • ${FG_SKY}/exit${RST}"
    fi
    echo -e "${FG_CYAN}${BOLD}╰──────────────────────────────────────────────────────────────────────────────────────╯${RST}\n"

    local history_json="[]"
    local turn_count=0
    local last_code_count=0
    local last_code_langs=()

    local in_code=0
    local code_idx=0
    local wrap_w=86
    local tick=$'\x60'
    local fence="${tick}${tick}${tick}"

    render_chat_line() {
        local raw_line="${1%$'\r'}"
        local trimmed_line="${raw_line#"${raw_line%%[![:space:]]*}"}"

        # Deteksi pembuka / penutup blok kode
        if [[ "${trimmed_line}" == "${fence}"* ]]; then
            local fence_lang="${trimmed_line#"${fence}"}"
            fence_lang="$(echo "${fence_lang}" | xargs)"
            if [[ ${in_code} -eq 0 ]]; then
                in_code=1
                code_idx=$((code_idx + 1))
                [[ -z "${fence_lang}" ]] && fence_lang="code"
                last_code_langs[${code_idx}]="${fence_lang}"
                : > "${TMP_DIR}/code_${code_idx}.txt"
                printf "%s│ %s┌─ CODE #%d (%s) ────────────────────────────────────────────────────%s\n" \
                    "${FG_CYAN}" "${FG_VIOLET}${BOLD}" "${code_idx}" "${fence_lang}" "${RST}"
            else
                in_code=0
                printf "%s│ %s└─ [Ketik /copy atau /copy %d untuk salin kode] ──────────────────────%s\n" \
                    "${FG_CYAN}" "${FG_MUTED}" "${code_idx}" "${RST}"
            fi
            return
        fi

        # Konten di dalam blok kode
        if [[ ${in_code} -eq 1 ]]; then
            printf "%s\n" "${raw_line}" >> "${TMP_DIR}/code_${code_idx}.txt"
            printf "%s│ %s│ %s%s%s\n" "${FG_CYAN}" "${FG_VIOLET}" "${FG_SKY}" "${raw_line}" "${RST}"
            return
        fi

        # Baris kosong di luar blok kode
        if [[ -z "${raw_line}" ]]; then
            printf "%s│%s\n" "${FG_CYAN}" "${RST}"
            return
        fi

        # Deteksi heading Markdown (#, ##, ###)
        local is_heading=0
        local clean_line="${raw_line}"
        if [[ "${trimmed_line}" =~ ^#{1,4}[[:space:]]+(.*)$ ]]; then
            is_heading=1
            clean_line="▸ ${BASH_REMATCH[1]}"
        fi

        # Word-wrap rapi agar tidak terpotong di tengah kata
        while IFS= read -r wline; do
            if [[ ${is_heading} -eq 1 ]]; then
                printf "%s│ %s%s%s%s\n" "${FG_CYAN}" "${FG_CYAN}${BOLD}" "${wline}" "${RST}"
            else
                style_inline_md "${wline}"
                printf "%s│ %s%s%s\n" "${FG_CYAN}" "${FG_TEXT}" "${RET_STR}" "${RST}"
            fi
        done < <(printf '%s\n' "${clean_line}" | fold -s -w "${wrap_w}")
    }

    while true; do
        printf "%s%s╭─ YOU %s[%d]%s\n%s╰─▸ %s" "${FG_VIOLET}" "${BOLD}" "${FG_MUTED}" "$((turn_count + 1))" "${RST}" "${FG_VIOLET}" "${RST}"
        local user_input=""
        IFS= read -r user_input || break

        [[ -z "${user_input}" ]] && continue
        case "${user_input}" in
            /exit|/quit) break ;;
        esac

        if [[ "${user_input}" == "/clear" ]]; then
            history_json="[]"
            turn_count=0
            last_code_count=0
            echo -e "${FG_AMBER}[✦] Neural context window cleared.${RST}\n"
            continue
        fi

        # Fitur salin seluruh respons terakhir
        if [[ "${user_input}" == "/last" ]]; then
            if [[ -s "${TMP_DIR}/last_reply.txt" ]]; then
                local full_txt
                full_txt="$(cat "${TMP_DIR}/last_reply.txt")"
                if copy_to_clipboard "${full_txt}"; then
                    echo -e "${FG_GREEN}[✓] Seluruh respons terakhir berhasil disalin ke clipboard!${RST}\n"
                else
                    echo -e "${FG_AMBER}[!] Clipboard tool (xclip/wl-copy) belum terpasang. Install: sudo apt install xclip${RST}\n"
                fi
            else
                echo -e "${FG_AMBER}[!] Belum ada respons AI untuk disalin.${RST}\n"
            fi
            continue
        fi

        # Fitur salin blok kode (/copy, /copy 1, /copy 2, /copy all)
        case "${user_input}" in
            /copy|/copy\ *)
                local arg="${user_input#/copy}"
                arg="$(echo "${arg}" | xargs)"

                if [[ ${last_code_count} -eq 0 ]]; then
                    echo -e "${FG_AMBER}[!] Tidak ditemukan blok kode pada respons terakhir.${RST}\n"
                    continue
                fi

                if [[ "${arg}" == "all" ]]; then
                    local all_code=""
                    for ((c = 1; c <= last_code_count; c++)); do
                        [[ -f "${TMP_DIR}/code_${c}.txt" ]] && all_code+="$(cat "${TMP_DIR}/code_${c}.txt")"$'\n\n'
                    done
                    if copy_to_clipboard "${all_code}"; then
                        echo -e "${FG_GREEN}[✓] Semua (${last_code_count}) blok kode berhasil disalin ke clipboard!${RST}\n"
                    else
                        echo -e "${FG_AMBER}[!] Clipboard tool (xclip/wl-copy) belum terpasang. Install: sudo apt install xclip${RST}\n"
                    fi
                    continue
                fi

                local target_idx=1
                if [[ -n "${arg}" ]]; then
                    if [[ "${arg}" =~ ^[0-9]+$ && "${arg}" -ge 1 && "${arg}" -le ${last_code_count} ]]; then
                        target_idx=${arg}
                    else
                        echo -e "${FG_RED}[✕] Nomor blok kode tidak valid. Tersedia: 1 s/d ${last_code_count}.${RST}\n"
                        continue
                    fi
                fi

                local code_file="${TMP_DIR}/code_${target_idx}.txt"
                if [[ -f "${code_file}" ]]; then
                    local code_content line_cnt
                    code_content="$(cat "${code_file}")"
                    line_cnt="$(wc -l < "${code_file}" | xargs)"
                    if copy_to_clipboard "${code_content}"; then
                        echo -e "${FG_GREEN}[✓] Code #${target_idx} (${last_code_langs[${target_idx}]:-code}, ${line_cnt} baris) berhasil disalin ke clipboard!${RST}\n"
                    else
                        echo -e "${FG_AMBER}[!] Install xclip (sudo apt install xclip) untuk auto-clipboard. File tersimpan di: ${code_file}${RST}\n"
                    fi
                fi
                continue
                ;;
        esac

        # Hitung lebar wrap adaptif mengikuti terminal saat ini
        local cols="${COLUMNS:-0}"
        [[ ${cols} -le 0 ]] && cols="$(tput cols 2>/dev/null || echo 96)"
        wrap_w=$((cols - 6))
        [[ ${wrap_w} -gt 92 ]] && wrap_w=92
        [[ ${wrap_w} -lt 40 ]] && wrap_w=40

        turn_count=$((turn_count + 1))
        local payload
        if [[ "${HAS_JQ}" -eq 1 ]]; then
            history_json="$(echo "${history_json}" | jq -c --arg content "${user_input}" '. + [{"role":"user","content":$content}]')"
            payload="$(jq -nc --arg model "${model_name}" --argjson msgs "${history_json}" '{"model":$model,"messages":$msgs,"stream":true}')"
        else
            local escaped_input
            escaped_input="$(printf '%s' "${user_input}" | sed 's/\\/\\\\/g; s/"/\\"/g')"
            payload="{\"model\":\"${model_name}\",\"messages\":[{\"role\":\"user\",\"content\":\"${escaped_input}\"}],\"stream\":true}"
        fi

        echo ""
        printf "%s%s╭─ AI // %s%s\n" "${FG_CYAN}" "${BOLD}" "${model_name}" "${RST}"

        mkdir -p "${TMP_DIR}"
        rm -f "${TMP_DIR}"/code_*.txt
        local reply_file="${TMP_DIR}/last_reply.txt"
        local stats_file="${TMP_DIR}/last_stats.txt"
        : > "${reply_file}"
        : > "${stats_file}"

        in_code=0
        code_idx=0
        last_code_langs=()
        local line_buf=""

        while IFS= read -r line; do
            [[ -z "${line}" ]] && continue
            local token=""
            if [[ "${HAS_JQ}" -eq 1 ]]; then
                token="$(printf '%s' "${line}" | jq -j '(.message.content // "") + "x"' 2>/dev/null)"
                token="${token%x}"
                if printf '%s' "${line}" | grep -q '"done":true'; then
                    printf '%s' "${line}" | jq -r '"Tokens: " + ((.eval_count // 0) | tostring) + " | Speed: " + ((((.eval_count // 0) / (((.eval_duration // 1) | if . <= 0 then 1 else . end) / 1000000000)) * 10 | round / 10) | tostring) + " tok/s | Latency: " + ((((.total_duration // 0) / 1000000000) * 100 | round / 100) | tostring) + "s"' 2>/dev/null > "${stats_file}" || true
                fi
            else
                token="$(printf '%s' "${line}" | sed -n 's/.*"content":"\([^"]*\)".*/\1/p' | sed 's/\\n/\n/g; s/\\"/"/g')"
            fi

            if [[ -n "${token}" ]]; then
                printf "%s" "${token}" >> "${reply_file}"
                line_buf+="${token}"
                while [[ "${line_buf}" == *$'\n'* ]]; do
                    local one_line="${line_buf%%$'\n'*}"
                    line_buf="${line_buf#*$'\n'}"
                    render_chat_line "${one_line}"
                done
            fi
        done < <(curl -sN -X POST "${OLLAMA_BASE_URL}/api/chat" -H "Content-Type: application/json" -d "${payload}")

        if [[ -n "${line_buf}" ]]; then
            render_chat_line "${line_buf}"
            line_buf=""
        fi
        if [[ ${in_code} -eq 1 ]]; then
            in_code=0
            printf "%s│ %s└─ [Ketik /copy atau /copy %d untuk salin kode] ──────────────────────%s\n" \
                "${FG_CYAN}" "${FG_MUTED}" "${code_idx}" "${RST}"
        fi

        last_code_count=${code_idx}

        local code_hint=""
        if [[ ${last_code_count} -gt 0 ]]; then
            code_hint="  ${FG_DIM}│  ${FG_VIOLET}${last_code_count} code block(s) ready (/copy)"
        fi

        if [[ -s "${stats_file}" ]]; then
            printf "%s╰─ ✦ %s%s%s%s\n\n" "${FG_CYAN}" "${FG_GREEN}" "$(cat "${stats_file}")" "${code_hint}" "${RST}"
        else
            printf "%s╰─ ✦ Stream complete%s%s\n\n" "${FG_CYAN}" "${code_hint}" "${RST}"
        fi

        if [[ "${HAS_JQ}" -eq 1 && -s "${reply_file}" ]]; then
            local full_reply
            full_reply="$(cat "${reply_file}")"
            history_json="$(echo "${history_json}" | jq -c --arg content "${full_reply}" '. + [{"role":"assistant","content":$content}]')"
        fi
    done

    enter_tui
}

# ==============================================================================
# 7. MODEL STORE & HARDWARE MATCHING (models_db.json)
# ==============================================================================
WRAP_LINES=()
wrap_text_var() {
    local text="$1"
    local max_w="$2"
    WRAP_LINES=()
    [[ -z "${text}" ]] && return

    local line=""
    local word=""
    for word in ${text}; do
        if [[ -z "${line}" ]]; then
            line="${word}"
        elif (( ${#line} + 1 + ${#word} <= max_w )); then
            line+=" ${word}"
        else
            WRAP_LINES+=("${line}")
            line="${word}"
        fi
    done
    [[ -n "${line}" ]] && WRAP_LINES+=("${line}")
}

get_scored_models_lines() {
    local lang="$1"
    local desc_field="description_${lang}"

    if [[ "${HAS_JQ}" -eq 1 ]]; then
        jq -r ".[] | \"\(.name)|\(.min_ram_gb)|\(.min_vram_gb)|\(.size)|\(.category // \"General\")|\(.[ \"${desc_field}\" ] // .description_en // .description_id // \"-\")\"" "${DB_PATH}" | while IFS='|' read -r name mram mvram size cat desc; do
            local fit_res score tier
            fit_res="$(evaluate_fit "${mram}" "${mvram}")"
            score="${fit_res%%|*}"
            tier="${fit_res##*|}"
            echo "${score}|${tier}|${name}|${size}|${mram}G/${mvram}G|${cat}|${desc}"
        done | sort -t'|' -k1,1nr
    else
        echo "3|optimal|qwen2.5-coder:1.5b-instruct|986 MB|4G/2G|Coding / Light|Sangat cepat & ringan untuk coding harian."
        echo "3|optimal|gemma2:2b|1.6 GB|6G/3G|General / Light|Responsif & pemahaman bahasa Indonesia bagus."
        echo "3|optimal|qwen2.5-coder:3b|1.9 GB|8G/3G|Coding / Medium|Seimbang untuk code completion & refactoring."
        echo "2|compat|phi3:3.8b|2.2 GB|8G/4G|Reasoning / Medium|Kuat untuk penalaran logika, matematika & koding."
        echo "2|compat|llama3.2:3b|2.0 GB|8G/4G|General / Medium|Cerdas untuk asisten teks umum & ringkasan."
        echo "1|compat|qwen2.5:7b-instruct|4.7 GB|16G/6G|General / Heavy|Performa tinggi untuk tugas kompleks."
        echo "1|compat|deepseek-r1:7b|4.7 GB|16G/6G|Reasoning / Heavy|Model reasoning mendalam bertahap."
    fi
}

matches_category_filter() {
    local flt="$1"
    local blob="${2,,} ${3,,} ${4,,}"
    case "${flt}" in
        ALL)
            return 0
            ;;
        CODING)
            case "${blob}" in
                *cod*|*sql*|*tool*|*program*|*pemrograman*) return 0 ;;
            esac
            ;;
        REASONING)
            case "${blob}" in
                *reason*|*logic*|*penalaran*|*logika*|*r1*|*math*) return 0 ;;
            esac
            ;;
        VISION)
            case "${blob}" in
                *vision*|*multimodal*|*llava*|*moondream*|*minicpm-v*|*gambar*|*image*) return 0 ;;
            esac
            ;;
        GENERAL)
            case "${blob}" in
                *general*|*umum*|*enterprise*|*assistant*) return 0 ;;
            esac
            ;;
    esac
    return 1
}

menu_model_store() {
    local lang
    lang="$(get_lang)"
    detect_ollama_state

    local all_names=() all_tiers=() all_sizes=() all_reqs=() all_cats=() all_descs=()
    while IFS='|' read -r score tier name size req cat desc; do
        all_names+=("${name}")
        all_tiers+=("${tier}")
        all_sizes+=("${size}")
        all_reqs+=("${req}")
        all_cats+=("${cat}")
        all_descs+=("${desc}")
    done < <(get_scored_models_lines "${lang}")

    local master_total=${#all_names[@]}
    [[ ${master_total} -eq 0 ]] && return

    local filters=("ALL" "CODING" "REASONING" "VISION" "GENERAL")
    local filter_idx=0
    local cursor=0
    local offset=0

    while true; do
        local cur_filter="${filters[$filter_idx]}"
        local names=() tiers=() sizes=() reqs=() cats=() descs=()

        for ((m = 0; m < master_total; m++)); do
            if matches_category_filter "${cur_filter}" "${all_cats[$m]}" "${all_names[$m]}" "${all_descs[$m]}"; then
                names+=("${all_names[$m]}")
                tiers+=("${all_tiers[$m]}")
                sizes+=("${all_sizes[$m]}")
                reqs+=("${all_reqs[$m]}")
                cats+=("${all_cats[$m]}")
                descs+=("${all_descs[$m]}")
            fi
        done

        local total=${#names[@]}
        [[ ${cursor} -ge ${total} && ${total} -gt 0 ]] && cursor=$((total - 1))
        [[ ${total} -eq 0 ]] && cursor=0

        begin_neural_frame "NEURAL MODEL STORE • HARDWARE MATCHED (${RAM_TOTAL_GB}G RAM / ${VRAM_TOTAL_GB}G VRAM)"

        # Kapasitas baris 1-line item agar header RAM/VRAM atas selalu tampil penuh
        local rows="${LINES:-0}"
        if [[ ${rows} -le 0 ]]; then
            rows="$(tput lines 2>/dev/null)"
            [[ -z "${rows}" ]] && rows=36
        fi
        local page_size=$((rows - 20))
        [[ ${page_size} -lt 5 ]] && page_size=5
        [[ ${page_size} -gt 9 ]] && page_size=9

        if [[ ${cursor} -lt ${offset} ]]; then
            offset=${cursor}
        elif [[ ${cursor} -ge $((offset + page_size)) ]]; then
            offset=$((cursor - page_size + 1))
        fi

        local end_idx=$((offset + page_size))
        [[ ${end_idx} -gt ${total} ]] && end_idx=${total}
        local visible_count=$((end_idx - offset))

        local cur_page=1
        local total_pages=1
        if [[ ${total} -gt 0 ]]; then
            cur_page=$(( (cursor / page_size) + 1 ))
            total_pages=$(( (total + page_size - 1) / page_size ))
        fi

        local name_col_w=28
        local spec_col_w=16
        if [[ ${BOX_W} -lt 92 ]]; then
            name_col_w=21
            spec_col_w=14
        fi

        buf_box_top "${FG_VIOLET}"

        local item_stat="0/0"
        [[ ${total} -gt 0 ]] && item_stat="$((cursor + 1))/${total}"
        local hdr_left="${FG_VIOLET}${BOLD}◈ CURATED NEURAL MODELS  ${FG_DIM}•  ${FG_AMBER}[FILTER: ${cur_filter}]${RST}${BG_CARD}"
        local hdr_right="${FG_MUTED}ITEM ${FG_CYAN}${item_stat}${FG_MUTED}  •  PAGE ${cur_page}/${total_pages}${RST}${BG_CARD}"

        strip_ansi_len "${hdr_left}"
        local hl_len=${RET_LEN}
        strip_ansi_len "${hdr_right}"
        local hr_len=${RET_LEN}
        local hdr_gap=$((BOX_W - 4 - hl_len - hr_len))
        [[ ${hdr_gap} -lt 1 ]] && hdr_gap=1
        repeat_char_var " " "${hdr_gap}"
        buf_box_line "${hdr_left}${RET_STR}${hdr_right}" "${FG_VIOLET}"
        buf_box_sep "${FG_DIM}"

        if [[ ${total} -eq 0 ]]; then
            buf_box_line "${FG_AMBER}  Tidak ada model untuk kategori '${cur_filter}'. Tekan [F] untuk ganti filter.${RST}${BG_CARD}" "${FG_VIOLET}"
        else
            for ((i = offset; i < end_idx; i++)); do
                local mname="${names[$i]}"
                local mtier="${tiers[$i]}"
                local msize="${sizes[$i]}"
                local mreq="${reqs[$i]}"
                local page_slot=$((i - offset + 1))

                truncate_plain_var "${mname}" $((name_col_w - 1))
                local disp_name="${RET_STR}"
                repeat_char_var " " $((name_col_w - ${#disp_name}))
                local name_pad="${RET_STR}"

                local fit_badge
                if [[ "${mtier}" == "optimal" ]]; then
                    fit_badge="${FG_GREEN}[■■■■■ OPTIMAL]${RST}"
                elif [[ "${mtier}" == "heavy" ]]; then
                    fit_badge="${FG_RED}[■□□□□ HEAVY  ]${RST}"
                else
                    fit_badge="${FG_SKY}[■■■□□ COMPAT ]${RST}"
                fi

                local spec_raw="${msize} (${mreq})"
                truncate_plain_var "${spec_raw}" "${spec_col_w}"
                local disp_spec="${RET_STR}"
                repeat_char_var " " $((spec_col_w - ${#disp_spec}))
                local spec_pad="${RET_STR}"

                local inst_tag=""
                for im in "${INSTALLED_MODELS[@]}"; do
                    local iname="${im%%|*}"
                    case "${iname}" in
                        "${mname}"|"${mname}:"*)
                            inst_tag="${FG_GREEN}${BOLD}✓ INSTALLED${RST}"
                            break
                            ;;
                    esac
                done

                local row_bg="${BG_CARD}"
                local prefix="  "
                local num_col="${FG_MUTED}"
                local name_col="${FG_TEXT}"
                if [[ ${i} -eq ${cursor} ]]; then
                    row_bg="${BG_SEL}"
                    prefix="${FG_CYAN}${BOLD}▸ "
                    num_col="${FG_CYAN}${BOLD}"
                    name_col="${FG_CYAN}${BOLD}"
                fi

                local left_part="${prefix}${num_col}[${page_slot}] ${name_col}${disp_name}${name_pad}${RST}${row_bg}  ${fit_badge}${row_bg}  ${FG_MUTED}${disp_spec}${spec_pad}${RST}${row_bg}"
                local right_part="${inst_tag}${row_bg}"

                strip_ansi_len "${left_part}"
                local l_len=${RET_LEN}
                strip_ansi_len "${right_part}"
                local r_len=${RET_LEN}
                local row_gap=$((BOX_W - 4 - l_len - r_len))
                [[ ${row_gap} -lt 1 ]] && row_gap=1
                repeat_char_var " " "${row_gap}"

                buf_box_line "${left_part}${RET_STR}${right_part}" "${FG_VIOLET}" "${row_bg}"
            done

            # Panel FULL INFO dengan Category, spesifikasi, status & deskripsi lengkap
            local sel_name="${names[$cursor]}"
            local sel_cat="${cats[$cursor]}"
            local sel_size="${sizes[$cursor]}"
            local sel_req="${reqs[$cursor]}"
            local sel_tier="${tiers[$cursor]}"
            local sel_desc="${descs[$cursor]}"

            local sel_fit_lbl="${FG_SKY}Compatible (Hybrid)"
            [[ "${sel_tier}" == "optimal" ]] && sel_fit_lbl="${FG_GREEN}Optimal (GPU Fit)"
            [[ "${sel_tier}" == "heavy" ]] && sel_fit_lbl="${FG_RED}Heavy (High RAM)"

            local sel_status_lbl="${FG_AMBER}Not Installed"
            for im in "${INSTALLED_MODELS[@]}"; do
                local iname="${im%%|*}"
                case "${iname}" in
                    "${sel_name}"|"${sel_name}:"*)
                        sel_status_lbl="${FG_GREEN}${BOLD}Installed"
                        break
                        ;;
                esac
            done

            buf_box_sep "${FG_DIM}"
            buf_box_line "${FG_CYAN}${BOLD}◈ FULL INFO: ${FG_TEXT}${sel_name}  ${FG_DIM}•  ${FG_MUTED}Category: ${FG_VIOLET}${BOLD}${sel_cat}${RST}${BG_CARD}" "${FG_VIOLET}"
            buf_box_line "  ${FG_MUTED}Size: ${FG_SKY}${sel_size}  ${FG_DIM}•  ${FG_MUTED}Min RAM/VRAM: ${FG_TEXT}${sel_req}  ${FG_DIM}•  ${FG_MUTED}Fit: ${sel_fit_lbl}  ${FG_DIM}•  ${FG_MUTED}Status: ${sel_status_lbl}${RST}${BG_CARD}" "${FG_VIOLET}"

            wrap_text_var "${sel_desc}" $((BOX_W - 8))
            local f_line1="${WRAP_LINES[0]:-}"
            local f_line2="${WRAP_LINES[1]:-}"
            if [[ ${#WRAP_LINES[@]} -gt 2 ]]; then
                truncate_plain_var "${f_line2} ${WRAP_LINES[2]}" $((BOX_W - 8))
                f_line2="${RET_STR}"
            fi
            buf_box_line "  ${FG_TEXT}${f_line1}${RST}${BG_CARD}" "${FG_VIOLET}"
            buf_box_line "  ${FG_TEXT}${f_line2}${RST}${BG_CARD}" "${FG_VIOLET}"
        fi

        buf_box_bottom "${FG_VIOLET}"

        local quick_hint=""
        if [[ ${visible_count} -gt 1 ]]; then
            quick_hint="[1-${visible_count}] Page Select   "
        elif [[ ${visible_count} -eq 1 ]]; then
            quick_hint="[1] Page Select   "
        fi
        buf_footer_hints "[↑/↓] Nav   [←/→] Page   [F] Filter: ${cur_filter}   [Enter] Install   ${quick_hint}[Esc/Q] Back"
        flush_frame

        local k
        k="$(read_key)"
        case "${k}" in
            UP|k|K)
                [[ ${total} -gt 0 ]] && cursor=$(( (cursor - 1 + total) % total ))
                ;;
            DOWN|j|J)
                [[ ${total} -gt 0 ]] && cursor=$(( (cursor + 1) % total ))
                ;;
            LEFT)
                if [[ ${total} -gt 0 ]]; then
                    cursor=$((cursor - page_size))
                    [[ ${cursor} -lt 0 ]] && cursor=0
                fi
                ;;
            RIGHT)
                if [[ ${total} -gt 0 ]]; then
                    cursor=$((cursor + page_size))
                    [[ ${cursor} -ge ${total} ]] && cursor=$((total - 1))
                fi
                ;;
            f|F)
                filter_idx=$(( (filter_idx + 1) % ${#filters[@]} ))
                cursor=0
                offset=0
                ;;
            [1-9])
                if [[ ${k} -le ${visible_count} ]]; then
                    local target_idx=$((offset + k - 1))
                    cursor=${target_idx}
                    pull_model_live "${names[$target_idx]}"
                    detect_ollama_state
                fi
                ;;
            ENTER)
                if [[ ${total} -gt 0 ]]; then
                    pull_model_live "${names[$cursor]}"
                    detect_ollama_state
                fi
                ;;
            ESC|q|Q|BACK)
                return
                ;;
        esac
    done
}

menu_custom_install() {
    local lang
    lang="$(get_lang)"

    local title prompt
    if [[ "${lang}" == "id" ]]; then
        title="CUSTOM REGISTRY PULL"
        prompt="Masukkan nama model & tag resmi dari https://ollama.com/library\nContoh: qwen2.5-coder:3b, llama3.2:3b, mistral:7b, nomic-embed-text"
    else
        title="CUSTOM REGISTRY PULL"
        prompt="Enter official model name & tag from https://ollama.com/library\nExamples: qwen2.5-coder:3b, llama3.2:3b, mistral:7b, nomic-embed-text"
    fi

    prompt_input "${title}" "${prompt}" "" 0 || return
    local model_tag
    model_tag="$(echo "${RET_INPUT}" | xargs)"
    if [[ -z "${model_tag}" ]]; then
        show_notice "DIBATALKAN" "Input kosong — pengunduhan dibatalkan." "${FG_AMBER}"
        return
    fi
    pull_model_live "${model_tag}"
}

# ==============================================================================
# 8. INSTALLED MODELS MANAGER (CHAT, INSPECT, COPY, DELETE)
# ==============================================================================
inspect_model_details() {
    local model_name="$1"
    local info_raw
    info_raw="$(ollama show "${model_name}" 2>/dev/null | head -n 16)"
    [[ -z "${info_raw}" ]] && info_raw="Tidak dapat membaca metadata model '${model_name}'."
    show_notice "MODEL ARCHITECTURE: ${model_name}" "${info_raw}" "${FG_SKY}"
}

menu_manage_installed() {
    local lang
    lang="$(get_lang)"
    local search_query=""
    local search_mode=0

    while true; do
        detect_ollama_state
        if [[ ${#INSTALLED_MODELS[@]} -eq 0 ]]; then
            if [[ "${lang}" == "id" ]]; then
                show_notice "NO LOCAL MODELS" "Belum ada model terinstall.\nGunakan 'Neural Model Store' untuk mengunduh model." "${FG_AMBER}"
            else
                show_notice "NO LOCAL MODELS" "No models installed yet.\nOpen 'Neural Model Store' to download weights." "${FG_AMBER}"
            fi
            return
        fi

        local all_total=${#INSTALLED_MODELS[@]}
        local cursor=0
        local offset=0

        while true; do
            # Filter daftar model berdasarkan search_query (case-insensitive)
            local filtered_models=()
            if [[ -z "${search_query}" ]]; then
                filtered_models=("${INSTALLED_MODELS[@]}")
            else
                local q_lower="${search_query,,}"
                for entry in "${INSTALLED_MODELS[@]}"; do
                    local mname="${entry%%|*}"
                    if [[ "${mname,,}" == *"${q_lower}"* ]]; then
                        filtered_models+=("${entry}")
                    fi
                done
            fi

            local total=${#filtered_models[@]}
            [[ ${cursor} -ge ${total} && ${total} -gt 0 ]] && cursor=$((total - 1))
            [[ ${total} -eq 0 ]] && cursor=0

            begin_neural_frame "LOCAL WEIGHTS VAULT • ${all_total} MODELS READY"

            # Hitung kapasitas baris adaptif agar kotak header atas tidak pernah terpotong
            local rows="${LINES:-0}"
            if [[ ${rows} -le 0 ]]; then
                rows="$(tput lines 2>/dev/null)"
                [[ -z "${rows}" ]] && rows=36
            fi
            local page_size=$((rows - 18))
            [[ ${page_size} -lt 4 ]] && page_size=4
            [[ ${page_size} -gt 10 ]] && page_size=10

            if [[ ${cursor} -lt ${offset} ]]; then
                offset=${cursor}
            elif [[ ${cursor} -ge $((offset + page_size)) ]]; then
                offset=$((cursor - page_size + 1))
            fi

            local end_idx=$((offset + page_size))
            [[ ${end_idx} -gt ${total} ]] && end_idx=${total}
            local visible_count=$((end_idx - offset))

            local cur_page=1
            local total_pages=1
            if [[ ${total} -gt 0 ]]; then
                cur_page=$(( (cursor / page_size) + 1 ))
                total_pages=$(( (total + page_size - 1) / page_size ))
            fi

            local name_col_w=34
            local size_col_w=11
            if [[ ${BOX_W} -lt 92 ]]; then
                name_col_w=24
                size_col_w=10
            fi

            buf_box_top "${FG_CYAN}"

            # Header kotak dengan indikator jumlah item & halaman
            local item_stat="0/0"
            [[ ${total} -gt 0 ]] && item_stat="$((cursor + 1))/${total}"
            local hdr_left="${FG_CYAN}${BOLD}◈ INSTALLED NEURAL MODELS${RST}${BG_CARD}"
            local hdr_right="${FG_MUTED}ITEM ${FG_CYAN}${item_stat}${FG_MUTED}  •  PAGE ${cur_page}/${total_pages}${RST}${BG_CARD}"

            strip_ansi_len "${hdr_left}"
            local hl_len=${RET_LEN}
            strip_ansi_len "${hdr_right}"
            local hr_len=${RET_LEN}
            local hdr_gap=$((BOX_W - 4 - hl_len - hr_len))
            [[ ${hdr_gap} -lt 1 ]] && hdr_gap=1
            repeat_char_var " " "${hdr_gap}"
            buf_box_line "${hdr_left}${RET_STR}${hdr_right}" "${FG_CYAN}"
            buf_box_sep "${FG_DIM}"

            # Baris pencarian interaktif
            local search_line=""
            if [[ ${search_mode} -eq 1 ]]; then
                search_line="${FG_CYAN}${BOLD}⌕ SEARCH:${RST}${BG_CARD} ${FG_TEXT}${search_query}${BG_PILL_CYAN}${FG_DARK}${BOLD} ${RST}${BG_CARD}   ${FG_MUTED}(Ketik nama • [Enter] Terapkan • [Esc] Reset)${RST}${BG_CARD}"
            elif [[ -n "${search_query}" ]]; then
                search_line="${FG_AMBER}${BOLD}⌕ FILTER:${RST}${BG_CARD} ${FG_TEXT}\"${search_query}\"${RST}${BG_CARD} ${FG_MUTED}(${total}/${all_total} cocok)   ${FG_SKY}[/] Ubah   [X/Esc] Reset${RST}${BG_CARD}"
            else
                search_line="${FG_MUTED}⌕ Tekan ${FG_SKY}[/]${FG_MUTED} atau ${FG_SKY}[S]${FG_MUTED} untuk mencari model terinstall...${RST}${BG_CARD}"
            fi
            buf_box_line "${search_line}" "${FG_CYAN}"
            buf_box_sep "${FG_DIM}"

            if [[ ${total} -eq 0 ]]; then
                buf_box_line "${FG_AMBER}  Tidak ada model yang cocok dengan \"${search_query}\". Tekan [Esc] atau [X] untuk reset.${RST}${BG_CARD}" "${FG_CYAN}"
            else
                for ((i = offset; i < end_idx; i++)); do
                    local entry="${filtered_models[$i]}"
                    local mname="${entry%%|*}"
                    local rest="${entry#*|}"
                    local msize="${rest%%|*}"
                    local mmod="${rest#*|}"
                    local page_slot=$((i - offset + 1))

                    # Kolom nama model (rata kiri, lebar tetap)
                    truncate_plain_var "${mname}" $((name_col_w - 1))
                    local disp_name="${RET_STR}"
                    repeat_char_var " " $((name_col_w - ${#disp_name}))
                    local name_pad="${RET_STR}"

                    # Kolom ukuran file (rata kiri, lebar tetap)
                    local size_tag="[${msize}]"
                    truncate_plain_var "${size_tag}" "${size_col_w}"
                    local disp_size="${RET_STR}"
                    repeat_char_var " " $((size_col_w - ${#disp_size}))
                    local size_pad="${RET_STR}"

                    local row_bg="${BG_CARD}"
                    local prefix="  "
                    local num_col="${FG_MUTED}"
                    local name_col="${FG_TEXT}"
                    if [[ ${i} -eq ${cursor} ]]; then
                        row_bg="${BG_SEL}"
                        prefix="${FG_CYAN}${BOLD}▸ "
                        num_col="${FG_CYAN}${BOLD}"
                        name_col="${FG_CYAN}${BOLD}"
                    fi

                    local left_part="${prefix}${num_col}[${page_slot}] ${name_col}${disp_name}${name_pad}${RST}${row_bg}  ${FG_SKY}${disp_size}${size_pad}${RST}${row_bg}"
                    local right_part="${FG_DIM}Updated: ${FG_MUTED}${mmod}${RST}${row_bg}"

                    strip_ansi_len "${left_part}"
                    local l_len=${RET_LEN}
                    strip_ansi_len "${right_part}"
                    local r_len=${RET_LEN}
                    local row_gap=$((BOX_W - 4 - l_len - r_len))
                    [[ ${row_gap} -lt 1 ]] && row_gap=1
                    repeat_char_var " " "${row_gap}"

                    buf_box_line "${left_part}${RET_STR}${right_part}" "${FG_CYAN}" "${row_bg}"
                done
            fi

            buf_box_bottom "${FG_CYAN}"

            if [[ ${search_mode} -eq 1 ]]; then
                buf_footer_hints "[A-Z/0-9] Filter Live   [↑/↓] Pilih   [Backspace] Hapus   [Enter] Selesai   [Esc] Reset"
            else
                local quick_hint=""
                [[ ${visible_count} -gt 1 ]] && quick_hint="[1-${visible_count}] Pilih   "
                [[ ${visible_count} -eq 1 ]] && quick_hint="[1] Pilih   "
                buf_footer_hints "[↑/↓] Nav   [←/→] Page   [/] Cari   [Enter] Actions   [C] Chat   ${quick_hint}[Esc/Q] Back"
            fi
            flush_frame

            local k
            k="$(read_key)"

            # Mode ketik pencarian langsung (live filter tanpa keluar TUI)
            if [[ ${search_mode} -eq 1 ]]; then
                case "${k}" in
                    ESC)
                        search_query=""
                        search_mode=0
                        cursor=0
                        offset=0
                        ;;
                    ENTER)
                        search_mode=0
                        ;;
                    BACK)
                        if [[ -n "${search_query}" ]]; then
                            search_query="${search_query%?}"
                            cursor=0
                            offset=0
                        fi
                        ;;
                    UP)
                        [[ ${total} -gt 0 ]] && cursor=$(( (cursor - 1 + total) % total ))
                        ;;
                    DOWN)
                        [[ ${total} -gt 0 ]] && cursor=$(( (cursor + 1) % total ))
                        ;;
                    *)
                        if [[ ${#k} -eq 1 && "${k}" =~ [a-zA-Z0-9._:/-] ]]; then
                            search_query+="${k}"
                            cursor=0
                            offset=0
                        fi
                        ;;
                esac
                continue
            fi

            # Mode navigasi normal
            case "${k}" in
                UP|k|K)
                    [[ ${total} -gt 0 ]] && cursor=$(( (cursor - 1 + total) % total ))
                    ;;
                DOWN|j|J)
                    [[ ${total} -gt 0 ]] && cursor=$(( (cursor + 1) % total ))
                    ;;
                LEFT)
                    if [[ ${total} -gt 0 ]]; then
                        cursor=$((cursor - page_size))
                        [[ ${cursor} -lt 0 ]] && cursor=0
                    fi
                    ;;
                RIGHT)
                    if [[ ${total} -gt 0 ]]; then
                        cursor=$((cursor + page_size))
                        [[ ${cursor} -ge ${total} ]] && cursor=$((total - 1))
                    fi
                    ;;
                /|s|S)
                    search_mode=1
                    ;;
                x|X)
                    if [[ -n "${search_query}" ]]; then
                        search_query=""
                        cursor=0
                        offset=0
                    fi
                    ;;
                c|C)
                    if [[ ${total} -gt 0 ]]; then
                        local sel_m="${filtered_models[$cursor]%%|*}"
                        open_local_chat "${sel_m}"
                        break
                    fi
                    ;;
                [1-9])
                    if [[ ${k} -le ${visible_count} ]]; then
                        local target_idx=$((offset + k - 1))
                        cursor=${target_idx}
                        local sel_m="${filtered_models[$target_idx]%%|*}"
                        submenu_model_actions "${sel_m}"
                        break
                    fi
                    ;;
                ENTER)
                    if [[ ${total} -gt 0 ]]; then
                        local sel_m="${filtered_models[$cursor]%%|*}"
                        submenu_model_actions "${sel_m}"
                        break
                    fi
                    ;;
                ESC)
                    if [[ -n "${search_query}" ]]; then
                        search_query=""
                        cursor=0
                        offset=0
                    else
                        return
                    fi
                    ;;
                q|Q|BACK)
                    return
                    ;;
            esac
        done
    done
}

submenu_model_actions() {
    local selected_model="$1"
    local cursor=0
    local actions=("chat" "inspect" "copy" "delete")

    local labels=(
        "Launch Neural Streaming Chat (Interactive Terminal)"
        "Inspect Architecture & Parameters (ollama show)"
        "Copy Model Tag to Clipboard"
        "Purge / Delete Model from Disk"
    )

    while true; do
        begin_neural_frame "MODEL CONTROL // ${selected_model}"
        buf_box_top "${FG_VIOLET}"
        buf_box_line "${FG_VIOLET}${BOLD}◈ TARGET WEIGHTS: ${FG_CYAN}${selected_model}${RST}${BG_CARD}" "${FG_VIOLET}"
        buf_box_sep "${FG_DIM}"

        for ((i = 0; i < 4; i++)); do
            local row_bg="${BG_CARD}"
            local prefix="  "
            local col="${FG_TEXT}"
            if [[ ${i} -eq ${cursor} ]]; then
                row_bg="${BG_SEL}"
                prefix="${FG_CYAN}${BOLD}▸ "
                col="${FG_CYAN}${BOLD}"
            fi
            [[ ${i} -eq 3 && ${i} -eq ${cursor} ]] && col="${FG_RED}${BOLD}"
            buf_box_line "${prefix}[$((i + 1))] ${col}${labels[$i]}${RST}${row_bg}" "${FG_VIOLET}" "${row_bg}"
        done

        buf_box_bottom "${FG_VIOLET}"
        buf_footer_hints "[↑/↓] Navigate   [Enter] Execute   [1-4] Hotkey   [Esc/Q] Back"
        flush_frame

        local k
        k="$(read_key)"
        case "${k}" in
            UP|k|K)   cursor=$(( (cursor - 1 + 4) % 4 )) ;;
            DOWN|j|J) cursor=$(( (cursor + 1) % 4 )) ;;
            [1-4])    cursor=$((k - 1)); k="ENTER" ;;
            ESC|q|Q|BACK) return ;;
        esac

        if [[ "${k}" == "ENTER" ]]; then
            case "${actions[$cursor]}" in
                chat)
                    open_local_chat "${selected_model}"
                    return
                    ;;
                inspect)
                    inspect_model_details "${selected_model}"
                    ;;
                copy)
                    if copy_to_clipboard "${selected_model}"; then
                        show_notice "CLIPBOARD COPIED" "Tag '${selected_model}' berhasil disalin ke clipboard!" "${FG_GREEN}"
                    else
                        show_notice "MODEL TAG" "Tag: ${selected_model}\n(Install xclip atau wl-copy untuk auto-clipboard)" "${FG_SKY}"
                    fi
                    ;;
                delete)
                    delete_model_prompt "${selected_model}"
                    return
                    ;;
            esac
        fi
    done
}

# ==============================================================================
# 9. INTEGRATIONS & API GATEWAY (9ROUTER, OPEN WEBUI, CONTINUE.DEV)
# ==============================================================================
build_continue_yaml() {
    local sample_model="qwen2.5-coder:3b"
    if [[ ${#INSTALLED_MODELS[@]} -gt 0 ]]; then
        sample_model="${INSTALLED_MODELS[0]%%|*}"
    fi

    cat << EOF
name: ARI-DEV Local Ollama
version: 1.0.0
schema: v1
models:
  - name: Local Chat (${sample_model})
    provider: ollama
    model: ${sample_model}
    apiBase: http://127.0.0.1:11434
    roles:
      - chat
      - edit
  - name: Local Autocomplete (${sample_model})
    provider: ollama
    model: ${sample_model}
    apiBase: http://127.0.0.1:11434
    roles:
      - autocomplete
EOF
}

menu_integrations_api() {
    detect_ollama_state
    local cursor=0
    local items=(
        "Endpoint Guide: 9Router, Open WebUI (Docker) & Aider CLI"
        "Live API Handshake Test (http://127.0.0.1:11434/api/tags)"
        "Preview Continue.dev Config (~/.continue/config.yaml)"
        "Copy Continue.dev YAML to Clipboard"
    )

    while true; do
        begin_neural_frame "AI AGENT GATEWAY • 9ROUTER • OPEN WEBUI • CONTINUE.DEV"
        buf_box_top "${FG_SKY}"
        buf_box_line "${FG_SKY}${BOLD}◈ LOCAL ENDPOINT & AGENT INTEGRATION HUB${RST}${BG_CARD}" "${FG_SKY}"
        buf_box_sep "${FG_DIM}"

        for ((i = 0; i < 4; i++)); do
            local row_bg="${BG_CARD}"
            local prefix="  "
            local col="${FG_TEXT}"
            if [[ ${i} -eq ${cursor} ]]; then
                row_bg="${BG_SEL}"
                prefix="${FG_CYAN}${BOLD}▸ "
                col="${FG_CYAN}${BOLD}"
            fi
            buf_box_line "${prefix}[$((i + 1))] ${col}${items[$i]}${RST}${row_bg}" "${FG_SKY}" "${row_bg}"
        done

        buf_box_bottom "${FG_SKY}"
        buf_footer_hints "[↑/↓] Navigate   [Enter] Select   [1-4] Hotkey   [Esc/Q] Back"
        flush_frame

        local k
        k="$(read_key)"
        case "${k}" in
            UP|k|K)   cursor=$(( (cursor - 1 + 4) % 4 )) ;;
            DOWN|j|J) cursor=$(( (cursor + 1) % 4 )) ;;
            [1-4])    cursor=$((k - 1)); k="ENTER" ;;
            ESC|q|Q|BACK) return ;;
        esac

        if [[ "${k}" == "ENTER" ]]; then
            case ${cursor} in
                0)
                    local guide_txt
                    guide_txt=$(cat << 'EOF'
1. UNIVERSAL OLLAMA ENDPOINTS
   • Native Ollama API : http://127.0.0.1:11434
   • OpenAI Compatible : http://127.0.0.1:11434/v1
   • API Key           : ollama (dummy key)

2. 9ROUTER PROXY INTEGRATION
   • Provider Type     : OpenAI Compatible
   • Base URL          : http://127.0.0.1:11434/v1
   • Model ID          : Sesuai tag terinstall (misal: qwen2.5-coder:3b)

3. OPEN WEBUI (DOCKER CONTAINER)
   • Systemd Env       : Environment="OLLAMA_HOST=0.0.0.0:11434"
   • Docker Run Flag   : --add-host=host.docker.internal:host-gateway
   • Container Env     : OLLAMA_BASE_URL=http://host.docker.internal:11434
   • UFW Firewall      : sudo ufw allow from 172.16.0.0/12 to any port 11434
EOF
)
                    show_notice "AI ECOSYSTEM INTEGRATION GUIDE" "${guide_txt}" "${FG_SKY}"
                    ;;
                1)
                    if curl -sf --max-time 3 "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
                        show_notice "HANDSHAKE SUCCESS" "✓ HTTP 200 OK — Neural API aktif di http://127.0.0.1:11434" "${FG_GREEN}"
                    else
                        show_notice "HANDSHAKE FAILED" "✕ Gagal terhubung ke http://127.0.0.1:11434.\nPastikan Ollama service sedang berjalan." "${FG_RED}"
                    fi
                    ;;
                2)
                    show_notice "SAMPLE ~/.continue/config.yaml" "$(build_continue_yaml)" "${FG_VIOLET}"
                    ;;
                3)
                    if copy_to_clipboard "$(build_continue_yaml)"; then
                        show_notice "CLIPBOARD COPIED" "✓ Konfigurasi Continue.dev YAML berhasil disalin ke clipboard!" "${FG_GREEN}"
                    else
                        show_notice "CLIPBOARD UNAVAILABLE" "Install 'xclip' atau 'wl-copy' untuk menyalin otomatis." "${FG_AMBER}"
                    fi
                    ;;
            esac
        fi
    done
}

# ==============================================================================
# 10. LANGUAGE PREFERENCES (ID / EN)
# ==============================================================================
menu_preferences() {
    local lang
    lang="$(get_lang)"
    local cursor=0
    [[ "${lang}" == "en" ]] && cursor=1

    while true; do
        begin_neural_frame "SYSTEM PREFERENCES // INTERFACE LOCALE"
        buf_box_top "${FG_VIOLET}"
        buf_box_line "${FG_VIOLET}${BOLD}◈ SELECT INTERFACE LANGUAGE${RST}${BG_CARD}" "${FG_VIOLET}"
        buf_box_line "${FG_MUTED}  Config: ${CONFIG_PATH}${RST}${BG_CARD}" "${FG_VIOLET}"
        buf_box_sep "${FG_DIM}"

        local opts=("Bahasa Indonesia (ID)" "English (EN)")
        local codes=("id" "en")

        for ((i = 0; i < 2; i++)); do
            local radio="○"
            [[ "${lang}" == "${codes[$i]}" ]] && radio="${FG_GREEN}●"
            local row_bg="${BG_CARD}"
            local prefix="  "
            local col="${FG_TEXT}"
            if [[ ${i} -eq ${cursor} ]]; then
                row_bg="${BG_SEL}"
                prefix="${FG_CYAN}${BOLD}▸ "
                col="${FG_CYAN}${BOLD}"
            fi
            buf_box_line "${prefix}${radio}${RST}${row_bg}  ${col}${opts[$i]}${RST}${row_bg}" "${FG_VIOLET}" "${row_bg}"
        done

        buf_box_bottom "${FG_VIOLET}"
        buf_footer_hints "[↑/↓] Toggle   [Enter] Save Locale   [Esc/Q] Back"
        flush_frame

        local k
        k="$(read_key)"
        case "${k}" in
            UP|DOWN|j|k|J|K) cursor=$((1 - cursor)) ;;
            ENTER)
                set_lang "${codes[$cursor]}"
                if [[ "${codes[$cursor]}" == "id" ]]; then
                    show_notice "LOCALE UPDATED" "✓ Bahasa antarmuka diubah ke Bahasa Indonesia (ID)." "${FG_GREEN}"
                else
                    show_notice "LOCALE UPDATED" "✓ Interface language switched to English (EN)." "${FG_GREEN}"
                fi
                return
                ;;
            ESC|q|Q|BACK) return ;;
        esac
    done
}

# ==============================================================================
# 11. MAIN NEURAL COMMAND CENTER LOOP (ZERO-FLICKER NAVIGATION)
# ==============================================================================
main_loop() {
    init_files
    enter_tui
    local cursor=0
    local need_sync=1

    local lang="id"
    local top_rec_name=""
    local top_rec_size=""

    while true; do
        # Only poll hardware & Ollama API when needed (startup, post-action, or [R])
        if [[ ${need_sync} -eq 1 ]]; then
            lang="$(get_lang)"
            detect_hardware
            detect_ollama_state
            top_rec_name=""
            top_rec_size=""
            if [[ ${OLLAMA_INSTALLED} -eq 1 && ${#INSTALLED_MODELS[@]} -eq 0 ]]; then
                local top_line
                top_line="$(get_scored_models_lines "${lang}" | head -n 1)"
                top_rec_name="$(echo "${top_line}" | cut -d'|' -f3)"
                top_rec_size="$(echo "${top_line}" | cut -d'|' -f4)"
            fi
            need_sync=0
        fi

        begin_neural_frame "${APP_SUB}"

        local keys=()
        local labels=()
        local badges=()

        if [[ ${OLLAMA_INSTALLED} -eq 0 ]]; then
            keys+=("install_ollama")
            if [[ "${lang}" == "id" ]]; then
                labels+=("INSTALL OLLAMA RUNTIME SEKARANG (Wajib)")
            else
                labels+=("INSTALL OLLAMA RUNTIME NOW (Required)")
            fi
            badges+=("${FG_RED}[SETUP]${RST}")
        elif [[ ${#INSTALLED_MODELS[@]} -eq 0 && -n "${top_rec_name}" ]]; then
            keys+=("quick_rec")
            if [[ "${lang}" == "id" ]]; then
                labels+=("Quick-Install Rekomendasi Terbaik: ${top_rec_name}")
            else
                labels+=("Quick-Install Top Match: ${top_rec_name}")
            fi
            badges+=("${FG_GREEN}[★ ${top_rec_size}]${RST}")
        fi

        if [[ "${lang}" == "id" ]]; then
            keys+=("models" "store" "custom" "service" "api" "prefs" "refresh" "quit")
            labels+=(
                "Neural Models Vault — Chat, Inspect, Copy & Delete"
                "Neural Model Store — Rekomendasi Cerdas Hardware"
                "Custom Registry Pull — Unduh Tag dari Ollama Library"
                "Engine Power Control — Start / Stop Ollama Daemon"
                "Agent & API Gateway — 9Router, Open WebUI & Continue.dev"
                "System Preferences — Bahasa Antarmuka (ID / EN)"
                "Sync Telemetry — Refresh Status Hardware & Service"
                "Exit Command Center"
            )
        else
            keys+=("models" "store" "custom" "service" "api" "prefs" "refresh" "quit")
            labels+=(
                "Neural Models Vault — Chat, Inspect, Copy & Delete"
                "Neural Model Store — Hardware-Matched Recommendations"
                "Custom Registry Pull — Download Tag from Ollama Library"
                "Engine Power Control — Start / Stop Ollama Daemon"
                "Agent & API Gateway — 9Router, Open WebUI & Continue.dev"
                "System Preferences — Interface Language (ID / EN)"
                "Sync Telemetry — Refresh Hardware & Service Status"
                "Exit Command Center"
            )
        fi

        local svc_tag="${FG_AMBER}[STANDBY]${RST}"
        [[ ${OLLAMA_RUNNING} -eq 1 ]] && svc_tag="${FG_GREEN}[ACTIVE]${RST}"

        badges+=(
            "${FG_CYAN}[${#INSTALLED_MODELS[@]} READY]${RST}"
            "${FG_VIOLET}[AI STORE]${RST}"
            "${FG_SKY}[LIBRARY]${RST}"
            "${svc_tag}"
            "${FG_SKY}[GATEWAY]${RST}"
            "${FG_MUTED}[${lang^^}]${RST}"
            "${FG_MUTED}[SYNC]${RST}"
            "${FG_RED}[ESC]${RST}"
        )

        local total=${#keys[@]}
        [[ ${cursor} -ge ${total} ]] && cursor=$((total - 1))

        buf_box_top "${FG_VIOLET}"
        buf_box_line "${FG_VIOLET}${BOLD}◈ NEURAL COMMAND MATRIX${RST}${BG_CARD}" "${FG_VIOLET}"
        buf_box_sep "${FG_DIM}"

        for ((i = 0; i < total; i++)); do
            local row_bg="${BG_CARD}"
            local prefix="  "
            local num_col="${FG_MUTED}"
            local txt_col="${FG_TEXT}"

            if [[ ${i} -eq ${cursor} ]]; then
                row_bg="${BG_SEL}"
                prefix="${FG_CYAN}${BOLD}▸ "
                num_col="${FG_CYAN}${BOLD}"
                txt_col="${FG_CYAN}${BOLD}"
            fi

            local left_part="${prefix}${num_col}[$((i + 1))] ${txt_col}${labels[$i]}${RST}${row_bg}"
            local right_part="${badges[$i]}${row_bg}"
            strip_ansi_len "${left_part}"
            local l_len=${RET_LEN}
            strip_ansi_len "${right_part}"
            local r_len=${RET_LEN}
            local gap=$((BOX_W - 4 - l_len - r_len))
            [[ ${gap} -lt 1 ]] && gap=1
            repeat_char_var " " "${gap}"

            buf_box_line "${left_part}${RET_STR}${right_part}" "${FG_VIOLET}" "${row_bg}"
        done

        buf_box_bottom "${FG_VIOLET}"
        buf_footer_hints "[↑/↓] Navigate   [Enter] Execute   [1-${total}] Quick Jump   [R] Sync Telemetry   [Q] Quit"
        flush_frame

        local k
        k="$(read_key)"
        case "${k}" in
            UP|k|K)   cursor=$(( (cursor - 1 + total) % total )) ;;
            DOWN|j|J) cursor=$(( (cursor + 1) % total )) ;;
            r|R)      need_sync=1 ;;
            [1-9])
                local idx=$((k - 1))
                if [[ ${idx} -lt ${total} ]]; then
                    cursor=${idx}
                    k="ENTER"
                fi
                ;;
            ESC|q|Q)  break ;;
        esac

        if [[ "${k}" == "ENTER" ]]; then
            case "${keys[$cursor]}" in
                install_ollama) workflow_install_ollama; need_sync=1 ;;
                quick_rec)      pull_model_live "${top_rec_name}"; need_sync=1 ;;
                models)         menu_manage_installed; need_sync=1 ;;
                store)          menu_model_store; need_sync=1 ;;
                custom)         menu_custom_install; need_sync=1 ;;
                service)        toggle_ollama_service 0; need_sync=1 ;;
                api)            menu_integrations_api; need_sync=1 ;;
                prefs)          menu_preferences; need_sync=1 ;;
                refresh)        need_sync=1 ;;
                quit)           break ;;
            esac
        fi
    done
}

main_loop
