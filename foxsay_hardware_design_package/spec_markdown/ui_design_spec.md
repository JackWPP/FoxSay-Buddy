# FoxSay 2寸屏极简 UI 设计规范与视觉方案 (纯触屏版)

本规范紧密依据 [hardware_design_analysis.md](file:///Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/hardware_design_analysis.md)，针对 2.0 寸电容触摸屏进行**纯触屏优先 (Pure Touch-First)** 的界面布局与动效定制。

---

## 🎨 视觉主题与色彩规范

*   **背景 (Background)**: `#151311` (暗温巧克力色) + 微小发光暖边，辅以淡网格底纹以增强科技质感。
*   **高亮 (Highlight)**: `#F59E0B` (活力琥珀橙) 用于当前焦点、公式高亮变量和核心手势路径。
*   **常规字 (Body Text)**: `#FFF7ED` (温暖粉白色) 以不同字重和透明度区分层级，保证小屏的极高识别度。

---

## 🎨 全场景界面视觉样机展示 (2-inch UI Carousel)

*(注：样机图片目前保留第二版命名，但底部的“按键”逻辑已在软件交互规范中被纯触控手势完全替代)*

````carousel
![1. 极简待机与倒计时](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/main_standby_2inch_1783741684211.jpg)
<!-- slide -->
![2. 小狐狸物理躺平休眠](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/flat_sleep_2inch_1783741835169.jpg)
<!-- slide -->
![3. 极简英文单词卡复习](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/flashcard_2inch_1783741698353.jpg)
<!-- slide -->
![4. 数学公式与难点标记卡片](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/math_formula_2inch_1783741789563.jpg)
<!-- slide -->
![5. 社区新知推送与Wiki决策](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/new_knowledge_wiki_2inch_1783741802682.jpg)
<!-- slide -->
![6. 极简滚轮式层级滑动搜索](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/search_2inch_1783741725379.jpg)
<!-- slide -->
![7. “我说你译”语音口语交互](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/voice_translation_2inch_1783741819540.jpg)
<!-- slide -->
![8. 疲劳提醒与像素解压游戏](/Users/xuchencen/.gemini/antigravity/brain/a9cf3e2d-359a-4712-bcc1-97c50b831cee/emotion_2inch_1783741712879.jpg)
````

---

## 🔍 适配 2.0 寸电容触摸屏的 8 大交互场景详解

---

### 第一板块：核心系统与电源姿态管理

#### 1. 极简待机与倒计时 (Main Standby & Countdown)
*   **触控交互**：
    *   **双击屏幕 (Double Tap)**：轻按两下唤醒屏幕。
    *   **屏幕顶部边缘下拉 (Swipe Down from Top Edge)**：滑出下拉状态栏（声音控制面板）。可以静音麦克风、调节扬声器音量。点击菜单外部向上滑回。
*   **物理传感**：设备水平躺平，自动进入休眠屏。

#### 2. 小狐狸物理躺平休眠 (Low-Power Sleeping)
*   **触控交互**：
    *   全屏防误触锁止，仅响应**双击屏幕**以手动唤醒小狐狸。

---

### 第二板块：双轨制闪卡学习系统

#### 3. 极简英文单词卡复习 (Vocabulary Flashcard)
*   **设计逻辑**：无痛、无决策门槛复习。
*   **触控交互 ➔ 单击任意位置切词 (Tap anywhere to Next)**：
    *   取消所有精细按钮。整个屏幕卡片就是一个巨大的触摸热区。
    *   用户只需**轻触屏幕任意位置（单击）**，当前卡片就会向左滑出，并无缝切入下一个单词。
    *   无需做“认识/不认识”的逻辑判断（“不要背，看着就行”）。

#### 4. 数学公式与难点标记卡片 (Math Formula & Mark Difficulty)
*   **设计逻辑**：显示经典理科公式。
*   **触控交互**：
    *   **单击卡片 (Single Tap)**：卡片 3D 翻转，显现公式核心变量解释和推导。
    *   **向上滑动 (Swipe Up)**：卡片向上飞出并闪烁星标，标记为“★ 记难点”并归档入 Wiki。
    *   **向下滑动 (Swipe Down)**：切换到下一个公式。

#### 5. 社区新知推送与 Wiki 决策 (Community Push & Wiki Decision)
*   **触控交互（左右划卡 / Tinder Mode）**：
    *   **卡片右滑 (Swipe Right)**：将社区卡片朝右划走，释放后飞入屏幕右侧，提示“存入 Wiki 📁”，无缝同步进个人课程 Wiki。
    *   **卡片左滑 (Swipe Left)**：将卡片朝左划走，释放后飞出，提示“忽略 🗑️”。

---

### 第三板块：知识库检索与滑动层级

#### 6. 极简滚轮式层级滑动 (Hierarchy Slider Menu)
*   **触控交互**：
    *   **上下滑动 (Swipe Up/Down)**：旋转知识库大纲轮盘（当前选中项居中放大，上下项缩小淡化）。
    *   **向右滑动 (Swipe Right)**：手势横扫，**进入下一层**大纲。
    *   **向左滑动 (Swipe Left)**：手势横扫，**退回上一层**目录。

---

### 第四板块：多模态语音交互与情绪自适应

#### 7. “我说你译”语音口语交互 (Voice Translation)
*   **触控交互**：
    *   **长按屏幕中心 (Long Press to Record)**：长按手动开启录音，松手结束录音开始翻译（适合桌面环境）。
    *   **单击麦克风图标 (Tap Mic)**：切换自动监听和手动长按模式。
    *   **向左滑动 (Swipe Left)**：退出，返回时钟主屏。

#### 8. 疲劳提醒与像素解压游戏 (Fatigue Break)
*   **触控交互**：
    *   情绪预警弹出后，**轻触屏幕“PLAY”大按钮**，在 2.0 寸电容触摸屏上单指点击屏幕控制小狐狸跳跃，玩简易解压像素小游戏。
    *   **向右滑动 (Swipe Right)**：随时退出游戏，返回待机页面。

---

## 🛠️ 后续代码开发还原思路 (LVGL)

1.  **全局轻触事件切词**
    在单词复习页，直接为全屏根容器绑定点击事件 `LV_EVENT_CLICKED`，无需寻找特定按钮，极大提升小屏操作的舒适度：
    ```c
    static void on_word_screen_clicked(lv_event_t * e) {
        // 单击任意位置切换下一个单词
        show_next_word();
    }
    ```
2.  **卡片手势识别与动效**
    在 `LV_EVENT_GESTURE` 事件中，读取手势方向：
    *   `LV_DIR_TOP` (上滑) ➔ 调用 `lv_anim` 启动卡片飞向 Y 轴负方向，并在回调中触发“记难点”API。
    *   `LV_DIR_BOTTOM` (下滑) ➔ 卡片飞向 Y 轴正方向，切入下一个公式。
3.  **状态栏顶部下拉手势**
    捕获顶部边缘的 `LV_DIR_BOTTOM` 动作（限定起点 $Y < 20px$），驱动快捷声音控制面板从 $Y = -100px$ 平滑过渡滑入到 $Y = 0$。
