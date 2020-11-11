#include <boost/python.hpp>

char const * greet()
{
    return "Hello World!";
}

BOOST_PYTHON_MODULE(extractor)
{
    using namespace boost::python;
    def("greet", greet);
}
