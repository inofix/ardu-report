ardu-report
===========

.. .. image:: https://travis-ci.org/zwischenloesung/ardu-report.svg?branch=master
       :target: https://travis-ci.org/zwischenloesung/ardu-report

Python CLI to report back the sensor data from our arduino(s). See
(https://pypi.org/project/ardu-report-lib/ / https://github.com/inofix/ardu-report-lib)
for the main library.

Dependencies, Requirements
--------------------------

 * Unix/Linux

 * Python 2/3

  - tested against: 2.7 and 3.5 (main lib has unittests and Travis-CI)

  - this is just a frontend for 'ardu-report-lib' (main dependency)

  - see requrements.txt for further dependencies

Basic Idea
----------

For now we have one arduino reporting sensor values back over the serial line.
On the other end there is a raspberry pi collecting the data. The data is then processed and either just printed to the console or a file, or sent over mobile or wired/wireless network to, e.g., a webserver..

If more than one arduino are connected. For each one of them the data processing can be configured individually.

Use it for Your Project?
------------------------

I am rewriting the input parser to accept any JSON schema following
the meta schema to control the object index names. As it really only
needs some sort of identifier and a value, there should not be too
many obstacles to use it for your project too.

See the 'schema'
folder for details on the implementation.

The 'example' folder contains JSON file that
validates against the schema and the tests/test\_json.py has
a test run for both the input.json against the schema and the
schema against the meta-schema.. Furthermore there is an
extended-input.json that validates against an example
customized schema (extended-input-schema.json), with itself
still validates against the meta-schema.json.


Example Data for Python Processing
----------------------------------

INPUT: JSON from the arduino over the serial line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two examples under the 'examples' folder.

The simple 'input.json'
shows two example measurements.
The "id" and "value" entries in the object are
mandatory. The "unit" and "threshold" are interpreted for the stdout
log. Any other entry will just be passed on to the output (except for
the sdtout log case).

Note that no timestamp joins the data. Most of the time there is no
clock source available to the dump sensor controller. The timestamp
is added in the output below though. If a timestamp is available
in the input, it can still be passed on of course.

See the 'extended-input.json' for an example with
more enries and custom naming.


OUTPUT: Target JSON from the raspberry pi for the use in e.g. a web app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on the URL specified, the data is appended to a file ("file://") as
a continuing list of JSON objects containing sensor value entries or
sent as a complete JSON array to a web server ("http://" / "https://")
as a POST request. If the URL string is empty, the data is just printed in
text form to stdout.

Example JSON output can be found under the examples folder:

 * output.json - default

 * custom-output.json - if an output JSON scheme is defined, the
   entries can be translated. The output JSON must validate against
   the meta schema..

