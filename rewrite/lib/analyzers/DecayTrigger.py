class DecayTriggerThorough:
    """
    Trigger on a set of extracted pulses and look for decayed muons.

    We demand a second pulse in the same channel where the muon got stuck.
    Should operate for a 10mu sec trigger window.

    :param logger: logger object
    :type logger: logging.Logger
    """

    def __init__(self, logger):
        # 10 musec set at DAQ -> in ns since, TMC info is in nsec
        self.trigger_window = 10000
        self.logger = logger
        self.logger.info("Initializing decay trigger, setting " +
                         "trigger window to %i" % self.trigger_window)

    def trigger(self, trigger_pulses, single_channel=2, double_channel=3,
                veto_channel=4, min_decay_time=0,
                min_single_pulse_width=0, max_single_pulse_width=12000,
                min_double_pulse_width=0, max_double_pulse_width=12000):
        """
        Trigger on a certain combination of single and double pulses

        :param trigger_pulses: detected pulses
        :type trigger_pulses: list
        :param single_channel: channel index
        :type single_channel: int
        :param double_channel: channel index
        :type double_channel: int
        :param veto_channel: channel index
        :type veto_channel: int
        :param min_decay_time: minimum decay time
        :type min_decay_time: int
        :param min_single_pulse_width: minimum single pulse width
        :type min_single_pulse_width: int
        :param max_single_pulse_width: maximum single pulse width
        :type max_single_pulse_width: int
        :param min_double_pulse_width: minimum double pulse width
        :type min_double_pulse_width: int
        :param max_double_pulse_width: maximum double pulse width
        :type max_double_pulse_width: int
        :returns: int or None
        """

        #debug
        #decay_time = 10e-3
        ttp = trigger_pulses
        pulses1 = len(ttp[single_channel])  # single pulse
        pulses2 = len(ttp[double_channel])  # double pulse
        pulses3 = len(ttp[veto_channel])    # veto pulses

        # reject events with too few pulses in some setups good value
        # will be three (single pulse + double pulse required) and no hits
        # in the veto channel3 change this if only one channel is available
        if (pulses1 + pulses2 < 2) or pulses3:
            # reject event if it has to few pulses or veto pulses
            self.logger.debug(("Rejecting decay with single pulses %s, " +
                               "double pulses %s and veto pulses %s") %
                              (repr(pulses1), repr(pulses2), repr(pulses3)))

            return None

        # muon it might have entered the second channel then we do
        # not want to have more than one hit in the first.
        # again: use selfveto to adjust the behavior
        if single_channel == double_channel:
            if pulses2 >= 2 and pulses1 >= 2:
                # check if the width of the pulses is as required
                single_pulse_width = (ttp[single_channel][0][1] -
                                      ttp[single_channel][0][0])
                double_pulse_width = (ttp[double_channel][-1][1] -
                                      ttp[double_channel][-1][0])

                if ((min_single_pulse_width < single_pulse_width <
                        max_single_pulse_width) and
                        (min_double_pulse_width < double_pulse_width <
                         max_double_pulse_width)):
                    # subtract rising edges, falling edges might be virtual
                    decay_time = (ttp[double_channel][-1][0] -
                                  ttp[double_channel][0][0])
                else:
                    self.logger.debug('Rejected event.')

                    return None
            else:
                self.logger.debug('Rejected event.')

                return None
        else:
            if pulses2 >= 2 and pulses1 == 1:
                # check if the width of the pulses is as required
                single_pulse_width = (ttp[single_channel][0][1] -
                                      ttp[single_channel][0][0])
                double_pulse_width = (ttp[double_channel][-1][1] -
                                      ttp[double_channel][-1][0])

                if ((min_single_pulse_width < single_pulse_width <
                        max_single_pulse_width) and
                        (min_double_pulse_width < double_pulse_width <
                         max_double_pulse_width)):
                    # subtract rising edges, falling edges might be virtual
                    decay_time = (ttp[double_channel][-1][0] -
                                  ttp[double_channel][0][0])
                else:
                    self.logger.debug('Rejected event.')

                    return None
            else:
                self.logger.debug('Rejected event.')

                return None

        # perform sanity checks
        # there is an artifact at the end of the trigger window, so -1000
        if ((decay_time > min_decay_time) and
                (decay_time < self.trigger_window - 1000)):
            self.logger.debug("Decay with decay time %d found " % decay_time)
            return decay_time

        self.logger.debug(("Rejecting decay with single pulses %s, " +
                           "double pulses %s and veto pulses %s") %
                          (repr(pulses1), repr(pulses2), repr(pulses3)))
        return None