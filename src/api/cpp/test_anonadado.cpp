#include "test_anonadado.hpp"

int main(int argc, char* argv[])
{
    anonadado::instance i;
    i.read(argv[1]);
    cout << "Bye!\n";
    
    return 0;
}
