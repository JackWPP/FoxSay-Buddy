# FoxSay 2.0寸屏 UI 界面生图提示词 (Prompts) 设计指南 (纯触屏版)

本指南为您整理了 **8 个核心交互场景** 的生图提示词。提示词进行了纯触控的交互映射优化，适用于 **Midjourney**、**DALL-E 3** 或其他 **Gemini/Imagen** 模型，能够输出统一色调（暖巧克力炭黑 + 琥珀橙）的 2.0 寸极简排版样机。

---

## 🎨 视觉基准与通用配置 (Global Style Guide)
在您自己输入提示词时，建议采用以下通用参数（如果是 Midjourney 可以在结尾加上 `--ar 4:3` 确保比例一致）：
*   **画幅比例 (Aspect Ratio)**: `4:3`（最契合板载 2.0 寸 320x240 屏幕）
*   **背景色 (Background)**: `#151311` 或 `Warm dark-chocolate charcoal background`
*   **发光强调色 (Accent)**: `#F59E0B` 或 `Glowing vibrant amber orange`
*   **主文字色 (Text)**: `#FFF7ED` 或 `Warm white / Cozy cream white`
*   **主体风格**: `Typography-driven, minimal retro-console UI style (like Panic Playdate)`
*   **避坑词**: `No device mockup frame, no hands, no mock-up device screen` (如果您只想要纯屏幕 UI，请务必声明不要设备框和手)。

---

## 🔍 8 大场景提示词设计

