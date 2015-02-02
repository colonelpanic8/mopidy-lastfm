from __future__ import unicode_literals

import logging

from mopidy import backend, models

import pykka
import pylast

from . import library
from . import playlists
from . import util


log = logging.getLogger(__name__)


class LastFMBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(LastFMBackend, self).__init__()
        self._config = config
        self._audio = audio
        self.network = pylast.LastFMNetwork(
            api_key=self._config['lastfm']['api_key'],
            api_secret=self._config['lastfm']['secret'],
        )
        self.network.enable_caching(file_path='pylast.cache')
        self.playlists = playlists.LastFMPlaylistsProvider(self)
        self.library = library.LastFMLibraryProvider(self)
        self.uri_schemes = ['lastfm']

    def pylast_to_mopidy_tracks(self, pylast_tracks):
        for tracks in util.segment(pylast_tracks, 20):
            for playlink, track in zip(
                self.network.get_track_play_links(tracks),
                tracks
            ):
                if playlink is not None:
                    yield models.Track(
                        uri=playlink,
                        name=track.title,
                        artists=[models.Artist(name=track.artist.name, uri='lastfm:arteest')]
                    )
