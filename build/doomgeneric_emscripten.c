//
// doomgeneric platform backend for Emscripten / WebAssembly.
//
// Rendering, input and timing are bridged straight to JavaScript. No SDL,
// no pthreads, no SharedArrayBuffer: the game runs on the browser main
// thread, driven by emscripten_set_main_loop at 35 fps (DOOM's tic rate).
//

#include <string.h>

#include <emscripten.h>

#include "doomgeneric.h"
#include "doomkeys.h"

#define KEYQUEUE_SIZE 64

static unsigned short s_KeyQueue[KEYQUEUE_SIZE];
static unsigned int s_KeyQueueWriteIndex = 0;
static unsigned int s_KeyQueueReadIndex = 0;

// Called from the JavaScript key handlers with an already-translated DOOM
// key code (see doomkeys.h).
EMSCRIPTEN_KEEPALIVE
void DG_PushKeyEvent(int pressed, int doomKey)
{
    unsigned short keyData = ((pressed & 1) << 8) | (doomKey & 0xff);

    s_KeyQueue[s_KeyQueueWriteIndex] = keyData;
    s_KeyQueueWriteIndex = (s_KeyQueueWriteIndex + 1) % KEYQUEUE_SIZE;
}

int DG_GetKey(int* pressed, unsigned char* doomKey)
{
    if (s_KeyQueueReadIndex == s_KeyQueueWriteIndex)
    {
        return 0;
    }

    unsigned short keyData = s_KeyQueue[s_KeyQueueReadIndex];
    s_KeyQueueReadIndex = (s_KeyQueueReadIndex + 1) % KEYQUEUE_SIZE;

    *pressed = keyData >> 8;
    *doomKey = keyData & 0xff;

    return 1;
}

EM_JS(void, js_init, (int resx, int resy), {
    Module.dg_init(resx, resy);
});

EM_JS(void, js_draw_frame, (void* screenBuffer, int resx, int resy), {
    Module.dg_drawFrame(screenBuffer, resx, resy);
});

EM_JS(void, js_set_window_title, (const char* title), {
    Module.dg_setTitle(UTF8ToString(title));
});

void DG_Init()
{
    js_init(DOOMGENERIC_RESX, DOOMGENERIC_RESY);
}

void DG_DrawFrame()
{
    js_draw_frame(DG_ScreenBuffer, DOOMGENERIC_RESX, DOOMGENERIC_RESY);
}

void DG_SleepMs(uint32_t ms)
{
    // Intentionally empty: blocking the browser main thread is not
    // possible without SharedArrayBuffer. TryRunTics' wait loop exits on
    // its own once I_GetTime() advances.
    (void)ms;
}

uint32_t DG_GetTicksMs()
{
    return (uint32_t)emscripten_get_now();
}

void DG_SetWindowTitle(const char* title)
{
    js_set_window_title(title);
}

// main(void) on purpose: with main(argc, argv) clang renames the symbol
// to __main_argc_argv, which this emscripten version fails to link. The
// IWAD is always /doom1.wad, planted into MEMFS by the embedding page.
int main(void)
{
    static char* argv[] = { "doom", "-iwad", "/doom1.wad", NULL };

    doomgeneric_Create(3, argv);

    // 35 fps == DOOM's internal tic rate, so TryRunTics almost always has
    // a fresh tic available and never spins for long.
    emscripten_set_main_loop(doomgeneric_Tick, 35, 0);

    return 0;
}
