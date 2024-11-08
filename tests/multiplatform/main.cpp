#include <iostream>

extern "C" {
    void sleep_ms(unsigned int ms);
}

int main()
{
    std::cout << "Hello" << std::endl;
    sleep_ms(10);
    std::cout << "World" << std::endl;

    return 0;
}
