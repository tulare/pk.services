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
            self._infos = {'error' : e }

    @property
    def infos(self) :
        return self._infos

    @property
    def url(self) :
        return self['webpage_url']

    @url.setter
    def url(self, url) :
        self._url = url
        self.update()

    def validate(self) :
        if self._url is None or self['error'] is not None :
            raise ServiceError(
                'url: {} - reason: {}'.format(
                    self._url, self['error']
                )
            )

        return True

    def print_formats(self) :
        assert self.validate()
        
        for fmt in self['formats'] :
            print(
                '{}'.format(
                    fmt['format']
                )
            )
        
    def select_format(self, max_height=None) :
        assert self.validate()
        
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

        return selected

    def video(self, max_height=None) :
        
        selected = self.select_format(max_height)

        title = '{} - {}'.format(
            self['title'],
            selected['format']
        )

        return title, selected['url']
        
    def probe(self, max_height=None) :
        title, video_url = self.video(max_height)

        command = [ 'ffprobe', '-show_format', '-show_streams', video_url ]
        probe = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = probe.communicate()

        return out

    def ffplay(self, max_height=None) :
        title, video_url = self.video(max_height)

        command = [
            'ffplay',
            '-window_title', title,
            '-loglevel', 'quiet',
            video_url,
        ]

        return subprocess.Popen(command)

    def mpv(self, max_height=None) :
        title, video_url = self.video(max_height)

        command = [
            'mpv',
            '--title', title,
            video_url,
        ]

        return subprocess.Popen(command)

            
