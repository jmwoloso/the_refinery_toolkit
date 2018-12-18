"""
classes.py: utility classes used in the the Refinery.

"""
from __future__ import print_function, division, unicode_literals, \
    absolute_import
import json

from googleapiclient.discovery_cache.base import Cache as GoogleCache

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"


class MetadataMixin(dict):
    """Generic mixin class that just serves as a container and can
    have arbitrary attributes programmatically set during refining
    and enrichment."""
    def __init__(self,*arg,**kw):
        super(MetadataMixin, self).__init__(*arg, **kw)

    def __repr__(self):
        return json.dumps(self,
                          indent=2)


class MemoryCache(GoogleCache):
    """Avoids the warning about the file_cache being unavailable."""
    _CACHE = {}

    def get(self, url):
        return MemoryCache._CACHE.get(url)

    def set(self, url, content):
        MemoryCache._CACHE[url] = content
