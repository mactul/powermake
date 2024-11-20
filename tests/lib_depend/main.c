#include <stdio.h>
#include "my_lib.h"


int main()
{
    if(add_numbers(6, 7) != 13)
    {
        fputs("6 + 7 != 13\n", stderr);
        return 1;
    }

    #ifndef DISABLE_GNU_AS
    if(_multiply(6, 7) != 42)
    {
        fputs("6 * 7 != 42\n", stderr);
        return 1;
    }
    #endif

    if(_subtract(12, 7) != 5)
    {
        fputs("12 - 7 != 5\n", stderr);
        return 1;
    }
    return 0;
}