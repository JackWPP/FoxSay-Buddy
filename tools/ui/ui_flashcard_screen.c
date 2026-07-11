/**
 * @file ui_flashcard_screen.c
 * FoxSay 闪卡 Tinder 划卡复习 (Flashcard Swipe)
 *
 * 布局依据 ui_wireframe_spec.md:
 *  - 左上角进度 "Card 12/50"
 *  - 主卡片 280x170, 圆角 8px
 *  - 生词 32px 粗体居中
 *  - 全屏轻触热区切换下一个
 *  - 上滑标记难点, 下滑下一个
 */
#include "ui_theme.h"

/**********************
 *  STATIC VARIABLES
 **********************/
static lv_obj_t * flash_screen = NULL;
static lv_obj_t * card = NULL;
static lv_obj_t * lbl_progress = NULL;
static lv_obj_t * lbl_word = NULL;
static lv_obj_t * lbl_phonetic = NULL;
static lv_obj_t * lbl_hint = NULL;

/* 模拟单词数据 */
static const char * demo_words[][3] = {
    {"persist",  "[pə'sɪst]",    "vi. 坚持，执意"},
    {"elaborate","[ɪ'læbərət]",  "adj. 精心的；v. 详述"},
    {"ambiguous","[æm'bɪɡjuəs]", "adj. 模糊的，含混的"},
    {"resilient","[rɪ'zɪliənt]", "adj. 有弹性的，坚韧的"},
    {"pragmatic","[præɡ'mætɪk]", "adj. 务实的，实用的"},
};
static int word_count = 5;
static int current_idx = 0;
static bool showing_answer = false;

/**********************
 *  STATIC FUNCTIONS
 **********************/

