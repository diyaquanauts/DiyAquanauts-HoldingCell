# DiyAquanauts-HoldingCell
Some place to hold DiyAquanauts scripts I'm on working until they're more ready for prime time...

For the moment, there's a working "capture.py" script that does Audio or Video, depending on if you call it with a "-a" or a "-v" argument.

There's also a set of (as yet unproven) instructions for installing the script(s) as a startup service using SystemD.

There's a semi-working script to grab pressure/depth and temperature from a Pico, but I'd still like to add pH, tubidity, EC, etc.

Next up (at some point) will be the bits for feeding periodic samples of the video/audio streams to a CNN and generating the "Index of Activity" files.  At some point soon, I'll upload the specs for how those should be structured...

Additionally, there's always integrating things into the Serosa API, which will (hopefully) make it much easier to communicate with the various parts of the system and issue "safe" commands...
