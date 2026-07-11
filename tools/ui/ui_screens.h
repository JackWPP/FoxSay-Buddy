/**
 * @file ui_screens.h
 * FoxSay UI 屏幕管理头文件
 */
#ifndef UI_SCREENS_H
#define UI_SCREENS_H

#include "lvgl/lvgl.h"

/* 各屏幕创建函数 */
lv_obj_t * ui_clock_screen_create(void);
lv_obj_t * ui_flashcard_screen_create(void);
lv_obj_t * ui_wiki_screen_create(void);

/* 更新函数 */
void ui_clock_update_time(int hour, int min);
void ui_clock_update_progress(int percent);

/* 屏幕导航 */
void ui_show_clock_screen(void);
void ui_show_flashcard_screen(void);
void ui_show_wiki_screen(void);

#endif /* UI_SCREENS_H */
