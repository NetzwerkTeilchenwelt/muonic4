#! /usr/bin/env python3
"""
Calculating the fraction of upgoing events
CAUTION: Assuming chan0 is the uppermost and
         chan1 is below chan0
"""

import sys


def check_direction(f):

    directions = []

    for line in f.readlines():
        try:
            line = line.split()
            directions.append(float(line[3][2:-1]) - float(line[1][2:-1]))
        except:
            pass

    up = 0
    down = 0

    for item in directions:
        if item > 0:
            down += 1
        else:
            up += 1

    rate = float(up)/(up+down)
    print("Upgoing events:", up)
    print("Downgoing events:", down)
    print("Fraction of upgoing events:", rate)
    return up, down, rate


if __name__ == "__main__":
    f = open(sys.argv[1])
    check_direction(f)
