#!/usr/bin/env python3
"""
Reads a given text and returns just the numbers from it
"""

import sys


def get_numbers():
    for line in open(sys.argv[1]).readlines():
        fields = line.split(' ')
        for field in fields:
            try:
                print float(field)
            except ValueError:
                pass


if __name__ == "__main__":
    get_numbers()
