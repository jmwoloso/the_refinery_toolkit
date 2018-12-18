"""
wordpress_lookup_service.py: A collection of utilities for the wordpress plugin
lookup service.
"""
from __future__ import print_function, division, unicode_literals, \
    absolute_import

import requests
import re

from bs4 import BeautifulSoup

from .crawler_service import HEADERS

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 Clause"


def get_wp_plugin_info_online(plugin=None):
    """Takes a plugin name and returns the description, name and
    tagshttps://www.silvabokis.com/squarespace-tips/how-to-find-out-which-squarespace-template-a-site-is-using for the plugin."""
    print("get_wp_plugin_info_online()")
    plugin_url = "http://plugins.svn.wordpress.org/{}/trunk/" \
        .format(plugin)
    try:
        r = requests.get(url=plugin_url,
                         headers=HEADERS)
    except requests.exceptions.HTTPError as e:
        print(e)

    if r.status_code != 200:
        description = None
        tags = list()
        name = None
    else:
        # check for the text file as they're potentially named
        # differently
        soup = BeautifulSoup(r.content,
                             "html.parser")

        # find the link with .txt and follow it
        txt_href = soup.select_one("a[href*=.txt]")

        if txt_href is None:
            return list(), None, None
        else:
            txt_href = txt_href.text

        # now visit that and parse the description
        try:
            readme_url = plugin_url + txt_href
            r = requests.get(url=readme_url,
                             headers=HEADERS)
        except requests.exceptions.HTTPError as e:
            print(e)

        if r.status_code != 200:
            description = None
            tags = list()
            name = None
        else:
            name_re = r"(?m)^===\s*(.+?)\s*="
            tags_re = r"(?m)^Tags:\s*(.+?)\r?$"
            d_re = r"(?ms)^== Description ==\s*(.+?)\s+^="
            try:
                name = re.search(name_re,
                                 r.text).group(1)
                name = name.replace("\r", " ").replace("\n", " ")
            except AttributeError as e:
                name = None
            try:
                tags = re.search(tags_re,
                                 r.text)\
                .group(1)\
                .split(",")
                tags = [tag.replace("\r", "").replace("\n", "")
                        for tag in tags]
            except AttributeError as e:
                tags = list()
            try:
                description = re.search(d_re,
                                        r.text).group(1)

                description = description.replace("\r", " ").replace(
                    "\n", " ")
            except AttributeError as e:
                description = None
    print("tags: {}".format(tags))
    print("description: {}".format(description))
    print("name: {}".format(name))
    return tags, description, name
