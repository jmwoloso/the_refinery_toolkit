"""
crawler_service.py: Utility functions used by the crawler service.
"""
from __future__ import print_function, division, unicode_literals, \
    absolute_import

from urllib.parse import urlparse
# try:
#     # for py 3.x
#     from urllib.parse import urlparse
# except ImportError:
#     # for py 2.7
#     from urlparse import urlparse

import re
import requests

import json

from google.cloud import language
from bs4 import BeautifulSoup

from .classes import MetadataMixin

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/61.0.3163.100 Safari/537.36"
}


def is_email_link(href=None):
    """Utility function to determine whether the supplied href attribute
    is an email link."""
    print("email_link()")
    return href and 'mailto:' in href


def is_tel_link(href=None):
    """Utility function to determine whether the supplied href
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
    try:
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
    except Exception as e:
        print(e)
        result = {
            "An Exception Occurred": 0.0
        }
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


def get_squarespace_context(document=None):
    """Returns the Squarespace template used on the site."""
    # this content contains all kinds of useful firmographic data.
    try:
        script = document.find(
            "script",
            {"data-name": "static-context"}
        )\
        .getText(strip=True)

        # now parse out the context object
        context = re.search(
            "(?ms)Static\.SQUARESPACE_CONTEXT = ({.+?});",
            script,
        ).group(1)
        context = json.loads(context)
    except json.decoder.JSONDecodeError as e:
        print(e)
        context = None
    except Exception as e:
        print(e)
        context = None
    return context


def get_all_links(document=None):
    """Function that returns all the links found on the visited page."""
    print("get_all_links()")
    all_links = [a["href"]
                 for a in document.find_all("a", href=True)]
    # remove empty strings
    all_links = [link for link in all_links if len(link) > 0 and
                 link != '/']
    all_links = list(set(all_links))
    return all_links


def get_internal_links(url=None, links=None):
    """Function that returns the internal links from the website."""
    print("get_internal_links()")
    internal_links_ = list()
    for link in links:
        if link is None:
            continue
        print(link)
        url_host = urlparse(url).hostname
        domain = urlparse(url).hostname.split(".")[1]
        print(domain)
        link_host = urlparse(link).hostname
        print(link_host)
        if link.startswith("/"):
            print("True")
            internal_links_.append(link)
        if url_host == link_host:
            internal_links_.append(link)
        if link_host is not None and domain in link_host:
            internal_links_.append(link)
        else:
            continue

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
    try:
        resp = requests.get(url=url,
                            headers=HEADERS)
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


def make_crawler_gcs_payload(request=None):
    """Utility function to flatten and parse the fields we need in
    BQ."""
    print("make_crawler_gcs_payload()")
    p = MetadataMixin()
    r = request.copy()

    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["html_string"] = r["document"]
    p["all_links"] = r["all_links"]
    p["internal_links"] = r["internal_links"]
    p["external_links"] = r["external_links"]
    p["href_emails"] = r["href_emails"]
    p["href_phones"] = r["href_phones"]
    p["href_socials"] = r["href_socials"]
    p["meta_keywords"] = r["meta_keywords"]
    p["ip_revealed"] = r["ip_revealed"]
    p["fuzzy_match"] = r["fuzzy_match"]
    if len(r["meta_description"]) != 0:
        p["meta_description"] = r["meta_description"].replace("\r", "")
    else:
        p["meta_description"] = None
    # add the metadata we injected to the request along the way
    p["refinery_company_id"] = r["refinery_company_id"]
    p["refinery_person_id"] = r["refinery_person_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["sfdc_lead_id"] = r["sfdc_lead_id"]
    p["sfdc_contact_id"] = r["sfdc_contact_id"]
    p["sfdc_asset_id"] = r["sfdc_asset_id"]
    p["sfdc_acct_id"] = request["sfdc_acct_id"]
    p["sfdc_oppty_id"] = request["sfdc_oppty_id"]
    p["app_name"] = request["app_name"]
    # TODO: should we keep all the content classifications if > 1 are
    # returned?
    if "No Category Available" in r["content_classification"].keys():
        p["classification_category"] = "No Category Available"
        p["classification_confidence"] = 0.0
        p["tier1_classification"] = "No Category Available"
        p["tier2_classification"] = None
        p["tier3_classification"] = None
    elif "An Exception Occurred" in r["content_classification"].keys():
        p["classification_category"] = "An Exception Occurred"
        p["classification_confidence"] = 0.0
        p["tier1_classification"] = "An Exception Occurred"
        p["tier2_classification"] = None
        p["tier3_classification"] = None
    else:
        max_class = None
        max_likelihood = 0.0
        for cat, prob in r["content_classification"].items():
            if prob > max_likelihood:
                max_likelihood = prob
                max_class = cat

            p["classification_category"] = max_class
            p["classification_confidence"] = max_likelihood
            # there are 1, 2 or 3 possible levels deep for the
            # classification
            # https://cloud.google.com/natural-language/docs/categories
            cat_list = max_class.split("/")[1:]
            if len(cat_list) == 1:
                p["tier1_classification"], \
                p["tier2_classification"], \
                p["tier3_classification"] = cat_list[0], None, None
            if len(cat_list) == 2:
                (
                    p["tier1_classification"],
                    p["tier2_classification"]
                ), \
                p["tier3_classification"] = cat_list, None
            if len(cat_list) == 3:
                p["tier1_classification"], \
                p["tier2_classification"], \
                p["tier3_classification"] = cat_list
    print("payload: {}".format(p))
    return p


def make_crawler_bq_payload(request=None):
    """Utility function to flatten and parse the fields we need in
    BQ."""
    print("make_crawler_gcs_payload()")
    p = MetadataMixin()
    r = request.copy()

    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["html_string"] = r["html_string"]
    p["ip_revealed"] = r["ip_revealed"]
    p["fuzzy_match"] = r["fuzzy_match"]
    p["all_links"] = " >>> ".join(
        r["all_links"]
    )
    p["internal_links"] = " >>> ".join(
        r["internal_links"]
    )
    p["external_links"] = " >>> ".join(
        r["external_links"]
    )
    p["href_emails"] = " >>> ".join(
        r["href_emails"]
    )
    p["href_phones"] = " >>> ".join(
        r["href_phones"]
    )
    p["href_socials"] = " >>> ".join(
        r["href_socials"]
    )
    p["meta_keywords"] = " >>> ".join(
        r["meta_keywords"]
    )
    p["meta_description"] = r["meta_description"]
    # add the metadata we injected to the request along the way
    p["refinery_company_id"] = r["refinery_company_id"]
    p["refinery_person_id"] = r["refinery_person_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["sfdc_lead_id"] = r["sfdc_lead_id"]
    p["sfdc_contact_id"] = r["sfdc_contact_id"]
    p["sfdc_asset_id"] = r["sfdc_asset_id"]
    p["sfdc_oppty_id"] = r["sfdc_oppty_id"]
    p["sfdc_acct_id"] = r["sfdc_acct_id"]
    p["app_name"] = r["app_name"]
    p["classification_confidence"] = r["classification_confidence"]
    p["tier1_classification"] = \
        r["tier1_classification"]
    p["tier2_classification"] = \
        r["tier2_classification"]
    p["tier3_classification"] = \
        r["tier3_classification"]
    print("payload: {}".format(p))
    return p


def wordpress_routines(request=None, is_parsed=True):
    """Utility function containing all the wordpress enrichment 
    routines."""
    print("wordpress_routines()")

    # container for holding the crawler results
    resp = MetadataMixin()

    # add the domain and url to the metadata container
    resp["domain"] = request["domain"]
    resp["url"] = request["url"]

    if is_parsed is False:
        # crawl the site and return the html for parsing
        resp["document"] = crawl_and_parse(url=resp["url"])
    elif is_parsed is True:
        resp["document"] = request["document"]

    # get the word press themes
    resp["wp_themes"] = get_wp_themes(document=resp["document"])

    # get the word press plugins
    resp["wp_plugins"] = get_wp_plugins(document=resp["document"])

    return resp


def squarespace_routines(request=None):
    """Utility function containing"""
    print("squarespace_routines()")

    # container for holding the crawler results
    resp = MetadataMixin()

    # add the domain and url to the metadata container
    resp["domain"] = request["domain"]
    resp["url"] = request["url"]

    # crawl the site and return the html for parsing
    resp["document"] = crawl_and_parse(url=resp["url"])

    # if the site is squarespace, we'll get the context object and
    # parse the info in it
    resp["squarespace_context"] = get_squarespace_context(
        document=resp["document"])

    return resp


def domain_routines(request=None):
    """Utility function containing the normal enrichment routines for
    the webcrawler."""
    print("domain_routines()")

    # container for holding the crawler results
    resp = MetadataMixin()

    # add the domain and url to the metadata container
    resp["domain"] = request["domain"]
    resp["url"] = request["url"]

    # crawl the site and return the html for parsing
    resp["document"] = crawl_and_parse(url=resp["url"])

    # get all links
    resp["all_links"] = get_all_links(document=resp["document"])

    # get the internal links
    resp["internal_links"] = \
        get_internal_links(url=resp["url"],
                               links=resp["all_links"])

    # get the external links
    resp["external_links"] = \
        get_external_links(internal_links=resp["internal_links"],
                               all_links=resp["all_links"])

    # get the phone, email and social data
    resp["href_emails"], resp["href_phones"], resp["href_socials"] = \
        get_hrefs(document=resp["document"])

    # get the keyword and description
    resp["meta_keywords"], resp["meta_description"] = \
        get_keywords_and_description(document=resp["document"])

    # get the content classification
    resp["content_classification"] = \
        get_content_class(content=resp["document"].text)

    # convert bs4 soup to plain string so we can convert it to json
    resp["document"] = resp["document"].prettify()

    return resp


# TODO: can we abstract this to fit all cases (tags, tech, wp)
def make_crawler_wordpress_payload(request=None):
    """Utility function that creates a payload for the Wordpress
    bucket."""
    print("make_crawler_wordpress_payload()")
    r = request.copy()
    p = MetadataMixin()

    p["refinery_company_id"] = r["refinery_company_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["ip_revealed"] = r["ip_revealed"]
    p["fuzzy_match"] = r["fuzzy_match"]
    # TODO: add additional lists here (wix, squarespace, etc.)
    if len(r["wp_themes"]) != 0:
        p["wp_themes"] = r["wp_themes"]
    if len(r["wp_plugins"]) != 0:
        p["wp_plugins"] = r["wp_plugins"]
    print("payload: {}".format(p))
    return p


def make_crawler_squarespace_payload(request=None):
    """Extracts useful fields from the Static.SQUARESPACE_CONTEXT
    object."""
    print("make_crawler_squarespace_payload()")
    r = request["squarespace_context"].copy()
    p = MetadataMixin()
    p["refinery_company_id"] = request["refinery_company_id"]
    p["refined_at"] = request["refined_at"]
    p["refined_date"] = request["refined_date"]
    p["domain"] = request["domain"]
    p["url"] = request["url"]
    p["ip_revealed"] = request["ip_revealed"]
    p["fuzzy_match"] = request["fuzzy_match"]

    # there is no guarantee any of these will be available in the
    # payload
    try:
        p["template_id"] = r["templateId"]
    except KeyError as e:
        p["template_id"] = None
    try:
        p["authentic_url"] = r["website"]["authenticUrl"]
    except KeyError as e:
        p["authentic_url"] = None
    try:
        p["base_url"] = r["website"]["baseUrl"]
    except KeyError as e:
        p["base_url"] = None
    try:
        p["content_modified_at"] = r["website"]["contentModifiedOn"]
    except KeyError as e:
        p["content_modified_at"] = None
    try:
        p["internal_url"] = r["website"]["internalUrl"]
    except KeyError as e:
        p["internal_url"] = None
    try:
        p["language"] = r["website"]["language"]
    except KeyError as e:
        p["language"] = None
    try:
        p["time_zone"] = r["website"]["timeZone"]
    except KeyError as e:
        p["time_zone"] = None
    try:
        p["time_zone_abbr"] = r["website"]["timeZoneAbbr"]
    except KeyError as e:
        p["time_zone_abbr"] = None
    try:
        p["utc_offset"] = r["website"]["TimeZoneOffset"] / 3.6e+6
    except KeyError as e:
        p["utc_offset"] = None
    try:
        p["site_description"] = r["website"]["siteDescription"].replace(
            "\r", "").replace("\n", "").replace("<p>", "")
    except KeyError as e:
        p["site_description"] = None
    try:
        p["site_title"] = r["website"]["siteTitle"]
    except KeyError as e:
        p["site_title"] = None
    try:
        p["primary_domain"] = r["website"]["primaryDomain"]
    except KeyError as e:
        p["primary_domain"] = None
    try:
        # TODO: this is a list so iterate through when adding to BQ
        p["social_accounts"] = r["website"]["socialAccounts"]
    except KeyError as e:
        p["social_accounts"] = None
    try:
        p["state"] = r["websiteSettings"]["state"]
    except KeyError as e:
        p["state"] = None
    try:
        p["supported_currencies"] = \
        r["websiteSettings"]["storeSettings"] \
            ["currenciesSupported"]
    except KeyError as e:
        p["supported_currencies"] = None
    try:
        p["default_currency"] = r["websiteSettings"]["storeSettings"] \
            ["defaultCurrency"]
    except KeyError as e:
        p["default_currency"] = None
    try:
        p["express_checkout_enabled"] = \
        r["websiteSettings"]["storeSettings"] \
            ["expressCheckout"]
    except KeyError as e:
        p["express_checkout_enabled"] = None
    try:
        p["light_cart_enabled"] = r["websiteSettings"]["storeSettings"] \
            ["useLightCart"]
    except KeyError as e:
        p["light_cart_enabled"] = None
    try:
        p["squarespace_website_id"] = \
        r["websiteSettings"]["storeSettings"] \
            ["websiteId"]
    except KeyError as e:
        p["squarespace_website_id"] = None
    try:
        p["mailing_list_opt_in_enabled"] = \
        r["websiteSettings"]["storeSettings"] \
            ["enableMailingListOptInByDefault"]
    except KeyError as e:
        p["mailing_list_opt_in_enabled"] = None
    try:
        p["business_name"] = \
            r["websiteSettings"]["storeSettings"] \
                ["businessName"]
    except KeyError as e:
        p["business_name"] = None
    try:
        p["business_address_line_1"] = \
            r["websiteSettings"]["storeSettings"] \
                ["contactLocation"]["addressLine1"]
    except KeyError as e:
        p["business_address_line_1"] = None
    try:
        p["business_address_line_2"] = \
            r["websiteSettings"]["storeSettings"] \
                ["contactLocation"]["addressLine2"]
    except KeyError as e:
        p["business_address_line_2"] = None
    try:
        p["business_address_country"] = \
            r["websiteSettings"]["storeSettings"] \
                ["contactLocation"]["addressCountry"]
    except KeyError as e:
        p["business_address_country"] = None
    try:
        p["typekit_id"] = r["website"]["typekitId"]
    except KeyError as e:
        p["typekit_id"] = None
    try:
        p["typekit_id"] = r["website"]["typekitId"]
    except KeyError as e:
        p["typekit_id"] = None
    try:
        p["address_title"] = r["website"]["location"][
            "addressTitle"]
    except KeyError as e:
        p["address_title"] = None
    try:
        p["address_line_1"] = r["website"]["location"][
            "addressLine1"]
    except KeyError as e:
        p["address_line_1"] = None
    try:
        p["address_line_2"] = r["website"]["location"][
            "addressLine2"]
    except KeyError as e:
        p["address_line_2"] = None
    try:
        p["latitude"] = r["website"]["location"]["mapLat"]
    except KeyError as e:
        p["latitude"] = None
    try:
        p["longitude"] = r["website"]["location"]["mapLng"]
    except KeyError as e:
        p["latitude"] = None
    # try:
    #     p["payment_settings"] = r["website"][""]

    return p


