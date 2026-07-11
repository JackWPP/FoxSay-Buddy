/**
 * @file ui_wiki_screen.c
 * FoxSay 全息球体知识库 (Spherical Wiki / Hierarchy Slider)
 *
 * 布局依据 ui_wireframe_spec.md:
 *  - 顶部 "Wiki Map" 标题
 *  - 父节点 (小, 暗, 上方)
 *  - 焦点节点 (大, 橙色发光, 居中)
 *  - 子节点 (小, 暗, 下方)
 *  - 上下滑动旋转, 左右滑动进出层级
 */
#include "ui_theme.h"

/**********************
 *  STATIC VARIABLES
 **********************/
static lv_obj_t * wiki_screen = NULL;
static lv_obj_t * lbl_parent = NULL;
static lv_obj_t * lbl_focus = NULL;
static lv_obj_t * lbl_child = NULL;
static lv_obj_t * lbl_sibling_l = NULL;
static lv_obj_t * lbl_sibling_r = NULL;

/* 模拟知识库大纲 */
static const char * nodes[][5] = {
    /* parent, focus, child, sibling_l, sibling_r */
    {"数学",    "微积分", "极限",   "代数",   "几何"},
    {"分析",    "极限",   "连续性", "序列",   "级数"},
    {"代数",    "矩阵",   "特征值", "向量",   "行列式"},
    {"物理",    "力学",   "运动学", "热学",   "电磁学"},
};
static int node_count = 4;
static int current_node = 0;

/**********************
 *  STATIC FUNCTIONS
 **********************/

static void update_wiki_content(void)
{
    lv_label_set_text(lbl_parent, nodes[current_node][0]);
    lv_label_set_text(lbl_focus, nodes[current_node][1]);
    lv_label_set_text(lbl_child, nodes[current_node][2]);
    lv_label_set_text(lbl_sibling_l, nodes[current_node][3]);
    lv_label_set_text(lbl_sibling_r, nodes[current_node][4]);
}

/** 上下滑动: 切换节点 */
static void on_gesture(lv_event_t * e)
{
    lv_indev_t * indev = lv_indev_active();
    lv_dir_t dir = lv_indev_get_gesture_dir(indev);

    if(dir == LV_DIR_TOP) {
        current_node = (current_node + 1) % node_count;
        update_wiki_content();
    }
    else if(dir == LV_DIR_BOTTOM) {
        current_node = (current_node - 1 + node_count) % node_count;
        update_wiki_content();
    }
    else if(dir == LV_DIR_RIGHT) {
        /* 右滑: 进入下一层 (简化: 跳到子节点) */
        /* 实际应实现层级导航, 这里仅演示切换 */
        current_node = (current_node + 1) % node_count;
        update_wiki_content();
    }
    else if(dir == LV_DIR_LEFT) {
        /* 左滑: 返回时钟主屏 */
        extern void ui_show_clock_screen(void);
        ui_show_clock_screen();
    }
}

/** 创建节点标签 */
static lv_obj_t * create_node_label(lv_obj_t * parent, int y, int font_size,
                                     lv_color_t color, lv_opa_t opa)
{
    lv_obj_t * lbl = lv_label_create(parent);
    lv_obj_set_style_text_color(lbl, color, 0);
    lv_obj_set_style_text_opa(lbl, opa, 0);
    lv_obj_align(lbl, LV_ALIGN_TOP_MID, 0, y);

    if(font_size >= 24) {
        lv_obj_set_style_text_font(lbl, &lv_font_montserrat_24, 0);
    } else {
        lv_obj_set_style_text_font(lbl, &fox_cn_14, 0);
    }

    return lbl;
}

