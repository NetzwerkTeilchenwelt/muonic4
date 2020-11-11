#include <boost/python.hpp>
#include "Logger.h"


char const *greet()
{
  return "Hello World!";
}

BOOST_PYTHON_MODULE(extractor)
{
  using namespace boost::python;
  def("greet", greet);

  class_<Log>("Log")
    .def("log", &Log::log);
}
