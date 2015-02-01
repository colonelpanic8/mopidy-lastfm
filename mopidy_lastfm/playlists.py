from __future__ import unicode_literals

import logging

from mopidy import backend, models
from six.moves import urllib
import pylast

from . import util


log = logging.getLogger(__name__)
util.enable_logger(__name__)


class LastFMPlaylistsProvider(backend.PlaylistsProvider):

    def __init__(self, backend):
        self._backend = backend
        self._the_playlist = self.user_playlist('IvanMalison', limit=10)
        log.debug('done')

    def user_playlist(self, username, **kwargs):
        kwargs.setdefault('limit', 100)
        kwargs.setdefault('period', pylast.PERIOD_3MONTHS)
        log.debug('requested {0} - {1}'.format(username, kwargs))
        tracks = self._backend.network.get_user(username).get_top_tracks(
            limit=kwargs['limit'],
            period=kwargs['period']
        )
        log.debug('got pylast tracks')
        mopidy_tracks = util.makelist(self._backend.pylast_to_mopidy_tracks(
            [ti.item for ti in tracks]
        ))
        log.debug('got mopidy tracks')
        urllib.parse.urlencode(kwargs)
        log.debug('made string')
        return models.Playlist(
            tracks=mopidy_tracks,
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
