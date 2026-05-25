#include <iostream>

extern "C" {
    void sleep_ms(unsigned int ms);
}

int main(int argc, char* argv[])
{
    for(int i = 1; i < argc; i++)
    {
        std::cout << argv[i] << std::endl;
    }
    std::cout << "Hello" << std::endl;
    sleep_ms(10);
    std::cout << "World" << std::endl;

    return 0;
}
