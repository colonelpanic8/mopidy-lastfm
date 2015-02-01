from __future__ import unicode_literals

import unittest

import mock

from mopidy_lastfm.backend import LastFMBackend


class BackendTest(unittest.TestCase):

    def test_network_creation(self):
        backend = LastFMBackend(mock.MagicMock(), mock.MagicMock())
        backend.on_start()
