/**
 * @file ui_clock_screen.c
 * FoxSay 时钟与计时主屏 (Time & Timer Screen)
 */
#include "ui_theme.h"

static lv_obj_t * clock_screen = NULL;
static lv_obj_t * lbl_time = NULL;
static lv_obj_t * lbl_countdown = NULL;
static lv_obj_t * progress_bar = NULL;

static int sim_hour = 10;
static int sim_min  = 24;

/** 顶部进度条 */
static void create_progress_bar(lv_obj_t * parent)
{
    progress_bar = lv_obj_create(parent);
    lv_obj_set_size(progress_bar, 200, 2);
    lv_obj_set_pos(progress_bar, 0, 1);
    lv_obj_set_style_bg_color(progress_bar, FOX_COLOR_PRIMARY, 0);
    lv_obj_set_style_bg_opa(progress_bar, LV_OPA_80, 0);
    lv_obj_set_style_border_width(progress_bar, 0, 0);
    lv_obj_set_style_radius(progress_bar, 0, 0);
    lv_obj_set_style_pad_all(progress_bar, 0, 0);
    lv_obj_clear_flag(progress_bar, LV_OBJ_FLAG_SCROLLABLE);
}

/** 居中大字号时钟 */
static void create_clock_label(lv_obj_t * parent)
{
    lbl_time = lv_label_create(parent);
    lv_label_set_text_fmt(lbl_time, "%02d:%02d", sim_hour, sim_min);
    lv_obj_set_style_text_color(lbl_time, FOX_COLOR_TEXT, 0);
    lv_obj_set_style_text_font(lbl_time, &lv_font_montserrat_48, 0);
    lv_obj_align(lbl_time, LV_ALIGN_TOP_MID, 0, 50);
}

/** 小狐狸占位 (后续换图片) */
static void create_fox_placeholder(lv_obj_t * parent)
{
    lv_obj_t * fox = lv_obj_create(parent);
    lv_obj_set_size(fox, 70, 70);
    lv_obj_align(fox, LV_ALIGN_TOP_MID, 0, 115);
    lv_obj_set_style_bg_color(fox, FOX_COLOR_CARD_BG, 0);
    lv_obj_set_style_bg_opa(fox, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(fox, 1, 0);
    lv_obj_set_style_border_color(fox, FOX_COLOR_PRIMARY, 0);
    lv_obj_set_style_border_opa(fox, LV_OPA_50, 0);
    lv_obj_set_style_radius(fox, 12, 0);
    lv_obj_clear_flag(fox, LV_OBJ_FLAG_SCROLLABLE);

    lv_obj_t * lbl = lv_label_create(fox);
    lv_label_set_text(lbl, "/\\\n/__\\");
    lv_obj_set_style_text_color(lbl, FOX_COLOR_PRIMARY, 0);
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_14, 0);
    lv_obj_center(lbl);
}

/** 底部倒计时药丸卡片 (使用中文字体) */
static void create_countdown_pill(lv_obj_t * parent)
{
    lv_obj_t * pill = lv_obj_create(parent);
    lv_obj_set_size(pill, LV_SIZE_CONTENT, 26);
    lv_obj_set_style_min_width(pill, 120, 0);
    lv_obj_align(pill, LV_ALIGN_TOP_MID, 0, 195);
    lv_obj_set_style_bg_color(pill, FOX_COLOR_PILL_BG, 0);
    lv_obj_set_style_bg_opa(pill, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(pill, 0, 0);
    lv_obj_set_style_radius(pill, 13, 0);
    lv_obj_set_style_pad_hor(pill, 16, 0);
    lv_obj_set_style_pad_ver(pill, 4, 0);
    lv_obj_clear_flag(pill, LV_OBJ_FLAG_SCROLLABLE);

    lbl_countdown = lv_label_create(pill);
    lv_label_set_text(lbl_countdown, "微积分: 5天");
    lv_obj_set_style_text_color(lbl_countdown, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(lbl_countdown, &fox_cn_14, 0);
    lv_obj_center(lbl_countdown);
}

/** 手势提示 */
static void create_swipe_hint(lv_obj_t * parent)
{
    lv_obj_t * hint = lv_label_create(parent);
    lv_label_set_text(hint, "< swipe >");
    lv_obj_set_style_text_color(hint, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(hint, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_opa(hint, LV_OPA_40, 0);
    lv_obj_align(hint, LV_ALIGN_BOTTOM_MID, 0, -8);
}

extern void ui_show_flashcard_screen(void);
extern void ui_show_wiki_screen(void);

static void on_gesture(lv_event_t * e)
{
    lv_indev_t * indev = lv_indev_active();
    lv_dir_t dir = lv_indev_get_gesture_dir(indev);
    if(dir == LV_DIR_LEFT)  ui_show_flashcard_screen();
    else if(dir == LV_DIR_RIGHT) ui_show_wiki_screen();
}

lv_obj_t * ui_clock_screen_create(void)
{
    if(clock_screen) lv_obj_delete(clock_screen);

    clock_screen = lv_obj_create(lv_screen_active());
    lv_obj_set_size(clock_screen, FOX_SCREEN_W, FOX_SCREEN_H);
    lv_obj_set_style_bg_color(clock_screen, FOX_COLOR_BG, 0);
    lv_obj_set_style_bg_opa(clock_screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(clock_screen, 0, 0);
    lv_obj_set_style_pad_all(clock_screen, 0, 0);
    lv_obj_set_style_radius(clock_screen, 0, 0);
    lv_obj_clear_flag(clock_screen, LV_OBJ_FLAG_SCROLLABLE);

    lv_obj_add_flag(clock_screen, LV_OBJ_FLAG_GESTURE_BUBBLE);
    lv_obj_add_event_cb(clock_screen, on_gesture, LV_EVENT_GESTURE, NULL);

    create_progress_bar(clock_screen);
    create_clock_label(clock_screen);
    create_fox_placeholder(clock_screen);
    create_countdown_pill(clock_screen);
    create_swipe_hint(clock_screen);

    return clock_screen;
}

void ui_clock_update_time(int hour, int min)
{
    if(lbl_time) lv_label_set_text_fmt(lbl_time, "%02d:%02d", hour, min);
}

void ui_clock_update_progress(int percent)
{
    if(progress_bar) {
        int w = (FOX_SCREEN_W * percent) / 100;
        lv_obj_set_width(progress_bar, w);
    }
}
