#!/usr/bin/env bash
#
# FoxSay Buddy 开发环境一键搭建脚本
#
# 功能:
#   1. 安装系统依赖 (SDL2, CMake)
#   2. 克隆 ESP-IDF v5.5.1 并安装 ESP32-S3 工具链
#   3. 克隆 LVGL v9.3 PC 模拟器
#   4. 将 FoxSay UI 源码链接到模拟器
#   5. 编译并验证模拟器
#
# 用法:
#   bash tools/setup.sh          # 完整安装
#   bash tools/setup.sh sim      # 只安装模拟器
#   bash tools/setup.sh idf      # 只安装 ESP-IDF
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TOOLS_DIR="$SCRIPT_DIR"
UI_SRC="$TOOLS_DIR/ui"

# ====== 版本常量 ======
ESP_IDF_VERSION="v5.5.1"
LVGL_SIM_BRANCH="release/v9.3"
ESP_IDF_DIR="$TOOLS_DIR/esp-idf"
LVGL_SIM_DIR="$TOOLS_DIR/lvgl_simulator"

# ====== 颜色输出 ======
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

# ====== Step 1: 系统依赖 ======
install_deps() {
    info "检查系统依赖..."

    if ! command -v brew &>/dev/null; then
        error "请先安装 Homebrew: https://brew.sh"
    fi

    local missing=()
    command -v sdl2 &>/dev/null || ! brew list sdl2 &>/dev/null 2>&1 && missing+=(sdl2)
    command -v cmake &>/dev/null || ! brew list cmake &>/dev/null 2>&1 && missing+=(cmake)

    if [ ${#missing[@]} -gt 0 ]; then
        info "安装: ${missing[*]}"
        brew install "${missing[@]}"
    fi

    command -v node &>/dev/null && npm list -g lv_font_conv &>/dev/null 2>&1 || {
        info "安装 lv_font_conv (字体转换工具)..."
        npm install -g lv_font_conv
    }

    info "系统依赖就绪"
}

# ====== Step 2: ESP-IDF ======
install_espidf() {
    if [ -d "$ESP_IDF_DIR" ] && [ -f "$ESP_IDF_DIR/export.sh" ]; then
        info "ESP-IDF 已存在，跳过克隆"
    else
        info "克隆 ESP-IDF $ESP_IDF_VERSION..."
        git clone -b "$ESP_IDF_VERSION" --recursive \
            https://github.com/espressif/esp-idf.git "$ESP_IDF_DIR"
    fi

    info "安装 ESP32-S3 工具链..."
    cd "$ESP_IDF_DIR"

    # 安装 Python 虚拟环境
    python3 tools/idf_tools.py install-python-env

    # 安装必要的工具 (跳过 RISC-V, 只装 ESP32-S3 需要的)
    python3 tools/idf_tools.py install xtensa-esp-elf xtensa-esp-elf-gdb
    python3 tools/idf_tools.py install esp32ulp-elf esp-rom-elfs
    python3 tools/idf_tools.py install riscv32-esp-elf openocd-esp32 2>/dev/null || \
        warn "部分可选工具安装失败，不影响 ESP32-S3 编译"

    info "ESP-IDF 就绪，使用以下命令激活:"
    echo "  source $ESP_IDF_DIR/export.sh"
}

# ====== Step 3: LVGL 模拟器 ======
install_simulator() {
    if [ -d "$LVGL_SIM_DIR" ] && [ -f "$LVGL_SIM_DIR/CMakeLists.txt" ]; then
        info "LVGL 模拟器已存在，跳过克隆"
    else
        info "克隆 LVGL PC 模拟器 ($LVGL_SIM_BRANCH)..."
        git clone -b "$LVGL_SIM_BRANCH" --recursive \
            https://github.com/lvgl/lv_port_pc_vscode.git "$LVGL_SIM_DIR"
    fi

    info "链接 FoxSay UI 源码到模拟器..."
    link_ui_to_simulator

    info "配置 lv_conf.h..."
    configure_lv_conf

    info "编译模拟器..."
    cd "$LVGL_SIM_DIR"
    mkdir -p build && cd build
    cmake .. 2>&1 | tail -5
    make -j"$(sysctl -n hw.ncpu 2>/dev/null || echo 8)"

    info "模拟器就绪，运行命令:"
    echo "  cd $LVGL_SIM_DIR && ./bin/main"
}

# ====== 链接 UI 源码 ======
link_ui_to_simulator() {
    local sim_ui="$LVGL_SIM_DIR/main/src/ui"

    # 如果 sim_ui 已存在且不是符号链接，备份并替换
    if [ -d "$sim_ui" ] && [ ! -L "$sim_ui" ]; then
        rm -rf "${sim_ui}.bak" 2>/dev/null
        mv "$sim_ui" "${sim_ui}.bak"
    fi

    # 创建符号链接
    rm -f "$sim_ui" 2>/dev/null
    ln -sf "$UI_SRC" "$sim_ui"

    info "UI 源码已链接: $sim_ui -> $UI_SRC"

    # 更新 CMakeLists.txt (如果还没有 UI 文件引用)
    local cmake="$LVGL_SIM_DIR/CMakeLists.txt"
    if ! grep -q "ui_clock_screen" "$cmake" 2>/dev/null; then
        # 添加 include 路径
        sed -i.bak 's|include_directories(${PROJECT_SOURCE_DIR}/main/inc)|include_directories(${PROJECT_SOURCE_DIR}/main/inc)\ninclude_directories(${PROJECT_SOURCE_DIR}/main/src)|' "$cmake"

        # 添加 UI 源文件到 executable
        sed -i.bak '/mouse_cursor_icon\.c/a\
        ${PROJECT_SOURCE_DIR}/main/src/ui/ui_clock_screen.c\
        ${PROJECT_SOURCE_DIR}/main/src/ui/ui_flashcard_screen.c\
        ${PROJECT_SOURCE_DIR}/main/src/ui/ui_wiki_screen.c\
        ${PROJECT_SOURCE_DIR}/main/src/ui/ui_screen_manager.c\
        ${PROJECT_SOURCE_DIR}/main/src/ui/fonts/fox_cn_14.c\
        ${PROJECT_SOURCE_DIR}/main/src/ui/fonts/fox_cn_24.c' "$cmake"

        info "CMakeLists.txt 已更新"
    fi

    # 更新 main.c (使用 FoxSay UI 替代 demo)
    local main_c="$LVGL_SIM_DIR/main/src/main.c"
    if ! grep -q "ui_screens.h" "$main_c" 2>/dev/null; then
        # 添加 include
        sed -i.bak 's|#include "glob.h"|#include "glob.h"\n#include "ui/ui_screens.h"|' "$main_c"
        # 替换 demo 调用
        sed -i.bak 's|lv_demo_widgets();|ui_show_clock_screen();|' "$main_c"
        # 修改分辨率为 320x240
        sed -i.bak 's|hal_init(320, 480)|hal_init(320, 240)|' "$main_c"
        info "main.c 已更新 (320x240, FoxSay UI)"
    fi
}

# ====== 配置 lv_conf.h ======
configure_lv_conf() {
    local conf="$LVGL_SIM_DIR/lv_conf.h"

    # 启用 snapshot
    sed -i.bak 's/#define LV_USE_SNAPSHOT 0/#define LV_USE_SNAPSHOT 1/' "$conf"
    # 启用压缩字体
    sed -i.bak 's/#define LV_USE_FONT_COMPRESSED 0/#define LV_USE_FONT_COMPRESSED 1/' "$conf"

    info "lv_conf.h 已配置"
}

# ====== 主流程 ======
main() {
    local target="${1:-all}"

    echo "========================================"
    echo "  FoxSay Buddy 开发环境搭建"
    echo "  项目根目录: $PROJECT_ROOT"
    echo "========================================"
    echo ""

    case "$target" in
        all)
            install_deps
            install_espidf
            install_simulator
            ;;
        idf)
            install_espidf
            ;;
        sim)
            install_deps
            install_simulator
            ;;
        *)
            echo "用法: bash $0 [all|sim|idf]"
            exit 1
            ;;
    esac

    echo ""
    echo "========================================"
    info "环境搭建完成!"
    echo ""
    echo "  激活 ESP-IDF:"
    echo "    source $ESP_IDF_DIR/export.sh"
    echo ""
    echo "  运行模拟器:"
    echo "    cd $LVGL_SIM_DIR && ./bin/main"
    echo ""
    echo "  截图验证:"
    echo "    python3 $TOOLS_DIR/screenshot.py"
    echo "========================================"
}

main "$@"
