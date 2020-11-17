#include "Logger.h"
#include "PulseExtractor.h"
#include <boost/python.hpp>

char const* greet()
{
    return "Hello World!";
}

BOOST_PYTHON_MODULE(extractor)
{
    using namespace boost::python;
    def("greet", greet);
    void (Log::*debug)(const char*) = &Log::debug;

    class_<Log>("Log")
        .def("log", &Log::info)
        .def("debug", debug);

    class_<PulseExtractor>("PulseExtractor", init<std::string>())
        .def("write_pulses", &PulseExtractor::write_pulses)
        .def("finish", &PulseExtractor::finish)
        .def("_calculate_edges", &PulseExtractor::_calculate_edges)
        .def("_order_and_clean_pulses", &PulseExtractor::_order_and_clean_pulses)
        .def("_get_evt_time", &PulseExtractor::_get_evt_time)
        .def("extract", &PulseExtractor::extract);
}
