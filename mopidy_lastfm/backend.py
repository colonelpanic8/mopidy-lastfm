from mopidy import backend

import pykka
import pylast

from . import playlists


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
        self.playlists = playlists.LastFMPlaylistsProvider(backend=self)
        self.uri_schemes = ['lastfm']
