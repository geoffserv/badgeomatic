"""
globals - program globals

This module handles program-wide globals, other variables, data, machine
states.


Requirements
------------
configparser : Basic configuration language parser.
tto_debugger : Error and info message handler.

Classes
-------
tbd : tbd

Functions
---------
config_file_load : Accepts a (config_file) and attempts to load config options.

Variables
---------
debugger : Global instance of Debugger class for logging.
config : Global instance of configparser containing program options.
"""

from configparser import ConfigParser
from debugger import Debugger


debugger = Debugger()  # Program-wide logger and debugger object

config = ConfigParser()  # Program-wide configuration object


def config_file_load(config_file):
    debugger.message("INFO", "Loading config file: {}".format(
        config_file))
    config.read(config_file)
    debugger.message("INFO", "Config Sections: {}".format(
        config.sections()))
    for cay in config['badgeomatic']:
        debugger.message("INFO", "    Key: {}, Value: {}".format(
            cay, config['badgeomatic'][cay]))


# These defaults apply unless overridden in the config file ['tto'] section:
config['DEFAULT'] = {}
# Create a ['tto'] section containing the above defaults:
config['badgeomatic'] = {}

# Load the config file values overtop of the defaults above:
config_file_load("badgeomatic.cfg")

# Define some colors for convenience and readability
color_black = (0, 0, 0)
