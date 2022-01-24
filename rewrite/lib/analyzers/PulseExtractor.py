"""
Get the absolute timing of the pulses by use of the gps time
Calculate also a non hex representation of leading and falling
edges of the pulses.
"""
import datetime
import os


from ..utils.WrappedFile import WrappedFile
from ..utils.Time import getLocalTime

# for the pulses
# 8 bits give a hex number
# but only the first 5 bits are used for the pulses time,
# the fifth bit flags if the pulse is considered valid
# the seventh bit should be the trigger flag...

BIT0_4 = 31
BIT5 = 1 << 5
BIT7 = 1 << 7

# For DAQ status
BIT0 = 1       # 1 PPS interrupt pending
BIT1 = 1 << 1  # Trigger interrupt pending
BIT2 = 1 << 2  # GPS data possible corrupted
BIT3 = 1 << 3  # Current or last 1PPS rate not within range

# tick size of tmc internal clock
# documentation says 0.75, measurement says 1.25
# TODO: find out if tmc is coupled to cpld!
TMC_TICK = 1.25  # nsec
# MAX_TRIGGER_WINDOW = 60.0  # nsec
MAX_TRIGGER_WINDOW = 9960.0  # nsec for mudecay!
DEFAULT_FREQUENCY = 25.0e6


class PulseExtractor:
    """
    Get the pulses out of a daq line. Speed is important here.
    If a pulse file is given, all the extracted pulses will be
    written into it.

    :param logger: logger object
    :type logger: logging.Logger
    :param filename: filename of the pulse file
    :type filename: str
    """

    def __init__(self, logger, filename):
        self.logger = logger
        self.pulse_file = WrappedFile(filename)
        self._write_pulses = False

        # start time and duration
        self.start_time = getLocalTime()
        self.measurement_duration = datetime.timedelta()

        # TODO change to dictionaries, they might be faster
        self.re = {"ch0": [], "ch1": [], "ch2": [], "ch3": []}
        self.fe = {"ch0": [], "ch1": [], "ch2": [], "ch3": []}
        self.last_re = {"ch0": [], "ch1": [], "ch2": [], "ch3": []}
        self.last_fe = {"ch0": [], "ch1": [], "ch2": [], "ch3": []}

        # ini will be False if we have seen the first trigger
        # store items if Events are longer than one line
        self.ini = True
        self.last_one_pps = 0
        self.last_trigger_time = 0
        self.trigger_count = 0
        self.last_time = 0

        # store the actual value of the trigger counter
        # to correct trigger counter rollover
        self.last_trigger_count = 0

        # TODO find a generic way to account for the fact that the default
        # cna be either 25 or 41 MHz variables for DAQ frequency calculation
        self.last_frequency_poll_time = 0
        self.last_frequency_poll_triggers = 0
        self.calculated_frequency = DEFAULT_FREQUENCY
        self.last_one_pps_poll = 0
        self.passed_one_pps = 0
        self.prev_last_one_pps = 0

    def write_pulses(self, write_pulses):
        """
        Enables or disables writing pulses to file.

        :param write_pulses: write pulses to file
        :type write_pulses: bool
        :return: None
        """
        if self._write_pulses == write_pulses:
            return

        if self.pulse_file is not None:
            if write_pulses:
                self.start_time = getLocalTime()
                self.pulse_file.open("a")
                self.logger.debug("Starting to write pulses to %s" %
                                  repr(self.pulse_file))
            else:
                stop_time = getLocalTime()

                # add duration
                self.measurement_duration += stop_time - self.start_time
                self.pulse_file.close()
            self._write_pulses = write_pulses
        else:
            self._write_pulses = False

    def finish(self):
        """
        Cleanup, close and rename pulse file

        :returns: None
        """
        if self._write_pulses:
            stop_time = getLocalTime()

            # add duration
            self.measurement_duration += stop_time - self.start_time
            self.pulse_file.close()

        # only rename if file actually exists
        if os.path.exists(self.pulse_file.get_filename()):
            try:
                self.logger.info(("The pulse extraction measurement was " +
                                  "active for %f hours") %
                                 get_hours_from_duration(
                    self.measurement_duration))
                rename_muonic_file(self.measurement_duration,
                                   self.pulse_file.get_filename())
            except (OSError, IOError):
                pass

    def _calculate_edges(self, line, counter_diff=0):
        """
        get the leading and falling edges of the pulses
        Use counter diff for getting pulse times in subsequent
        lines of the trigger flag

        :param line: DQ message split on whitespaces
        :type line: list
        :param counter_diff: counter difference
        :type counter_diff: int
        :return: None
        """

        rising_edges = {
            "ch0": int(line[1], 16), "ch1": int(line[3], 16),
            "ch2": int(line[5], 16), "ch3": int(line[7], 16)
        }
        falling_edges = {
            "ch0": int(line[2], 16), "ch1": int(line[4], 16),
            "ch2": int(line[6], 16), "ch3": int(line[8], 16)
        }

        for ch in ["ch0", "ch1", "ch2", "ch3"]:
            re = rising_edges[ch]
            fe = falling_edges[ch]

            if re & BIT5:
                self.re[ch].append(counter_diff + (re & BIT0_4) * TMC_TICK)
            if fe & BIT5:
                self.fe[ch].append(counter_diff + (fe & BIT0_4) * TMC_TICK)

    def _order_and_clean_pulses(self):
        """
        Remove pulses which have a
        leading edge later in time than a
        falling edge and do a bit of sorting
        Remove also single leading or falling edges
        NEW: We add virtual falling edges!

        :returns: dict of lists
        """
        pulses = {"ch0": [], "ch1": [], "ch2": [], "ch3": []}

        for ch in ["ch0", "ch1", "ch2", "ch3"]:
            for index, re in enumerate(self.last_re[ch]):
                # add the virtual falling edge if necessary
                try:
                    fe = self.last_fe[ch][index]
                    if fe < re:
                        fe = MAX_TRIGGER_WINDOW
                except IndexError:
                    fe = MAX_TRIGGER_WINDOW

                pulses[ch].append((re, fe))

            pulses[ch] = sorted(pulses[ch])

            # self.pulses[ch] = [(re,fe) for re,fe in self.last_re[ch],
            #                    self.last_fe[ch])
            # for i in self.pulses[ch]:
            #     if not i[0] < i[1]:
            #         #self.chan0.remove(i)
            #         self.pulses[ch] = (i[0],MAX_TRIGGER_WINDOW)
        return pulses

    def _get_evt_time(self, time, correction, trigger_count, one_pps):
        """
        Get the absolute event time in seconds since day start
        If gps is not available, only relative event time based on counts
        is returned

        :param time: event time
        :param correction:
        :param trigger_count:
        :param one_pps:
        :returns: float
        """
        time_fields = time.split(".")
        t = time_fields[0]

        secs_since_day_start = (int(t[0:2]) * 3600 +
                                int(t[2:4]) * 60 + int(t[4:6]))

        # FIXME: Why time_fields[1] / 1000?
        gps_time = float(secs_since_day_start + int(time_fields[1]) / 1000.0 +
                         int(correction) / 1000.0)

        line_time = gps_time + float((trigger_count - one_pps) /
                                     self.calculated_frequency)
        return line_time

    def extract(self, line):
        """
        Analyze subsequent lines (one per call)
        and check if pulses are related to triggers
        For each new trigger,
        return the set of pulses which belong to that trigger,
        otherwise return None

        :param line: DAQ message
        :type line: str
        :returns: tuple
        """
        line = line.split()
        if len(line) < 10:
            return
        one_pps = int(line[9], 16)
        trigger_count = int(line[0], 16)
        time = line[10]

        # correct for trigger count rollover
        if trigger_count < self.last_trigger_count:
            trigger_count += int(0xFFFFFFFF)  # counter offset

        self.trigger_count = trigger_count

        if one_pps != self.last_one_pps:
            self.passed_one_pps += 1
            # poll every x lines for the frequency
            # check for one_pps counter rollover
            if one_pps < self.last_one_pps:
                one_pps += int(0xFFFFFFFF)

            # calculate the frequency every x one_pps
            if not self.passed_one_pps % 5:
                self.calculated_frequency = ((one_pps - self.last_one_pps_poll) /
                                             float(self.passed_one_pps))
                self.passed_one_pps = 0
                self.last_one_pps_poll = one_pps

                # check if calculated_frequency is sane,
                # assuming the daq frequency is somewhat stable
                if not (0.5 * self.calculated_frequency <
                        DEFAULT_FREQUENCY < 1.5 * self.calculated_frequency):
                    self.calculated_frequency = DEFAULT_FREQUENCY

            if time == self.last_time:
                # correcting for delayed one_pps switch
                line_time = self._get_evt_time(line[10], line[15],
                                               trigger_count,
                                               self.last_one_pps)
            else:
                line_time = self._get_evt_time(line[10], line[15],
                                               trigger_count, one_pps)
        else:
            line_time = self._get_evt_time(line[10], line[15],
                                           trigger_count, one_pps)

        # storing the last two one_pps switches
        self.prev_last_one_pps = self.last_one_pps
        self.last_one_pps = one_pps

        self.last_time = time

        if int(line[1], 16) & BIT7:  # a trigger flag!
            self.ini = False

            # a new trigger! we have to evaluate the
            # last one and get the new pulses
            self.last_re = self.re
            self.last_fe = self.fe

            pulses = self._order_and_clean_pulses()
            # utcTime = getLocalTime()

            # from_zone = tz.tzutc()
            # to_zone = tz.tzlocal()
            # utc = getLocalTime()

            # utc = utc.replace(tzinfo=from_zone)



            extracted_pulses = ( self.last_trigger_time, pulses["ch0"],
                                pulses["ch1"], pulses["ch2"], pulses["ch3"], str(getLocalTime()))

            if self._write_pulses:
                self.pulse_file.write(repr(extracted_pulses) + '\n')

            # as the pulses for the last event are done,
            # reinitialize data structures
            # for the next event
            self.last_trigger_time = line_time
            self.re = {"ch0": [], "ch1": [], "ch2": [], "ch3": []}
            self.fe = {"ch0": [], "ch1": [], "ch2": [], "ch3": []}

            # calculate edges of the new pulses
            self._calculate_edges(line)
            self.last_trigger_count = trigger_count

            return extracted_pulses
        else:
            # we do have a previous trigger and are now
            # adding more pulses to the event
            if self.ini:
                self.last_one_pps = int(line[9], 16)
            else:
                counter_diff = (self.trigger_count - self.last_trigger_count)
                # print(counter_diff, counter_diff > int(0xffffffff))
                # FIXME: is this correct?
                if counter_diff > int(0xffffffff):
                    counter_diff -= int(0xffffffff)

                counter_diff /= self.calculated_frequency

                self._calculate_edges(line, counter_diff=counter_diff * 1e9)

        # end of if trigger flag
        self.last_trigger_count = trigger_count
