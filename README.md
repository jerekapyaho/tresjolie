tresjolie for Clojure and Python

The Clojure README contains information about this project. It will be
migrated here soon.

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

There are two independent subprojects, one for Python and one for 
[Clojure](http://clojure.org).

### Python notes

The Python version requires Python 3 or later. There's no specific setup;
just execute the script in _python/tresjolie_.

### Clojure notes

Use [Leiningen](http://leiningen.org) to build and run.

### Usage

Currently the only GTFS file type processed is a stops file, usually
found in a GTFS data dump as `stops.txt`. It is a CSV file with a header row.
Before using it with these tools, remove the header row, and convert the file
into UTF-8 encoding, if necessary, since that is what _tresjolie_ assumes.

## About the name

It's a pun, of course:

* _Très jolie_ is French for _very nice_
* _TRE_ is a common abbreviation for [Tampere](http://www.tampere.fi)
* Public transport is _joukkoliikenne_ in Finnish, sometimes abbreviated as _joli_
* The _e_ is for example (_esimerkki_ in Finnish)

## License

Copyright © 2014 Conifer Productions Oy

Distributed under the MIT License.
