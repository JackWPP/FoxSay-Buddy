/**
 * @file ui_screen_manager.c
 * FoxSay 屏幕导航管理器
 */
#include "ui_screens.h"

typedef enum {
    SCREEN_CLOCK = 0,
    SCREEN_FLASHCARD,
    SCREEN_WIKI,
    SCREEN_COUNT
} screen_id_t;

static screen_id_t current_screen = SCREEN_CLOCK;

void ui_show_clock_screen(void)
{
    current_screen = SCREEN_CLOCK;
    ui_clock_screen_create();
}

void ui_show_flashcard_screen(void)
{
    current_screen = SCREEN_FLASHCARD;
    ui_flashcard_screen_create();
}

void ui_show_wiki_screen(void)
{
    current_screen = SCREEN_WIKI;
    ui_wiki_screen_create();
}
