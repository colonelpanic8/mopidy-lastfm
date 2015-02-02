from __future__ import unicode_literals

import logging

from mopidy import backend, models
from six.moves import urllib
import pylast

from . import util


log = logging.getLogger(__name__)
util.enable_logger(__name__)
log_decorator = util.build_log_decorator(log)


class LastFMPlaylistsProvider(backend.PlaylistsProvider):

    def __init__(self, backend):
        self._backend = backend
        self._the_playlist = self.user_playlist('IvanMalison', limit=10)
        log.debug('done')

    @log_decorator
    def lookup(self, uri):
        return self._backend.library.lookup(uri)

    def user_playlist(self, username, **kwargs):
        return models.Playlist(
            tracks=[],
            name="top tracks",
            uri="lastfm:user:{0}:{1}".format(
                username, urllib.parse.urlencode(kwargs)
            )
        )

    @staticmethod
    def _normalize_kwargs(kwargs):
        return {
            key: value[0] if isinstance(value, list) else value
            for key, value in kwargs.items()
        }

    @property
    def playlists(self):
        return [self._the_playlist]
