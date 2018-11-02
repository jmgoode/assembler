#!/usr/bin/env python3

"""
MPCS52011 Project 0
Whitespace and Comment Parser
Author: Jason Goode
"""

import sys
import os

# program logic
def strip(in_file):
    """Program Logic"""
    # read in file
    f = open(in_file, 'r')
    lines = f.readlines()

    out_file = in_file.split('.asm')[0] + '_clean.asm'
    out = open(out_file, 'w')

    for line in lines: # iterate each line of the in file
        if line.startswith('//') is False and line.startswith('\n') is False:
            no_whitespace = line.replace(" ", "") # strip whitespace
            if '//' in no_whitespace:
                no_comments = no_whitespace.split('//')[0] + '\n' # store anything to left of commment
                if no_comments != '':
                    out.write(no_comments) # write anything to left of comments delimiter, unless blank
            else:
                out.write(no_whitespace)
