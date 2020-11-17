#pragma once
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>

#include <memory>
#include <string>
#include <vector>

class Log {
    std::shared_ptr<spdlog::logger> logger;
    std::shared_ptr<spdlog::sink_ptr> sink;

public:
    Log()
    {
        std::vector<spdlog::sink_ptr> logSinks;
        logSinks.emplace_back(std::make_shared<spdlog::sinks::stdout_color_sink_mt>());
        logSinks[0]->set_pattern("%^[%T] %n: %v%$");

        logger = std::make_shared<spdlog::logger>("console", begin(logSinks), end(logSinks));
        spdlog::register_logger(logger);
        logger->set_level(spdlog::level::trace);
        //err_logger = spdlog::stderr_color_mt("stderr");
    }

    void info(const char* msg)
    {
        spdlog::get("console")->info(msg);
    }

    void debug(const char* msg)
    {
        spdlog::get("console")->debug(msg);
    }

    void debug(std::string msg)
    {
        debug(msg.c_str());
    }
};