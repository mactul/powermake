#include "my_lib.h"


int main()
{
    if(add_numbers(6, 7) != 13)
    {
        return 1;
    }

    #ifndef DISABLE_GNU_AS
    if(multiply(6, 7) != 42)
    {
        return 1;
    }
    #endif

    if(_subtract(12, 7) != 5)
    {
        return 1;
    }
    return 0;
}