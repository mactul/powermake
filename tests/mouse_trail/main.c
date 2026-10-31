#define SDL_MAIN_USE_CALLBACKS
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>

#define MAX_POINTS 256
#define FADE_MS    500

typedef struct
{
    float  x;
    float  y;
    Uint64 t; // 0 = unused slot
} Point;

static SDL_Window*   window   = NULL;
static SDL_Renderer* renderer = NULL;
static Point         points[MAX_POINTS];
static int           head     = 0;

SDL_AppResult SDL_AppInit(void** appstate, int argc, char** argv)
{
    if(!SDL_CreateWindowAndRenderer("trail", 800, 600, SDL_WINDOW_RESIZABLE, &window, &renderer))
    {
        return SDL_APP_FAILURE;
    }
    if(!SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND))
    {
        return SDL_APP_FAILURE;
    }
    return SDL_APP_CONTINUE;
}

SDL_AppResult SDL_AppEvent(void* appstate, SDL_Event* event)
{
    if(event->type == SDL_EVENT_QUIT)
    {
        return SDL_APP_SUCCESS;
    }
    if(event->type == SDL_EVENT_MOUSE_MOTION)
    {
        points[head].x = event->motion.x;
        points[head].y = event->motion.y;
        points[head].t = SDL_GetTicks();
        head = (head + 1) % MAX_POINTS;
    }
    return SDL_APP_CONTINUE;
}

SDL_AppResult SDL_AppIterate(void* appstate)
{
    const Uint64 now = SDL_GetTicks();

    if(!SDL_SetRenderDrawColor(renderer, 0, 5, 30, 255) || !SDL_RenderClear(renderer))
    {
        return SDL_APP_FAILURE;
    }

    for(int i = 0; i < MAX_POINTS; i++)
    {
        if(points[i].t == 0)
        {
            continue;
        }
        const Uint64 age = now - points[i].t;
        if(age >= FADE_MS)
        {
            continue;
        }
        const Uint8 alpha = (Uint8)(255 * (FADE_MS - age) / FADE_MS);
        const SDL_FRect rect = { points[i].x - 8, points[i].y - 8, 16, 16 };

        if(!SDL_SetRenderDrawColor(renderer, 255, 255, 255, alpha) || !SDL_RenderFillRect(renderer, &rect))
        {
            return SDL_APP_FAILURE;
        }
    }

    if(!SDL_RenderPresent(renderer))
    {
        return SDL_APP_FAILURE;
    }
    return SDL_APP_CONTINUE;
}

void SDL_AppQuit(void* appstate, SDL_AppResult result)
{
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
}