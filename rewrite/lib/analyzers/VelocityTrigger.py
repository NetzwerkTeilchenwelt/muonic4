class VelocityTrigger:
    """
    A velocity "trigger", so that czts can be defined

    :param logger: logger object
    :type logger: logging.Logger
    """

    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Velocity trigger initialized")

    def trigger(self, pulses, upper_channel=1, lower_channel=2):
        """
        Time difference will be calculated t(upper_channel) - t(lower_channel)

        :param pulses: detected pulses
        :type pulses: list
        :param upper_channel: index of the upper channel
        :type upper_channel: int
        :param lower_channel: index of the lower channel
        :type lower_channel: int
        :returns: float or None
        """
        # remember that index 0 is the trigger time
        upper_pulses = len(pulses[upper_channel])
        lower_pulses = len(pulses[lower_channel])

        print(f"upper Pulses[{upper_channel}]: {upper_pulses} -> {pulses[upper_channel]}, lower pulses[{lower_channel}]: {lower_pulses} -> {pulses[lower_channel]}")

        if upper_pulses and lower_pulses:
            if (len(pulses[upper_channel][0]) > 1 and
                    len(pulses[lower_channel][0]) > 1):
                pulse_width_upper = (pulses[upper_channel][0][1] -
                                     pulses[upper_channel][0][0])
                pulse_width_lower = (pulses[lower_channel][0][1] -
                                     pulses[lower_channel][0][0])

                # THIS is only for debugging !!! reenable in production
                # if (pulse_width_upper - pulse_width_lower < -15. or
                #         pulse_width_upper - pulse_width_lower > 45.):
                #     return None
            else:
                return None

            # always use rising edge since fe might be virtual
            return pulses[lower_channel][0][0] - pulses[upper_channel][0][0]
        return None