### 场景 1：时钟与计时主屏 (Main Standby & Countdown)
*   **中文含义**：极简时钟待机屏。顶部特大粗体数码钟 10:24，中间坐着一只等待的扁平化卡通小狐狸，底部是一个暖橙色倒计时圆角卡片“微积分: 5天”。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: High-fidelity UI design for a 2-inch screen with a 4:3 aspect ratio. Warm dark-chocolate background (#151311) with a soft warm amber glow. Extremely minimal and typography-driven UI: a giant bold digital clock '10:24' at the top, a simple flat-design cartoon fox mascot sitting in the center looking alert, and a clean rounded rectangle card at the bottom displaying '微积分: 5天' in vibrant amber orange. Modern minimal game-console style, no device mockup frame.

---

### 场景 2：小狐狸物理躺平休眠 (Low-Power Sleeping)
*   **中文含义**：低功耗休眠屏。暗色巧克力背景，中间是一只闭着眼睛睡在小棉垫上的可爱卡通狐狸，上方有微弱的“Zzz”字样，顶部有极细的时间 10:25，整体低对比度昏暗。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: High-fidelity UI mockup for a 2-inch screen, 4:3 aspect ratio, representing low-power sleep mode. Theme: Very dim, dark warm-chocolate background. In the center, a cute cartoon fox mascot is lying flat on its back, sleeping soundly on a tiny pillow with soft 'Zzz' bubbles floating up. Faint digital clock '10:25' at the top in thin warm-white font. Faint amber text at the bottom says '已休眠 (Sleeping)'. Minimalist, peaceful, designed for dark ambient light. Just the screen UI, no physical frame.

---

### 场景 3：极简英文单词卡复习 (Vocabulary Flashcard)
*   **中文含义**：单词复习闪卡（触屏单击任意位置进入下一个）。居中巨大粗体英文单词 `persist`，下方是小号音标和中文意思，底部是一个巨大的橙色胶囊按钮，提示“轻触屏幕切换”，整体高度精简易读。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: Cozy UI design for a 2-inch screen (4:3 ratio) showing a minimal English vocabulary flashcard. Warm charcoal dark background, glowing warm amber highlights. In the center, the English word 'persist' in massive bold cream white text. Below it, the phonetic '[pəˈsɪst]' and simple translation 'vi. 坚持' in clear legible warm white. At the bottom, a large pill-shaped bar saying '轻触屏幕进入下一个 (Tap Screen to Next)' in vibrant warm amber. Typography-driven, no sidebars, high readability. Just the screen UI.

---

### 场景 4：数学公式与难点标记卡片 (Math Formula & Mark Difficulty)
*   **中文含义**：理科公式复习。背景为极细的物理网格线，中间显示漂亮的欧拉恒等式公式，底部是提示“上滑记难点，下滑下一个”。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: Premium high-fidelity UI design for a 2-inch screen (4:3 ratio). Theme: Warm dark-chocolate grid paper texture background (#14110e) with a soft amber glow. In the center, an elegant math formula card showing Euler's Identity 'e^(iπ) + 1 = 0' in large math serif font. Below it, a clean label reads '欧拉公式'. At the bottom, a glowing amber indicator bar displaying 'Swipe Up to Star (上滑记难点)' in warm white. Retro-modern console UI style.

---

### 场景 5：社区新知推送与 Wiki 决策 (Community Push & Wiki Decision)
*   **中文含义**：新知滑卡决策物（Tinder 式卡片左右滑动）。卡片正中显示大字“太阳光到达地球需要8分钟”，右侧有一只探头出来的小狐狸，滑动卡片向右代表“存入Wiki”，向左代表“没用”。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: Premium high-fidelity UI design for a 2-inch screen (4:3 ratio) demonstrating a Tinder-style card swiping gesture. Theme: Warm dark-chocolate background with a soft amber glow. A card displaying '太阳光到达地球需要8分钟' in bold cream text is shown tilted mid-swipe to the right, showing an amber stamp '存入Wiki' (Save to Wiki). A cute cartoon fox head peaks from the right edge with a curious expression. High-readability retro-console style. Just the screen UI.

---

### 场景 6：极简滚轮式层级滑动 (Hierarchy Slider Menu)
*   **中文含义**：知识大纲滚轮导航（滑动手势横扫切换）。呈 3D 纵向滚动弧线排列，最上面是半透明较小的“数学”，中间是高亮带橙色框的超大“微积分”，下面是半透明较小的“极限”。左右两侧有极简指示手势箭头。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: Cozy UI design for a 2-inch screen (4:3 ratio) showing a minimal sliding menu for a knowledge base. Warm charcoal dark background, glowing warm amber accents. The layout is optimized for a tiny screen: in the center, a vertical scrolling list with only three giant items. Top item is '数学' (small and faded). Center item is '微积分' in massive bold cream text highlighted with a thick warm amber border. Bottom item is '极限' (small and faded). Left and right sides have simple minimalist arrow icons indicating touch sliding navigation. No search bars, no sidebars, extremely clean and high-contrast for a 2-inch display. Just the screen UI.

---

### 场景 7：“我说你译”语音口语交互 (Voice Translation)
*   **中文含义**：语音练习录音界面。屏幕顶部是跳动的发光橙色正弦音频波形，中间引导“请说：'我坚持我的决定'”，下方是麦克风和“正在聆听...”，右下角为戴耳机的小狐狸头像。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: Premium high-fidelity UI design for a 2-inch screen (4:3 ratio) of a voice translation interactive screen. Theme: Warm dark-chocolate background with amber glow. At the top, a bold glowing amber voice waveform. In the center, a simple text prompt '请说: "我坚持我的决定"' in bold cream text. Below it, a microphone icon with the status text '正在聆听...' (Listening...). A small cute cartoon fox head wearing headphones is shown in a corner. Clean, high-readability retro-console style. Just the screen UI.

---

### 场景 8：疲劳提醒与像素解压游戏 (Fatigue Break & Game)
*   **中文含义**：解压小游戏。中间是一个擦汗并比大拇指的卡通狐狸形象，气泡框显示“休息一下吧! ☕”，底部是一个大橙色物理触控按钮“开始游戏 (Play)”。
*   **Midjourney / DALL-E 3 提示词**：
    > **Prompt**: Cozy UI design for a 2-inch screen (4:3 ratio) of a desktop companion reacting to user fatigue. Warm charcoal background with a soft orange glow. In the center, a large, cute cartoon fox face looking supportive and happy, with a clear speech bubble saying '休息一下吧! ☕' (Take a break!) in large bold text. Below it, a simple large play button displaying '开始游戏 (Play)' in warm amber for a quick relaxation game. Minimalist, bold elements, high readability on a small screen. Just the screen UI.
