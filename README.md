# tresjolie

Utilities for processing open data related to Tampere public transport

## Purpose

These routines help to massage the Tampere Public Transport
[GTFS data](http://wiki.itsfactory.fi/index.php/Tampere_Public_Transport_GTFS_feed)
provided by [ITS Factory](http://www.hermiagroup.fi/its-factory/)
into formats more suitable for use in applications. They are primary intended to
help the development of [BusMonTRE](http://www.coniferproductions.com/apps/busmontre/), 
but are released as open source, in the hope that other
application developers will find them useful.

The Tampere Public Transport data is released under 
[its own license](http://www.tampere.fi/tampereinfo/avoindata/avoindatalisenssi.html)
(in Finnish only), so it is not duplicated here.

## Installation and usage

The Python version requires Python 3 or later. 

* Set up a virtual environment in the project directory 
using `python3 -m venv venv`. 
* Activate the virtual environment with `source venv/bin/activate`.
You should see the command prompt change to indicate an active
virtual environment.
* Install the required dependencies. For example, to install Requests,
type `pip3 install requests`.
 
Type `cd python; python3 tresjolie.py` to show usage information.

When you're done, deactivate the virtual environment with `deactivate`.

## About the name

It's a pun, of course:

* _Très jolie_ is French for _very nice_
* _TRE_ is a common abbreviation for [Tampere](http://www.tampere.fi)
* Public transport is _joukkoliikenne_ in Finnish, sometimes abbreviated as _joli_
* The _e_ is for example (_esimerkki_ in Finnish)

## License

Copyright © 2014-2018 Conifer Productions Oy

Distributed under the MIT License.
