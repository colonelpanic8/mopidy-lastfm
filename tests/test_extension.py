from __future__ import unicode_literals

import unittest

import mock

from mopidy_lastfm import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        self.assertIn('[lastfm]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        self.assertIn('username', schema)
        self.assertIn('password', schema)
        self.assertIn('api_key', schema)
        self.assertIn('secret', schema)

    def test_setup(self):
        ext = Extension()
        ext.setup(mock.Mock())
