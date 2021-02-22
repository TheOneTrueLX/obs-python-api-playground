# LX's OBS Scripting Playground
A collection of scripts for Open Broadcaster Software (OBS).

## Disclaimer
All of the scripts published here are written for a single person (me) and for a single purpose (my own enjoyment).  There is no guarantee that any of these scripts will function in your unique circumstances (or function at all for that matter).  Uses these scripts at your own risk.

## A Note About Python in OBS on Windows
OBS only supports Python up to v3.6.  For Windows users, go [here](https://www.python.org/downloads/release/python-368/) to download the latest available installer for Python 3.6.8.

The scripts listed here all use (or eventually will use) 3rd party modules.  If you have multiple versions of Python installed, you will need to make sure you're using the correct ``pip`` binary when installing them.  OBS doesn't know how to work with virtual environments, so you'll need to install those modules globally.

Future versions of OBS may changes these requirements, but for now, them's the breaks.

## Current Scripts:
* gameinfo.py: Uses Twitch and IGDB APIs to automatically populate a local browser source with game information, including cover image, release dates, platforms, developers, and publishers.
* smw_exit_counter.py: Turns a "Text (GDI+)" source into a rudimentary Super Mario World exit counter