import requests
import re

from bs4 import BeautifulSoup


def get_wp_plugin_info_online(plugin=None):
    """Takes a plugin name and returns the description, name and
    tags for the plugin."""
    print("get_wp_plugin_info_online()")
    plugin_url = "http://plugins.svn.wordpress.org/{}/trunk/" \
        .format(plugin)
    try:
        r = requests.get(url=plugin_url)
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
            r = requests.get(url=readme_url)
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


# def get_wp_plugin_info_from_doc(document=None):
#     """Takes a scraped WP plugin page and returns the description and
#     tags and other information for the specified plugin."""
#     # there might not be any tags
#     try:
#         tags = document.find("div",
#                              {
#                                  "class": "tags"
#                              }
#                              ).contents
#         # get list of tags
#         tags = [tag.text for tag in tags]
#         tags = list(set(tags))
#     except AttributeError as e:
#         tags = list()
#
#     try:
#         # pull the description
#         description = document.find(
#             "div",
#             {
#                 "id": "tab-description"
#             }
#         ) \
#             .contents[3] \
#             .text \
#             .strip("\r")
#     except Exception as e:
#         description = "no description"
#         print(e)
#     return tags, description
