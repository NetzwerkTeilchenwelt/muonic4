#!/usr/bin/env python3
"""
Script for creating a histogram of the time difference between two triggers
Usage python plot_trigger_time_differences.py PULSEFILE
"""

import sys

import matplotlib.pylab as p
import numpy as n


def plot_trigger_timmdiff():
    f = open(sys.argv[1])

    triggers = []
    ini = True
    iniini = True
    last_trigger = 0

    for line in f.readlines():
        if iniini:
            iniini = False
            continue
        try:
            if ini:
                last_line = line.split()
                last_trigger = last_line[0].split('(')[1]
                last_trigger = last_trigger.split(',')[0]
                ini = False
                continue

            this_line = line.split()
            this_trigger = this_line[0].split('(')[1]
            this_trigger = this_trigger.split(',')[0]

            difference = (float(this_trigger) -
                          float(last_trigger)) / 1000000

            print(difference)

            triggers.append(difference)
            last_trigger = this_trigger
        except:
            pass

    xmax = max(triggers)
    #pulsebins = n.linspace(0, xmax, int(xmax) + 1)

    pulsebins = n.linspace(0, xmax, len(triggers)//5)
    hist0 = n.histogram(n.array(triggers), bins=pulsebins)

    baredges0 = n.linspace(0, hist0[1][-1], len(hist0[0]))
    p.ylim(ymax=1.2 * max(hist0[0]))
    # pulsebins = hist0[1]
    p.bar(baredges0, hist0[0], width=pulsebins[1] - pulsebins[0],
          color='b', label='triggers')
    p.grid()
    p.legend()
    p.xlabel('Triggerdistance')
    p.ylabel('Events')
    p.show()


if __name__ == "__main__":
    plot_trigger_timmdiff()
