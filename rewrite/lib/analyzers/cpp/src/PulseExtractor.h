#pragma once
#include "Logger.h"
#include "boost/date_time/gregorian/gregorian.hpp"
#include "boost/date_time/posix_time/posix_time.hpp"
#include <cstdint>
#include <fstream>
#include <map>
#include <memory>

//using edgeMap = std::map<std::string, std::vector<std::int64_t>>;

struct Edge {
    std::int64_t ch0 = 0;
    std::int64_t ch1 = 0;
    std::int64_t ch2 = 0;
    std::int64_t ch3 = 0;
    Edge() {};
    Edge(std::int64_t ch0,
        std::int64_t ch1,
        std::int64_t ch2,
        std::int64_t ch3)
        : ch0(ch0)
        , ch1(ch1)
        , ch2(ch2)
        , ch3(ch3)
    {
    }

    std::int64_t operator[](int i)
    {
        switch (i) {
        case 0:
            return ch0;
        case 1:
            return ch1;
        case 2:
            return ch2;
        case 3:
            return ch3;
        default:
            return ch0;
        }
    }
};

struct Pulse {
    double fe = 0.0;
    double re = 0.0;
};

struct EdgeMap {
    std::vector<Pulse> ch0;
    std::vector<Pulse> ch1;
    std::vector<Pulse> ch2;
    std::vector<Pulse> ch3;

    EdgeMap() {};

    EdgeMap(std::vector<Pulse> ch0,
        std::vector<Pulse> ch1,
        std::vector<Pulse> ch2,
        std::vector<Pulse> ch3)
        : ch0(ch0)
        , ch1(ch1)
        , ch2(ch2)
        , ch3(ch3)
    {
    }

    std::vector<Pulse>& operator[](size_t i)
    {
        switch (i) {
        case 0:
            return ch0;
        case 1:
            return ch1;
        case 2:
            return ch2;
        case 3:
            return ch3;
        default:
            return ch0;
        }
    }
};

struct Exctraction {
    std::int64_t last_trigger_time;
    EdgeMap edgeMap;
};

class PulseExtractor {
    /*    
  Get the pulses out of a daq line. Speed is important here.
    If a pulse file is given, all the extracted pulses will be
    written into it.

    :param logger: logger object
    :type logger: logging.Logger
    :param filename: filename of the pulse file
    :type filename: str
    */
    // for the pulses
    // 8 bits give a hex number
    // but only the first 5 bits are used for the pulses time,
    // the fifth bit flags if the pulse is considered valid
    // the seventh bit should be the trigger flag...
    const std::uint32_t BIT0_4 = 31;
    const std::uint32_t BIT5 = 1 << 5;
    const std::uint32_t BIT7 = 1 << 7;

    // For DAQ status
    const std::uint32_t BIT0 = 1; // 1 PPS interrupt pending
    const std::uint32_t BIT1 = 1 << 1; // Trigger interrupt pending
    const std::uint32_t BIT2 = 1 << 2; // GPS data possible corrupted
    const std::uint32_t BIT3 = 1 << 3; // Current or last 1PPS rate not within range

    // tick size of tmc internal clock
    // documentation says 0.75, measurement says 1.25
    // TODO: find out if tmc is coupled to cpld!
    const double TMC_TICK = 1.25; // nsec
    // MAX_TRIGGER_WINDOW = 60.0  // nsec
    const double MAX_TRIGGER_WINDOW = 9960.0; // nsec for mudecay!
    const double DEFAULT_FREQUENCY = 25.0e6;

    Log logger = Log();

    std::string pulse_file;
    std::shared_ptr<std::ofstream> pulse_stream;

    bool _write_pulses = false;

    //Start time and duration
    boost::posix_time::ptime start_time = boost::posix_time::second_clock::local_time();
    boost::posix_time::ptime measurement_duration = boost::posix_time::second_clock::local_time();

    EdgeMap re;
    EdgeMap fe;
    EdgeMap last_re;
    EdgeMap last_fe;

    // ini will be False if we have seen the first trigger
    // store items if Events are longer than one line
    bool ini = true;
    std::int64_t last_one_ps = 0;
    std::int64_t last_trigger_time = 0;
    std::int64_t trigger_count = 0;
    std::int64_t last_time = 0;

    // store the actual value of the trigger counter
    // to correct trigger counter rollover
    std::int64_t last_trigger_count = 0;

    // TODO find a generic way to account for the fact that the default
    // cna be either 25 or 41 MHz variables for DAQ frequency calculation
    std::int64_t last_frequency_poll_time = 0;
    std::int64_t last_frequency_poll_triggers = 0;
    double calculated_frequency = DEFAULT_FREQUENCY;
    std::int64_t last_one_pps_poll = 0;
    std::int64_t passed_one_pps = 0;
    std::int64_t prev_last_one_pps = 0;

public:
    PulseExtractor(std::string pulse_file);
    void write_pulses(bool write_pulses);
    void finish();
    void _calculate_edges(std::vector<std::string> line, int counter_diff);
    EdgeMap _order_and_clean_pulses();
    double _get_evt_time(std::string time, int correction, std::int64_t trigger_count, std::int64_t one_pps);
    Exctraction extract(std::string line);
    boost::posix_time::ptime now();
    template <typename T2, typename T1>
    inline T2 lexical_cast(const T1& in);
    // void getTime()
    // {
    //     logger.log(to_simple_string(timeLocal).c_str());
    // }
};