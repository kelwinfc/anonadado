#include "anonadado.hpp"

using namespace anonadado;
using namespace std;

instance::instance()
{
    this->d = 0;
}

instance::instance(domain* d)
{
    this->d = d;
}

void instance::read(string filename)
{
    
}