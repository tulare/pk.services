# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

__all__ = [ 'YoutubeService' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import youtube_dl
import subprocess

from .exceptions import ServiceError
from .types import Service

# --------------------------------------------------------------------

class YoutubeService(Service) :

    def __init__(self) :
        super(YoutubeService, self).__init__(opener=None)
        self._url = None
        self._infos = {}
        self.ytdl = youtube_dl.YoutubeDL({
            'skip_download' : True,
            'logger' : log
        })

    def __getitem__(self, key) :
        return self._infos.get(key, None)

    def update(self) :
        try :
            self._infos = self.ytdl.extract_info(self._url)
        except (youtube_dl.DownloadError, TypeError) as e :
            log.error(e)
            self._infos = {}

    @property
    def url(self) :
        return self['webpage_url']

    @url.setter
    def url(self, url) :
        self._url = url
        self.update()

    def player(self, max_height=None) :
        if 'quality' in self._infos :
            key = 'quality'
        if 'height' in self._infos :
            key = 'height'

        try :
            selected = max(
                filter(
                    lambda f : f[key] <= max_height,
                    self['formats']
                ),
                key = lambda f : f[key]
            )
        except (TypeError, ValueError) :
            if max_height is None :
                selected = max(
                    self['formats'],
                    key = lambda f : f[key]
                )
            else :
                selected = min(
                    self['formats'],
                    key = lambda f : f[key]
                )

        title = '{} - {}'.format(
            self['title'],
            selected['format']
        )
        
        proc = subprocess.Popen([
            'mpv.exe', '--title', title ,selected['url']
        ])
        return proc

    def print_formats(self) :
        for fmt in self['formats'] :
            print(
                '{}'.format(
                    fmt['format']
                )
            )
            
