/**
 * @file ui_theme.h
 * FoxSay UI 全局主题与色彩规范
 */
#ifndef UI_THEME_H
#define UI_THEME_H

#include "lvgl/lvgl.h"

/* ====== 色彩定义 (依据 ui_design_spec.md) ====== */

/* 背景: 暗温巧克力色 */
#define FOX_COLOR_BG        lv_color_hex(0x151311)

/* 高亮: 活力琥珀橙 */
#define FOX_COLOR_PRIMARY   lv_color_hex(0xF59E0B)

/* 正文: 温暖粉白色 */
#define FOX_COLOR_TEXT      lv_color_hex(0xFFF7ED)

/* 辅助: 淡灰色 */
#define FOX_COLOR_MUTED     lv_color_hex(0xBFAFA6)

/* 卡片背景 */
#define FOX_COLOR_CARD_BG   lv_color_hex(0x1D1A18)

/* 药丸/次级卡片背景 */
#define FOX_COLOR_PILL_BG   lv_color_hex(0x231F1C)

/* 警告红 */
#define FOX_COLOR_DANGER    lv_color_hex(0xEF4444)

/* ====== 字体大小常量 ====== */
#define FOX_FONT_CLOCK      48
#define FOX_FONT_WORD        32
#define FOX_FONT_TITLE       24
#define FOX_FONT_BODY        16
#define FOX_FONT_SMALL       14
#define FOX_FONT_TINY        12

/* 中文字体 (生成的位图字体, 包含常用汉字) */
extern const lv_font_t fox_cn_14;
extern const lv_font_t fox_cn_24;

/* ====== 屏幕尺寸 ====== */
#define FOX_SCREEN_W         320
#define FOX_SCREEN_H         240

#endif /* UI_THEME_H */
