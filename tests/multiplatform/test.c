#ifdef POWERMAKE_WIN32
    #include <windows.h>
#else
    #include <unistd.h>
#endif


void sleep_ms(unsigned int ms)
{
    #ifdef POWERMAKE_WIN32
        Sleep(ms);
    #else
        usleep(1000 * ms);
    #endif
}
