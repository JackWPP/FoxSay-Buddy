# FoxSay Buddy 工具链搭建指南

> 面向团队开发者的本地开发环境搭建文档。从零开始配置 ESP32 固件编译与 LVGL PC 模拟器两套工具链。

---

## 目录

1. [概述](#1-概述)
2. [环境要求](#2-环境要求)
3. [ESP-IDF 工具链搭建](#3-esp-idf-工具链搭建)
4. [LVGL PC 模拟器搭建](#4-lvgl-pc-模拟器搭建)
5. [中文字体方案](#5-中文字体方案)
6. [UI 开发工作流](#6-ui-开发工作流)
7. [屏幕导航架构](#7-屏幕导航架构)
8. [常见问题](#8-常见问题)

---

## 1. 概述

FoxSay Buddy 项目的固件开发依赖两套独立的工具链：

| 工具链 | 用途 | 运行环境 |
|--------|------|----------|
| **ESP-IDF 固件编译** | 交叉编译 ESP32-S3 固件，烧录至立创·实战派开发板 (N16R8) | 命令行 + ESP-IDF 工具链 |
| **LVGL PC 模拟器** | 在 PC 上实时预览 UI 界面，快速迭代视觉效果 | SDL2 + CMake + LVGL v9.3 |

**开发策略**：所有 UI 页面先在 PC 模拟器上调试通过，再移植到 ESP-IDF 固件工程中。模拟器分辨率固定为 **320×240**，与目标硬件 GT911 触摸屏完全一致，确保布局代码无需修改即可迁移。

---

## 2. 环境要求

### 操作系统

- **macOS**（Apple Silicon M 系列 / Intel 均支持）
- Linux（Ubuntu 20.04+ 推荐）
- Windows 请参考 LVGL 官方 Windows 文档（本文以 macOS/Linux 为主）

### 基础依赖

| 依赖 | 最低版本 | 安装方式 |
|------|----------|----------|
| Homebrew (macOS) | 最新版 | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Python 3 | 3.8+ | `brew install python3`（macOS 自带或 Homebrew 安装） |
| Node.js | 16+ | `brew install node`（用于字体生成工具） |
| Git | 2.30+ | `brew install git` 或使用系统自带 |
| Pillow (Python) | 最新版 | `pip3 install Pillow`（截图转 PNG 工具依赖） |

验证基础环境：

```bash
python3 --version
node --version
git --version
```

---

## 3. ESP-IDF 工具链搭建

本项目使用 **ESP-IDF v5.5.1**，仓库已包含在 `tools/esp-idf/` 目录下。

### 3.1 克隆 ESP-IDF（如仓库中尚未包含）

> **注意**：本仓库 `tools/esp-idf/` 已包含 ESP-IDF v5.5.1 源码。如你是在本仓库中工作，可跳过此步骤。
>
> 如果需要独立安装 ESP-IDF：

```bash
# 选择一个工作目录
mkdir -p ~/esp
cd ~/esp

# 克隆 ESP-IDF v5.5.1（含所有子模块）
git clone -b v5.5.1 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
```

### 3.2 安装 ESP32-S3 交叉编译器

```bash
# 进入 ESP-IDF 目录
cd tools/esp-idf       # 本仓库内路径
# 或 cd ~/esp/esp-idf  # 独立安装路径

# 仅安装 ESP32-S3 所需的工具链（节省磁盘和时间）
./install.sh esp32s3
```

安装过程会自动下载：
- Xtensa ESP32-S3 交叉编译器 (GCC)
- esptool.py（烧录工具）
- 必要的 Python 依赖包

> **提示**：如果你同时需要编译其他芯片（如 ESP32、ESP32-C3），可以用逗号分隔：
> ```bash
> ./install.sh esp32,esp32s3,esp32c3
> ```

### 3.3 激活环境变量

每次打开新终端后，都需要先激活 ESP-IDF 环境：

```bash
# 在本仓库根目录下
source tools/esp-idf/export.sh
```

激活后，终端提示符前会出现 `(idf)` 前缀，表示环境已就绪。

> **便捷做法**：将以下内容添加到 `~/.zshrc`（或 `~/.bashrc`），创建快捷命令：
> ```bash
> alias get_idf='source /Users/<你的用户名>/FoxSay-Buddy/tools/esp-idf/export.sh'
> ```
> 之后只需输入 `get_idf` 即可激活环境。

### 3.4 验证安装

```bash
idf.py --version
```

预期输出：

```
ESP-IDF v5.5.1
```

### 3.5 编译固件（后续使用）

```bash
# 进入固件工程目录（按项目实际路径）
cd firmware

# 设置目标芯片为 ESP32-S3
idf.py set-target esp32s3

# 编译
idf.py build

# 烧录到开发板（USB 连接后）
idf.py -p /dev/cu.usbserial-* flash

# 打开串口监控
idf.py -p /dev/cu.usbserial-* monitor
```

---

## 4. LVGL PC 模拟器搭建

### 4.1 安装系统依赖

**macOS：**

```bash
brew install sdl2 cmake
```

**Ubuntu/Debian：**

```bash
sudo apt-get install build-essential libsdl2-dev cmake
```

验证安装：

```bash
cmake --version
sdl2-config --version
```

### 4.2 项目模拟器位置

本项目的 LVGL PC 模拟器已集成在仓库中：

```
tools/lvgl_simulator/
├── CMakeLists.txt          # CMake 构建配置
├── lv_conf.h               # LVGL 全局配置（v9.3.0）
├── lvgl/                   # LVGL v9.3 库源码 (Git submodule)
├── main/src/
│   ├── main.c              # 模拟器入口
│   ├── mouse_cursor_icon.c # 鼠标光标图标
│   └── ui/
│       ├── ui_screens.h           # 屏幕头文件（公共接口）
│       ├── ui_theme.h             # 全局主题与色彩定义
│       ├── ui_screen_manager.c    # 屏幕导航管理器
│       ├── ui_clock_screen.c      # 时钟主屏
│       ├── ui_flashcard_screen.c  # 闪卡页面
│       ├── ui_wiki_screen.c       # 知识库页面
│       └── fonts/
│           ├── fox_cn_14.c        # 中文字体 14px
│           └── fox_cn_24.c        # 中文字体 24px
├── screenshot.py           # 截图 .bin → .png 转换工具
└── bin/                    # 编译输出目录
```

### 4.3 关键 LVGL 配置

配置文件位于 `tools/lvgl_simulator/lv_conf.h`，以下为本项目的关键配置项：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `LV_COLOR_DEPTH` | `32` | 32 位色深 (XRGB8888)，与模拟器截图格式一致 |
| `LV_USE_SNAPSHOT` | `1` | 启用截图功能，用于自动化截图验证 |
| `LV_USE_FONT_COMPRESSED` | `1` | 启用压缩字体支持，减少中文字体的 Flash 占用 |

### 4.4 编译模拟器

```bash
cd tools/lvgl_simulator

# 创建构建目录
mkdir -p build && cd build

# 配置 CMake
cmake ..

# 编译（使用所有可用核心）
cmake --build . -j$(sysctl -n hw.ncpu)
```

编译成功后，可执行文件位于 `tools/lvgl_simulator/bin/main`。

### 4.5 运行模拟器

```bash
# 方式一：直接运行
./bin/main

# 方式二：通过 CMake 自定义 target
cd build && cmake --build . --target run
```

运行后会弹出一个 **320×240** 像素的 SDL2 窗口，显示 FoxSay UI 界面。

> **交互说明**：
> - **鼠标点击** = 触摸点击
> - **鼠标按住拖动** = 触摸滑动（模拟 GT911 触摸手势）
> - **鼠标滚轮** = 编码器旋转
> - **键盘** = 键盘输入

### 4.6 截图验证

模拟器启动时会自动对三个核心屏幕截图，生成 `.bin` 原始文件。使用 `screenshot.py` 转换为 PNG：

```bash
cd tools/lvgl_simulator

# 转换单张截图
python3 screenshot.py screenshot_clock.bin screenshot_clock.png

# 批量转换所有截图
python3 screenshot.py screenshot_clock.bin screenshot_clock.png
python3 screenshot.py screenshot_flash.bin screenshot_flash.png
python3 screenshot.py screenshot_wiki.bin screenshot_wiki.png
```

> **依赖**：脚本自动依赖 `Pillow` 库，首次运行时会自动安装（`pip3 install Pillow`）。

---

## 5. 中文字体方案

### 5.1 为什么需要自定义字体

LVGL 内置字体为 **Montserrat**（拉丁字母），不包含 CJK（中日韩统一表意文字）字符。如果直接在标签中使用中文文本，将显示为空白或"豆腐块"。

本项目采用**按需生成位图字体**的方案：仅将项目中实际使用的汉字编入字体文件，大幅减小固件体积（相比完整 GB2312 字库 1MB+ 缩减至几十 KB）。

### 5.2 字体规格

| 字体标识 | 像素大小 | 用途 | 源文件 |
|----------|----------|------|--------|
| `fox_cn_14` | 14px, 4bpp | 正文、提示、标签 | `main/src/ui/fonts/fox_cn_14.c` |
| `fox_cn_24` | 24px, 4bpp | 标题、焦点节点 | `main/src/ui/fonts/fox_cn_24.c` |

### 5.3 安装字体生成工具

LVGL 官方提供 `lv_font_conv` 命令行工具，将 TrueType 字体转换为 LVGL C 数组格式：

```bash
npm install -g lv_font_conv
```

验证安装：

```bash
lv_font_conv --version
```

### 5.4 生成字体命令

以下命令从系统字体中提取项目所需的汉字，生成 LVGL 位图字体 C 文件。

**生成 fox_cn_14（14px 正文字体）：**

```bash
cd tools/lvgl_simulator/main/src/ui/fonts

lv_font_conv \
  --font /Library/Fonts/Arial\ Unicode.ttf \
  --size 14 \
  --bpp 4 \
  --range 0x20-0x7E \
  --range 0x2605-0x2605 \
  --symbols "微积分天极限连续性序列级数矩阵特征值向量行列式数学物理力热电磁运动学代数几何分析坚持执意精心详述模糊含混弹性坚韧务实轻触屏幕任意位置进入下个上下滑旋转左右进出层级知识地图卡词复习难点标记已存忽略" \
  --format lvgl \
  --output fox_cn_14.c
```

**生成 fox_cn_24（24px 标题字体）：**

```bash
cd tools/lvgl_simulator/main/src/ui/fonts

lv_font_conv \
  --font /Library/Fonts/Arial\ Unicode.ttf \
  --size 24 \
  --bpp 4 \
  --range 0x20-0x7E \
  --symbols "微积分天极限连续性序列级数矩阵特征值向量行列式数学物理力热电磁运动学代数几何分析" \
  --format lvgl \
  --output fox_cn_24.c
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `--font` | 源 TrueType 字体路径（macOS 系统自带 Arial Unicode 包含完整 CJK） |
| `--size` | 输出像素大小 |
| `--bpp` | 每像素位数，4 = 16 级灰度抗锯齿 |
| `--range 0x20-0x7E` | 基本 ASCII 可打印字符 |
| `--range 0x2605-0x2605` | 星号 ★ 字符（用于"标记难点"功能） |
| `--symbols` | 项目实际使用的所有汉字（逐字列出） |
| `--format lvgl` | 输出 LVGL C 数组格式 |

> **Linux 用户**：如果没有 `Arial Unicode.ttf`，可使用文泉驿或 Noto Sans CJK：
> ```bash
> # Ubuntu
> sudo apt install fonts-noto-cjk
> # 然后使用：
> --font /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
> ```

### 5.5 如何添加新汉字

当你在 UI 代码中需要使用新的中文文本时：

1. **找到新增的汉字**：列出你新增文本中的所有汉字（去重）。

2. **追加到 `--symbols` 参数**：将新汉字追加到现有 `--symbols` 字符串末尾。例如新增文本"设置音量"，则追加 `设置音量`。

3. **重新运行生成命令**：执行上面的 `lv_font_conv` 命令重新生成 `.c` 文件。

4. **重新编译模拟器**：
   ```bash
   cd tools/lvgl_simulator/build
   cmake --build . -j$(sysctl -n hw.ncpu)
   ```

> **检查遗漏**：如果运行时发现某些汉字显示为空白方块，说明该字未包含在字体中，需要将其添加到 `--symbols` 并重新生成。

---

## 6. UI 开发工作流

### 6.1 文件结构

```
main/src/ui/
├── ui_theme.h              ← 全局主题：色彩宏、字体常量、屏幕尺寸
├── ui_screens.h            ← 公共头文件：所有屏幕的创建函数声明
├── ui_screen_manager.c     ← 屏幕管理器：维护当前屏幕状态，提供切换函数
├── ui_clock_screen.c       ← 时钟与倒计时主屏
├── ui_flashcard_screen.c   ← 闪卡 Tinder 划卡复习
├── ui_wiki_screen.c        ← 全息球体知识库
└── fonts/
    ├── fox_cn_14.c         ← 中文字体 14px (生成文件)
    └── fox_cn_24.c         ← 中文字体 24px (生成文件)
```

**核心文件说明：**

- **`ui_theme.h`**：定义全部色彩（如 `FOX_COLOR_BG = #151311`、`FOX_COLOR_PRIMARY = #F59E0B`）和字体常量。所有页面统一引用此文件，确保视觉一致性。
- **`ui_screens.h`**：声明三个屏幕的创建函数（`ui_clock_screen_create` 等）和更新函数（`ui_clock_update_time` 等），以及屏幕导航函数。
- **`ui_screen_manager.c`**：维护 `screen_id_t` 枚举状态，提供 `ui_show_clock_screen()`、`ui_show_flashcard_screen()`、`ui_show_wiki_screen()` 三个导航入口。

### 6.2 设计规范引用

所有 UI 实现的依据文档：

| 规范文档 | 路径 | 内容 |
|----------|------|------|
| UI 设计规范 | `foxsay_hardware_design_package/spec_markdown/ui_design_spec.md` | 色彩方案、8 大交互场景、手势逻辑 |
| 线框图规范 | `foxsay_hardware_design_package/spec_markdown/ui_wireframe_spec.md` | 像素级坐标 (X, Y, W, H)、控件布局参数表 |

**关键色彩规范**（已在 `ui_theme.h` 中定义）：

| 语义 | 宏名称 | 色值 | 用途 |
|------|--------|------|------|
| 背景 | `FOX_COLOR_BG` | `#151311` | 暗温巧克力色全局背景 |
| 高亮 | `FOX_COLOR_PRIMARY` | `#F59E0B` | 活力琥珀橙，焦点、进度、强调 |
| 正文 | `FOX_COLOR_TEXT` | `#FFF7ED` | 温暖粉白色，主要内容文字 |
| 辅助 | `FOX_COLOR_MUTED` | `#BFAFA6` | 淡灰色，次要文字、提示 |
| 卡片 | `FOX_COLOR_CARD_BG` | `#1D1A18` | 卡片背景色 |
| 药丸 | `FOX_COLOR_PILL_BG` | `#231F1C` | 药丸/次级卡片背景 |
| 警告 | `FOX_COLOR_DANGER` | `#EF4444` | 警告红色 |

**坐标系**：左上角为原点 `(0, 0)`，X 轴向右递增，Y 轴向下递增。屏幕尺寸 **320×240**。

### 6.3 截图验证闭环

完整开发流程如下：

```
修改 UI 代码 → 编译模拟器 → 运行 → 截图 → 查看 PNG → 确认/调整
```

**一步到位命令**（从项目根目录执行）：

```bash
# 编译
cd tools/lvgl_simulator/build && cmake --build . -j$(sysctl -n hw.ncpu)

# 运行（会自动截图三个屏幕，然后保持窗口运行）
../bin/main

# Ctrl+C 停止后，转换截图
cd ..
python3 screenshot.py screenshot_clock.bin screenshot_clock.png
python3 screenshot.py screenshot_flash.bin screenshot_flash.png
python3 screenshot.py screenshot_wiki.bin screenshot_wiki.png

# 用系统预览打开查看
open screenshot_clock.png screenshot_flash.png screenshot_wiki.png
```

### 6.4 手势交互模拟

模拟器中通过 SDL2 将鼠标操作映射为触摸事件：

| 鼠标操作 | 模拟的触摸手势 | 在 FoxSay 中的功能 |
|----------|---------------|-------------------|
| 按住左键 + 向左拖动 | 左滑 (`LV_DIR_LEFT`) | 时钟页 → 闪卡页 |
| 按住左键 + 向右拖动 | 右滑 (`LV_DIR_RIGHT`) | 时钟页 → 知识库页 |
| 按住左键 + 向上拖动 | 上滑 (`LV_DIR_TOP`) | 闪卡页：标记难点并飞卡 |
| 按住左键 + 向下拖动 | 下滑 (`LV_DIR_BOTTOM`) | 闪卡页：切换下一个 |
| 单击左键 | 点击 | 闪卡页：翻转显示答案 / 切下一个 |

> **注意**：手势需要一定的拖动距离才能被 LVGL 识别（默认阈值约 50px）。如果滑动没反应，尝试加大拖动幅度。

---

## 7. 屏幕导航架构

### 7.1 三个核心界面

| 界面 | 创建函数 | 说明 |
|------|----------|------|
| **时钟主屏** | `ui_clock_screen_create()` | 大字号数字时钟 (48px)、小狐狸占位、倒计时药丸卡片、顶部进度条 |
| **闪卡复习** | `ui_flashcard_screen_create()` | 280×170 主卡片、Tinder 式划卡交互、上滑标记难点带飞卡动画 |
| **知识库** | `ui_wiki_screen_create()` | 父/焦点/子三级节点显示、橙色发光边框焦点节点、左右兄弟节点 |

### 7.2 手势导航逻辑

```
                    左滑
    时钟主屏 ───────────────→ 闪卡复习
        ↑                         │
        │ 右滑                    │ 右滑
        │                         ↓
    知识库 ←─────────────── (返回时钟)
                    左滑
```

详细导航规则：

- **时钟主屏**：左滑 → 闪卡 | 右滑 → 知识库
- **闪卡页面**：右滑 → 返回时钟 | 上滑 → 标记难点并下一张 | 下滑 → 下一张
- **知识库页面**：左滑 → 返回时钟 | 上下滑 → 旋转浏览节点 | 右滑 → 进入下一层级

导航由 `ui_screen_manager.c` 统一管理，通过 `screen_id_t` 枚举跟踪当前屏幕状态。

---

## 8. 常见问题

### 8.1 CMake 找不到 SDL2

**现象**：

```
CMake Error: Could not find a package configuration file provided by "SDL2"
```

**解决方案**：

```bash
# macOS：确认 SDL2 已安装
brew install sdl2

# 如果仍然报错，手动指定 SDL2 路径
cmake -DSDL2_DIR=$(brew --prefix sdl2)/lib/cmake/SDL2 ..

# 或者设置 CMAKE_PREFIX_PATH
export CMAKE_PREFIX_PATH="$(brew --prefix sdl2)"
cmake ..
```

**Ubuntu/Debian**：

```bash
sudo apt-get install libsdl2-dev

# 如果 pkg-config 找不到
export PKG_CONFIG_PATH="/usr/lib/x86_64-linux-gnu/pkgconfig:$PKG_CONFIG_PATH"
```

### 8.2 中文显示为豆腐块（空白方块）

**现象**：UI 中的中文字符显示为空白方块或乱码。

**排查步骤**：

1. **确认字体文件存在**：
   ```bash
   ls -la tools/lvgl_simulator/main/src/ui/fonts/fox_cn_*.c
   ```

2. **确认代码中引用了中文字体**：
   ```c
   // 正确：使用 fox_cn_14 中文字体
   lv_obj_set_style_text_font(label, &fox_cn_14, 0);

   // 错误：使用了 Montserrat（不含中文）
   lv_obj_set_style_text_font(label, &lv_font_montserrat_14, 0);
   ```

3. **确认目标汉字已包含在字体中**：查看 `fox_cn_14.c` 文件头部的 `--symbols` 参数，检查是否包含你使用的所有汉字。

4. **重新生成字体**：如果缺少某些汉字，按照 [5.5 如何添加新汉字](#55-如何添加新汉字) 重新生成字体文件。

5. **确认 `LV_USE_FONT_COMPRESSED` 已启用**：
   ```bash
   grep LV_USE_FONT_COMPRESSED tools/lvgl_simulator/lv_conf.h
   # 应输出：#define LV_USE_FONT_COMPRESSED 1
   ```

### 8.3 ESP-IDF 克隆慢或失败

**现象**：`git clone --recursive` 下载速度极慢或超时。

**解决方案**：

1. **使用镜像源**（推荐国内用户）：
   ```bash
   # 使用乐鑫中国镜像
   git clone -b v5.5.1 --recursive https://gitee.com/EspressifSystems/esp-idf.git
   ```

2. **分步克隆**（避免一次性下载过多）：
   ```bash
   git clone -b v5.5.1 https://github.com/espressif/esp-idf.git
   cd esp-idf
   # 设置子模块深度为 1
   git submodule update --init --recursive --depth 1
   ```

3. **设置 Git 代理**：
   ```bash
   git config --global http.proxy http://127.0.0.1:7890
   git config --global https.proxy http://127.0.0.1:7890
   ```

4. **注意**：本仓库 `tools/esp-idf/` 已包含完整 ESP-IDF v5.5.1，通常无需额外克隆。

### 8.4 压缩字体报错

**现象**：

```
undefined reference to `lv_font_fmt_txt_create'
```

或运行时字体加载失败。

**解决方案**：

1. **确认 `lv_conf.h` 中启用了压缩字体**：
   ```c
   #define LV_USE_FONT_COMPRESSED 1
   ```
   本项目 `lv_conf.h` 第 639 行已设置此项。

2. **确认字体生成时使用了正确的 `--format`**：
   ```bash
   # 确保使用 lvgl 格式（不是 bin 格式）
   lv_font_conv ... --format lvgl --output fox_cn_14.c
   ```

3. **确认字体 C 文件已加入编译**：检查 `CMakeLists.txt` 中的 `add_executable` 是否包含字体源文件：
   ```cmake
   ${PROJECT_SOURCE_DIR}/main/src/ui/fonts/fox_cn_14.c
   ${PROJECT_SOURCE_DIR}/main/src/ui/fonts/fox_cn_24.c
   ```

4. **重新清理编译**：
   ```bash
   cd tools/lvgl_simulator
   rm -rf build
   mkdir build && cd build
   cmake ..
   cmake --build . -j$(sysctl -n hw.ncpu)
   ```

### 8.5 Apple Silicon (M1/M2/M3) 编译问题

**现象**：CMake 报架构不匹配或链接错误。

**解决方案**：

```bash
# 确认 Homebrew 安装的是 ARM64 版本的 SDL2
file $(brew --prefix sdl2)/lib/libSDL2.dylib
# 应显示 arm64

# 如果之前安装了 x86 版本，重新安装
brew reinstall sdl2

# 清理并重新编译
cd tools/lvgl_simulator
rm -rf build
mkdir build && cd build
cmake ..
cmake --build . -j$(sysctl -n hw.ncpu)
```

### 8.6 模拟器窗口无响应或黑屏

**现象**：运行 `./bin/main` 后窗口黑屏或立即崩溃。

**排查步骤**：

1. 确认 LVGL 子模块已正确初始化：
   ```bash
   cd tools/lvgl_simulator
   git submodule update --init --recursive
   ```

2. 确认 `lv_conf.h` 位于 `lvgl/` 同级目录（当前项目的默认位置）。

3. 使用 Debug 模式编译以获取详细日志：
   ```bash
   cd build
   cmake -DCMAKE_BUILD_TYPE=Debug ..
   cmake --build . -j$(sysctl -n hw.ncpu)
   ./bin/main 2>&1 | head -50
   ```
