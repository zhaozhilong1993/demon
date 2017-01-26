#!/usr/bin/python

import optparse
import os

def main():
    today = os.popen("date '+%Y-%m-%d'").read()
    p = optparse.OptionParser()
    p.add_option("--date", "-d", default=today)
    p.add_option("--date", "-p", default=today)
