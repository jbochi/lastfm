# -*- coding: utf-8 -*-
import md5
import time
import json
import datetime
from urllib import urlopen, urlencode

class LastFMError(Exception):
    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return '%s - %s' % (self.code, self.description)

class Api:
    API_ROOT_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self, api_key, api_secret, token=None, session_key=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = token
        self.session_key = session_key

    def _get_signature(self, params):
        m = md5.new()
        for key, value in iter(sorted(params.iteritems())):
            if key not in ['format', 'callback']:
                m.update(key)
                m.update(value.encode('utf-8'))
        m.update(self.api_secret)
        return m.hexdigest()

    def query_api(self, method, params, sign=True, post=False):
        if 'api_key' not in params:
            params['api_key'] = self.api_key

        if 'method' not in params:
            params['method'] = method

        if sign and self.session_key and 'sk' not in params:
            params['sk'] = self.session_key

        params['format'] = 'json'

        if sign and 'api_sig' not in params:
            params['api_sig'] = self._get_signature(params)

        url = self.API_ROOT_URL

        utf8_params = {}
        for k, v in params.iteritems():
            utf8_params[k] = unicode(v).encode('utf-8')

        json = json.loads(self._http_call(url, utf8_params))
        if 'error' in json:
            raise LastFMError(json['error'], json['message'])

        return json

    def _http_call(self, url, utf8_params, post=False):
        data = urlencode(utf8_params)
        if not post:
            url += '?' + data
            data = None
        return urlopen(url, data)

    def get_session(self):
        json = self.query_api('auth.getSession',
                              {'token': self.token})
        return json['session']

    def get_recommended_artists(self):
        return self.query_api('user.getRecommendedArtists', {},
                              sign=True)

    def get_top_artists(self, user, period='overall'):
        return self.query_api('user.getTopArtists',
                              {'user': user,
                               'period': period},
                              sign=False)

    def get_top_tracks(self, artist, mbid=None, autocorrect='0'):
        return self.query_api('artist.getTopTracks',
                              {'artist': artist,
                               'mbid': mbid,
                               'autocorrect': autocorrect},
                              sign=False)


    def scrobble(self, artist, track, timestamp):
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp)
        return self.query_api('track.scrobble',
                              {'timestamp': timestamp,
                               'track': track,
                               'artist': artist},
                              post=True)

    def update_now_playing(self, artist, track):
        return self.query_api('track.updateNowPlaying',
                              {'track': track,
                               'artist': artist},
                              post=True)