static void update_card_content(void)
{
    lv_label_set_text_fmt(lbl_progress, "Card %d/%d", current_idx + 1, word_count);
    lv_label_set_text(lbl_word, demo_words[current_idx][0]);

    if(showing_answer) {
        lv_label_set_text(lbl_phonetic, demo_words[current_idx][1]);
        lv_label_set_text(lbl_hint, demo_words[current_idx][2]);
        lv_obj_clear_flag(lbl_phonetic, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(lbl_hint, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_add_flag(lbl_phonetic, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(lbl_hint, LV_OBJ_FLAG_HIDDEN);
    }
}

/** 单击切换答案/下一个 */
static void on_card_clicked(lv_event_t * e)
{
    if(!showing_answer) {
        showing_answer = true;
        update_card_content();
    } else {
        /* 下一个单词 */
        current_idx = (current_idx + 1) % word_count;
        showing_answer = false;
        update_card_content();
    }
}

/** 手势: 上滑标记难点, 下滑下一个 */
static void on_gesture(lv_event_t * e)
{
    lv_indev_t * indev = lv_indev_active();
    lv_dir_t dir = lv_indev_get_gesture_dir(indev);

    if(dir == LV_DIR_TOP) {
        /* 上滑: 标记难点 (闪烁星标动效) */
        lv_obj_set_style_border_color(card, FOX_COLOR_PRIMARY, 0);
        lv_obj_set_style_border_width(card, 2, 0);
        lv_obj_set_style_border_opa(card, LV_OPA_COVER, 0);

        /* 卡片向上飞出动画 */
        lv_anim_t a;
        lv_anim_init(&a);
        lv_anim_set_var(&a, card);
        lv_anim_set_values(&a, lv_obj_get_y(card), -250);
        lv_anim_set_duration(&a, 300);
        lv_anim_set_path_cb(&a, lv_anim_path_ease_in);
        lv_anim_start(&a);

        /* 延迟切下一个 */
        current_idx = (current_idx + 1) % word_count;
        showing_answer = false;
        /* 动画结束后应重置卡片位置, 这里简化处理 */
    }
    else if(dir == LV_DIR_BOTTOM) {
        /* 下滑: 下一个 */
        current_idx = (current_idx + 1) % word_count;
        showing_answer = false;
        update_card_content();
    }
    else if(dir == LV_DIR_RIGHT) {
        /* 右滑返回时钟主屏 */
        extern void ui_show_clock_screen(void);
        ui_show_clock_screen();
    }
}

/** 创建主卡片 */
static void create_flashcard(lv_obj_t * parent)
{
    card = lv_obj_create(parent);
    lv_obj_set_size(card, 280, 170);
    lv_obj_align(card, LV_ALIGN_TOP_MID, 0, 35);
    lv_obj_set_style_bg_color(card, FOX_COLOR_CARD_BG, 0);
    lv_obj_set_style_bg_opa(card, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(card, 0, 0);
    lv_obj_set_style_radius(card, 8, 0);
    lv_obj_set_style_pad_all(card, 10, 0);
    lv_obj_set_style_shadow_width(card, 10, 0);
    lv_obj_set_style_shadow_color(card, lv_color_hex(0x000000), 0);
    lv_obj_set_style_shadow_opa(card, LV_OPA_50, 0);
    lv_obj_set_style_shadow_offset_y(card, 3, 0);
    lv_obj_clear_flag(card, LV_OBJ_FLAG_SCROLLABLE);

    /* 生词主体 */
    lbl_word = lv_label_create(card);
    lv_obj_set_style_text_color(lbl_word, FOX_COLOR_TEXT, 0);
    lv_obj_set_style_text_font(lbl_word, &lv_font_montserrat_32, 0);
    lv_obj_align(lbl_word, LV_ALIGN_TOP_MID, 0, 15);

    /* 音标 */
    lbl_phonetic = lv_label_create(card);
    lv_obj_set_style_text_color(lbl_phonetic, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(lbl_phonetic, &lv_font_montserrat_16, 0);
    lv_obj_align(lbl_phonetic, LV_ALIGN_TOP_MID, 0, 60);

    /* 翻译 */
    lbl_hint = lv_label_create(card);
    lv_obj_set_style_text_color(lbl_hint, FOX_COLOR_TEXT, 0);
    lv_obj_set_style_text_font(lbl_hint, &lv_font_montserrat_16, 0);
    lv_obj_align(lbl_hint, LV_ALIGN_TOP_MID, 0, 85);

    /* 上滑提示 */
    lv_obj_t * star_hint = lv_label_create(card);
    lv_label_set_text(star_hint, "Swipe Up to Star");
    lv_obj_set_style_text_color(star_hint, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(star_hint, &lv_font_montserrat_12, 0);
    lv_obj_set_style_text_opa(star_hint, LV_OPA_40, 0);
    lv_obj_align(star_hint, LV_ALIGN_BOTTOM_MID, 0, 0);
}

/**********************
 *  GLOBAL FUNCTIONS
 **********************/

lv_obj_t * ui_flashcard_screen_create(void)
{
    if(flash_screen) {
        lv_obj_delete(flash_screen);
    }

    flash_screen = lv_obj_create(lv_screen_active());
    lv_obj_set_size(flash_screen, FOX_SCREEN_W, FOX_SCREEN_H);
    lv_obj_set_style_bg_color(flash_screen, FOX_COLOR_BG, 0);
    lv_obj_set_style_bg_opa(flash_screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(flash_screen, 0, 0);
    lv_obj_set_style_pad_all(flash_screen, 0, 0);
    lv_obj_set_style_radius(flash_screen, 0, 0);
    lv_obj_clear_flag(flash_screen, LV_OBJ_FLAG_SCROLLABLE);

    /* 手势 */
    lv_obj_add_flag(flash_screen, LV_OBJ_FLAG_GESTURE_BUBBLE);
    lv_obj_add_event_cb(flash_screen, on_gesture, LV_EVENT_GESTURE, NULL);

    /* 进度文本 */
    lbl_progress = lv_label_create(flash_screen);
    lv_obj_set_style_text_color(lbl_progress, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(lbl_progress, &lv_font_montserrat_12, 0);
    lv_obj_align(lbl_progress, LV_ALIGN_TOP_LEFT, 15, 12);

    /* 主卡片 */
    create_flashcard(flash_screen);

    /* 卡片点击事件 (全屏热区) */
    lv_obj_add_flag(card, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(card, on_card_clicked, LV_EVENT_CLICKED, NULL);

    /* 底部提示 */
    lv_obj_t * bottom_hint = lv_label_create(flash_screen);
    lv_label_set_text(bottom_hint, "轻触屏幕任意位置进入下一个");
    lv_obj_set_style_text_color(bottom_hint, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(bottom_hint, &fox_cn_14, 0);
    lv_obj_set_style_text_opa(bottom_hint, LV_OPA_40, 0);
    lv_obj_align(bottom_hint, LV_ALIGN_BOTTOM_MID, 0, -5);

    current_idx = 0;
    showing_answer = false;
    update_card_content();

    return flash_screen;
}
