#include "PulseExtractor.h"
#include <algorithm>
#include <boost/lexical_cast.hpp>
#include <filesystem>
#include <iostream>
#include <sstream>

PulseExtractor::PulseExtractor(std::string pulse_file)
    : pulse_file(pulse_file)
{
}

/*
Enables or disables writing pulses to file.

:param write_pulses: write pulses to file
:type write_pulses: bool
:return: None
*/
void PulseExtractor::write_pulses(bool write_pulses)
{
    if (_write_pulses == write_pulses) {
        return;
    }

    if (pulse_file != "") {
        if (write_pulses) {
            start_time = now();
            pulse_stream = std::make_shared<std::ofstream>(pulse_file, std::ofstream::out | std::ofstream::app);
            logger.debug("Starting to write pulses to " + pulse_file);
        } else {
            auto stop_time = now();
            measurement_duration += stop_time - start_time;
            pulse_stream->close();
        }
        _write_pulses = write_pulses;
    } else {
        _write_pulses = false;
    }
}
/*
Cleanup, close and rename pulse file

:returns: None
*/
void PulseExtractor::finish()
{
    if (_write_pulses) {
        auto stop_time = now();

        // add duration
        measurement_duration += stop_time - start_time;
        pulse_stream->close();
    }

    // only rename if file actualle exists
    /*auto path = std::filesystem::path(pulse_file);
    if (std::filesystem::exists(path)) {
        logger.info("The pulse extraction measurement was active for " + measurement_duration);
        auto path
    }*/
}

/*
get the leading and falling edges of the pulses
Use counter diff for getting pulse times in subsequent 
lines of the trigger flag

:param line: DQ message split on whitespaces
:type line: list
:param counter_diff: counter difference
:type counter_diff: int
:return: None
*/
void PulseExtractor::_calculate_edges(std::vector<std::string> line, int counter_diff = 0)
{
    Edge rising_edges(lexical_cast<std::int64_t>(line[1]),
        lexical_cast<std::int64_t>(line[3]),
        lexical_cast<std::int64_t>(line[5]),
        lexical_cast<std::int64_t>(line[7]));

    Edge falling_edges(lexical_cast<std::int64_t>(line[2]),
        lexical_cast<std::int64_t>(line[4]),
        lexical_cast<std::int64_t>(line[6]),
        lexical_cast<std::int64_t>(line[8]));

    for (size_t ch = 0; ch <= 3; ch++) {
        auto _re = rising_edges[ch];
        auto _fe = rising_edges[ch];

        if (_re & BIT5) {
            re[ch].push_back(counter_diff + (_re & BIT0_4) * TMC_TICK));
        }

        if (_fe & BIT5) {
            fe[ch].push_back(counter_diff + (_fe & BIT0_4) * TMC_TICK));
        }
    }
}

/*
Remove pulses which have a 
leading edge later in time than a 
falling edge and do a bit of sorting
Remove also single leading or falling edges
NEW: We add virtual falling edges!

:returns: dict of lists
*/
EdgeMap PulseExtractor::_order_and_clean_pulses()
{
    EdgeMap pulses;
    for (size_t ch = 0; ch <= 3; ch++) {
        for (size_t i = 0; i < last_re[ch].size(); i++) {
            auto _re = last_re[ch][i].re;
            auto fe = MAX_TRIGGER_WINDOW;
            try {
                fe = last_fe[ch].at(i).fe;
                if (fe < _re) {
                    fe = MAX_TRIGGER_WINDOW;
                }
            } catch (std::out_of_range const& exc) {
            }
            pulses[ch].emplace_back({ fe, re });
        }
        pulses[ch] = std::sort(pulses[ch].begin(), pulses[ch].end(), [](Pulse& a, Pulse& b) { return a.re < b.re; })
    }
    return pulses;
}
double PulseExtractor::_get_evt_time(std::string time, int correction, std::int64_t trigger_count, std::int64_t one_pps) { }
Exctraction PulseExtractor::extract(std::string line) { }

boost::posix_time::ptime PulseExtractor::now()
{
    return boost::posix_time::second_clock::local_time();
}

template <typename T2, typename T1>
inline T2 PulseExtractor::lexical_cast(const T1& in)
{
    T2 out;
    std::stringstream ss;
    ss << std::hex << in;
    ss >> out;
    return out;
}