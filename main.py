"""badgeomatic - Security badge photo compositor and printer thingie

I have this idea that we could take employee photos with a cell phone
Then send it to a slack channel from where-ever
My bot grabs the photo from the slack channel
Maybe does a little color balancing, cropping
Composites it with our badge template
Takes their name, the date, composites that
Remembers everything in a CSV for later import to the security system
And sends the print job to the HID Fargo printer

Requirements
------------
badgeomatic_globals : program-wide globals, debugger, etc
badgeomatic_slackbot : connect to slack and fire off the badgebot
atexit : trap exits

Functions
---------
tbd
"""

import badgeomatic_globals
import badgeomatic_slackbot
import atexit


def badgeomatic_terminate():
    """Gracefully terminate the program.

    This should try to handle any final cleanup and close any open resources
    before exiting the program entirely
    """

    badgeomatic_globals.debugger.message("INFO",
                                         "Beginning program termination")

    # Show a debugger summary
    badgeomatic_globals.debugger.summary()

    badgeomatic_globals.debugger.exit("Completed program termination")


def badgeomatic_init():
    # Register the tto_terminate() function to run any time the program
    # terminates for any reason, using the atexit library.
    atexit.register(badgeomatic_terminate)


if __name__ == '__main__':
    """badgeomatic Main Function
    
    At this time, under development
    """

    badgeomatic_globals.debugger.message("INFO", "Beginning program execution")

    badgeomatic_init()

    slackbot = badgeomatic_slackbot.Slackbot()
    slackbot.run()


