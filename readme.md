# badgeomatic
## Security badge photo compositor and printer thingie
I have this idea that we could take employee photos with a cell phone,

Then send it to a slack channel from where-ever.  Maybe a private channel
that only some people have access to.  Or something..

My bot grabs the photo from the slack channel,

Maybe does a little color balancing, cropping,

Composites it with our badge template,

Takes their name, the date, composites that too--

Maybe remembers everything in a CSV for later import to the security system?

And sends the print job to the HID Fargo printer.

## Current progress

This is working!  Todos:
- It's jacked up in Windows because, windows file paths and stuff.  Check that out.
- The Slackbot needs tons of cleanup, error trapping, logging
- File handling for the downloaded slack images
- For some reason the Windows image preview won't print, or save.  Seems ok on Mac.  TBD
- How/what to capture to a CSV? 
- Could I use Slack Modal layouts for a super cool interface?