
"""
Unit tests for python-twitter

The tests can be run as a C{suite} by running::

    nosetests

"""

import logging

log = logging.getLogger('twitter')
echoHandler = logging.StreamHandler()
echoFormatter = logging.Formatter('%(levelname)-8s %(message)s')
log.addHandler(echoHandler)

# log.setLevel(logging.DEBUG)
