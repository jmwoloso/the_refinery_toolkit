"""
crawler_service.py: Utility functions used by the crawler service.
"""

__author__ = "jason wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

import re
import requests
from urllib.parse import urlparse

from google.cloud import language
from bs4 import BeautifulSoup


def is_email_link(href=None):
    """Utility function to determine whether the supplied href attribute
    is an email link."""
    print("email_link()")
    return href and 'mailto:' in href


def is_tel_link(href=None):
    """Utility function to detemrine whether the supplied href
    attribute is a telephone link."""
    print("is_tel_link()")
    return href and 'tel:' in href


def is_social_link(href=None):
    """Utility function to determine whether the supplied href
    attribute is a social media link."""
    print("is_social_link()")
    return href and (
            'facebook' in href or 'twitter' in href or 'pinterest'
            in href or 'linkedin' in href)


def get_emails(document=None):
    """Utility function to return emails from a document."""
    print("get_emails()")
    _r = r"'<\S+?>'"
    # this caught false-positives like 'rd@context'
    # _r = r"[\w\.-]+@[\w\.-]+"
    emails = list(
        set(
            re.findall(
                _r,
                document.text) +
            [
                a["href"] for a in
                document.find_all(
                    "a",
                    href=is_email_link
            )
             ]
        )
    )
    return emails


def get_phones(document=None):
    """Utility function that returns any phone numbers found within the
    supplied document."""
    print("get_phones()")
    _r = r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])' \
         r'\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9]' \
         r'[02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|' \
         r'[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9]' \
         r'[02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*' \
         r'(?:#|x\.?|ext\.?|extension)\s*(\d+))?'
    regex_captured_numbers = re.findall(_r, document.text)
    phones = list(set([''.join(match) for
                       match in regex_captured_numbers] +
                      [a["href"] for
                       a in document.
                      find_all("a", href=is_tel_link)]))
    # TODO: hack; fix in regex
    phones = [phone.strip("tel:") for phone in phones]
    return phones


def get_socials(document=None):
    """Utility function that returns social media links from the
    supplied document."""
    print("get_socials()")
    # TODO: add regex back in later
    socials = list(set(
        # re.findall(r'[\w\.-]+@[\w\.-]+', document.text) + [
        [a["href"] for a in
         document.find_all("a", href=is_social_link)]))

    return socials

# TODO: needs implemented
def get_url(ip_address=None):
    """Converts the supplied IP address to the associated URL for
    crawling and parsing."""
    print("get_url()")
    # TODO: figure out how to overcome CDNs (like cloudflare) which
    # obscure the DNS info though perhaps that is a sign that the
    # company is probably too big for our product


def get_content_class(content=None):
    """Utility function that takes website content and returns the
    classification of that text by Google."""
    print("get_content_class()")
    language_client = language.LanguageServiceClient()

    document = language.types.Document(
        content=content,
        type=language.enums.Document.Type.PLAIN_TEXT)

    response = language_client.classify_text(document)

    categories = response.categories

    result = {}

    for category in categories:
        result[category.name] = category.confidence

    # google may not return anything
    if len(result) == 0:
        result["No Category Available"] = 0.0

    return result


def get_wp_plugins(document=None):
    """Retrieves a list of the installed WP plugins."""
    print("get_wp_plugins()")
    r = r"""(?<=wp-content\/plugins\/)(.*?)(?=\/)"""
    plugin_links = document \
        .find_all('link',
                  {'href': re.compile(r)})
    plugins_list = [re.findall(r, tag["href"])[0] for tag in
                    plugin_links]
    plugins_list = list(set(plugins_list))
    return plugins_list


def get_wp_themes(document=None):
    """Returns the WP theme used on the site."""
    print("get_wp_themes()")
    r = r"""(?<=wp-content\/themes\/)(.*?)(?=\/)"""
    themes = document.find_all("link",
                               {"href": re.compile(r)})
    themes_list = [re.findall(r, tag["href"])[0] for tag in themes]
    themes_list = list(set(themes_list))
    return themes_list


def get_all_links(document=None):
    """Function that returns all the links found on the visited page."""
    print("get_all_links()")
    all_links = [a["href"]
                 for a in document.find_all("a", href=True)]
    # remove empty strings
    all_links = [link for link in all_links if len(link) > 0 and
                 link != '/']
    return all_links


def get_internal_links(url=None, links=None):
    """Function that returns the internal links from the website."""
    print("get_internal_links()")
    internal_links_ = list()
    for link in links:
        url_host = urlparse(url).hostname
        domain = urlparse(url).hostname.split(".")[1]
        link_host = urlparse(link).hostname
        if link_host is None:
            continue
        elif link.startswith("/") or url_host == link_host or \
                domain in link_host:
            internal_links_.append(link)
    return internal_links_


def get_external_links(internal_links=None,  all_links=None):
    """Function that returns the external links from a site."""
    print("get_external_links()")
    # TODO: clean this up to remove incorrect links like jquery,
    # tel:, etc.
    _r = r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))" \
         r"([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
    links = [link for link in all_links
             if link not in internal_links]
    # do some additional cleanup to remove jquery anchors, etc.
    external_links = [re.findall(_r, link) for link in links]
    # remove empty lists
    external_links = [link for link in external_links
                      if len(link) > 0]
    # reconstruct original links from remaining tuples
    external_links = [l[0][0] + "://" + l[0][1] + l[0][2]
                      for l in external_links]
    return external_links


def get_hrefs(document=None):
    """Function to return the email, phone and social data from a 
    website."""
    print("get_hrefs()")
    # attempt to fill in the attributes
    emails_ = get_emails(document=document)
    phones_ = get_phones(document=document)
    socials_ = get_socials(document=document)
    return emails_, phones_, socials_


def get_keywords_and_description(document=None):
    """Extracts the keywords and description from the `meta`
    tags."""
    print("get_keywords_and_description()")
    keywords_ = document \
        .find_all(name="meta",
                  attrs={"name": "keywords"})

    if len(keywords_) != 0:
        keywords_ = keywords_[0]["content"] \
            .split(",")

        keywords_ = [keyword.lstrip().rstrip() for keyword in keywords_]

    description_ = document \
        .find_all(name="meta",
                  attrs={"name": "description"})

    if len(description_) != 0:
        description_ = description_[0]["content"].replace("\r", " ")
    return keywords_, description_


def crawl_and_parse(url=None):
    """Utility function to crawl and return the HTML from the
    supplied domain."""
    print("crawl_and_parse()")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/61.0.3163.100 Safari/537.36"
    }

    try:
        resp = requests.get(url=url,
                            headers=headers)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        resp = "Error: {}".format(e)
    except Exception as e:
        resp = "Error: {}".format(e)

    # OK
    if resp.status_code == 200:
        return BeautifulSoup(resp.content,
                             "html.parser")
    else:
        return "error: {}".format(resp)
