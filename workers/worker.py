#!/usr/bin python
import sys

from distribrewed.core.utils import coreutils
import distribrewed.core.defaults as defaults

configfile = defaults.DEFAULT_CONFIG

if len(sys.argv) > 1:
    configfile = sys.argv[1]

print('Starting Twisted Brew (config:{0})'.format(configfile))

config = coreutils.parse_config(configfile)
coreutils.start_workers(config)
