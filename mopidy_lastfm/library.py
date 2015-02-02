from __future__ import unicode_literals

import itertools
import logging
from six.moves import urllib

from mopidy import backend, models
from mopidy_spotify import translator
import pylast

from . import util


log = logging.getLogger(__name__)
util.enable_logger(__name__)
log_decorator = util.build_log_decorator(log)


class LastFMLibraryProvider(backend.LibraryProvider):

    ALL_PERIODS = [
        pylast.PERIOD_OVERALL,
        pylast.PERIOD_7DAYS,
        pylast.PERIOD_3MONTHS,
        pylast.PERIOD_6MONTHS,
        pylast.PERIOD_12MONTHS,
    ]

    @staticmethod
    def _normalize_kwargs(kwargs):
        return {
            key: value[0] if isinstance(value, list) else value
            for key, value in kwargs.items()
        }

    @log_decorator
    def __init__(self, backend):
        self._backend = backend
        self._request_type_to_handler = {
            'user': self._handle_user_playlist_lookup, # self._handle_user_album_lookup,
            'user-album': self._handle_user_playlist_lookup, #self._handle_user_album_lookup,
            'artist': self._handle_artist_album_lookup
        }

    @log_decorator
    def search(self, query=None, uris=None):
        if query is None:
            return
        queries = query.get('any', []) + query.get('albums', [])
        users = [self._user_exists(query) for query in queries]
        return models.SearchResult(albums=[
            user_album for user in users
            for user_album in
            self._build_user_albums(user)
            if user is not None
        ])

    @log_decorator
    def lookup(self, uri):
        _, request_type, identifier, query_string = uri.split(':')
        return self._request_type_to_handler[request_type](
            identifier, **self._normalize_kwargs(urllib.parse.parse_qs(query_string))
        )

    def _handle_user_playlist_lookup(self, username, **kwargs):
        return models.Playlist(
            tracks=self._handle_user_tracks_lookup(username, **kwargs),
            name=self._generate_name(username, **kwargs),
            uri="lastfm:user:{0}".format(self._generate_uri_tail(username, **kwargs))
        )

    def _handle_user_album_lookup(self, username, **kwargs):
        return self._handle_user_tracks_lookup(username, **kwargs)

    def _handle_artist_album_lookup(self, artist, **kwargs):
        pass

    def _handle_user_tracks_lookup(self, username, **kwargs):
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
        return mopidy_tracks

    def _generate_uri_tail(self, identifier, **kwargs):
        return "{0}:{1}".format(identifier, urllib.parse.urlencode(kwargs))

    def _generate_name(self, identifier, **kwargs):
        return "{0} - {1}".format(identifier, kwargs)

    @property
    def limit(self):
        return self._backend._config['lastfm']['top_list_size']

    def _build_user_albums(self, user):
        return [
            models.Album(
                uri='lastfm:user-album:{0}'.format(
                    self._generate_uri_tail(user.name,
                                            limit=self.limit,
                                            period=period)
                ),
                name=self._generate_name(user.name,
                                        limit=self.limit,
                                        period=period),
            )
            for period in self.ALL_PERIODS
        ]

    def _user_exists(self, username):
        user = self._backend.network.get_user(username)
        try:
            user.get_name(properly_capitalized=True)
        except:
            return None
        else:
            return user
