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
        mopidy_tracks = util.makelist(self.pylast_to_mopidy_tracks(
            [ti.item for ti in tracks]
        ))
        log.debug('got mopidy tracks')
        return models.Playlist(
            tracks=mopidy_tracks,
            name="top tracks",
            uri="lastfm:user:{0}:{1}".format(
                username, urllib.parse.urlencode(kwargs)
            )
        )

    @property
    def playlists(self):
        return []

    def lookup(self, uri):
        log.debug('lookup')
        _, playlist_type, identifier, query_string = uri.split(':')
        return self.user_playlist(
            identifier, **urllib.parse.parse_qs(query_string)
        )

    def pylast_to_mopidy_tracks(self, pylast_tracks):
        for tracks in util.segment(pylast_tracks, 20):
            for playlink, track in zip(
                self._backend.network.get_track_play_links(tracks),
                tracks
            ):
                if playlink is not None:
                    yield models.Track(
                        uri=playlink,
                        name=track.title,
                        artists=[track.artist.name]
                    )