/** 焦点节点发光边框 */
static void create_focus_glow(lv_obj_t * parent)
{
    lv_obj_t * glow = lv_obj_create(parent);
    lv_obj_set_size(glow, 170, 42);
    lv_obj_align(glow, LV_ALIGN_TOP_MID, 0, 88);
    lv_obj_set_style_bg_color(glow, lv_color_hex(0x000000), 0);
    lv_obj_set_style_bg_opa(glow, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(glow, 2, 0);
    lv_obj_set_style_border_color(glow, FOX_COLOR_PRIMARY, 0);
    lv_obj_set_style_border_opa(glow, LV_OPA_60, 0);
    lv_obj_set_style_radius(glow, 8, 0);
    lv_obj_set_style_shadow_width(glow, 15, 0);
    lv_obj_set_style_shadow_color(glow, FOX_COLOR_PRIMARY, 0);
    lv_obj_set_style_shadow_opa(glow, LV_OPA_30, 0);
    lv_obj_clear_flag(glow, LV_OBJ_FLAG_SCROLLABLE);
}

/**********************
 *  GLOBAL FUNCTIONS
 **********************/

lv_obj_t * ui_wiki_screen_create(void)
{
    if(wiki_screen) {
        lv_obj_delete(wiki_screen);
    }

    wiki_screen = lv_obj_create(lv_screen_active());
    lv_obj_set_size(wiki_screen, FOX_SCREEN_W, FOX_SCREEN_H);
    lv_obj_set_style_bg_color(wiki_screen, FOX_COLOR_BG, 0);
    lv_obj_set_style_bg_opa(wiki_screen, LV_OPA_COVER, 0);
    lv_obj_set_style_border_width(wiki_screen, 0, 0);
    lv_obj_set_style_pad_all(wiki_screen, 0, 0);
    lv_obj_set_style_radius(wiki_screen, 0, 0);
    lv_obj_clear_flag(wiki_screen, LV_OBJ_FLAG_SCROLLABLE);

    /* 手势 */
    lv_obj_add_flag(wiki_screen, LV_OBJ_FLAG_GESTURE_BUBBLE);
    lv_obj_add_event_cb(wiki_screen, on_gesture, LV_EVENT_GESTURE, NULL);

    /* 标题 */
    lv_obj_t * title = lv_label_create(wiki_screen);
    lv_label_set_text(title, "Wiki Map");
    lv_obj_set_style_text_color(title, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(title, &lv_font_montserrat_12, 0);
    lv_obj_align(title, LV_ALIGN_TOP_LEFT, 15, 12);

    /* 连接线 (简易竖线) */
    lv_obj_t * line = lv_obj_create(wiki_screen);
    lv_obj_set_size(line, 2, 130);
    lv_obj_align(line, LV_ALIGN_TOP_MID, 0, 50);
    lv_obj_set_style_bg_color(line, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_bg_opa(line, LV_OPA_20, 0);
    lv_obj_set_style_border_width(line, 0, 0);
    lv_obj_set_style_radius(line, 0, 0);
    lv_obj_clear_flag(line, LV_OBJ_FLAG_SCROLLABLE);

    /* 父节点 */
    lbl_parent = create_node_label(wiki_screen, 50, 14, FOX_COLOR_TEXT, LV_OPA_40);

    /* 焦点节点 (大字, 橙色) */
    create_focus_glow(wiki_screen);
    lbl_focus = create_node_label(wiki_screen, 93, 14, FOX_COLOR_PRIMARY, LV_OPA_COVER);
    lv_obj_set_style_text_font(lbl_focus, &fox_cn_24, 0);

    /* 子节点 */
    lbl_child = create_node_label(wiki_screen, 155, 14, FOX_COLOR_TEXT, LV_OPA_40);

    /* 左右兄弟节点 */
    lbl_sibling_l = lv_label_create(wiki_screen);
    lv_obj_set_style_text_color(lbl_sibling_l, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(lbl_sibling_l, &fox_cn_14, 0);
    lv_obj_set_style_text_opa(lbl_sibling_l, LV_OPA_30, 0);
    lv_obj_align(lbl_sibling_l, LV_ALIGN_LEFT_MID, 20, 10);

    lbl_sibling_r = lv_label_create(wiki_screen);
    lv_obj_set_style_text_color(lbl_sibling_r, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(lbl_sibling_r, &fox_cn_14, 0);
    lv_obj_set_style_text_opa(lbl_sibling_r, LV_OPA_30, 0);
    lv_obj_align(lbl_sibling_r, LV_ALIGN_RIGHT_MID, -20, 10);

    /* 手势提示 */
    lv_obj_t * hint = lv_label_create(wiki_screen);
    lv_label_set_text(hint, "上下滑旋转 / 左右滑进出层级");
    lv_obj_set_style_text_color(hint, FOX_COLOR_MUTED, 0);
    lv_obj_set_style_text_font(hint, &fox_cn_14, 0);
    lv_obj_set_style_text_opa(hint, LV_OPA_30, 0);
    lv_obj_align(hint, LV_ALIGN_BOTTOM_MID, 0, -10);

    current_node = 0;
    update_wiki_content();

    return wiki_screen;
}
