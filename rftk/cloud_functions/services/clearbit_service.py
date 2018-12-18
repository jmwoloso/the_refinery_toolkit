"""
clearbit_service.py: Utility functions used by the clearbit service.
"""
from __future__ import print_function, division, unicode_literals, \
    absolute_import
import sys
import os
import base64
import time
import requests

import googleapiclient.discovery
from google.cloud import storage
import clearbit
import gcsfs

from .classes import MemoryCache, MetadataMixin
from .constants import MAX_RETRIES, SLEEP_LENGTH

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"


def decrypt_with_kms(project_id=None, location_id=None,
                     key_ring_id=None, crypto_key_id=None,
                     ciphertext_string=None):
    """Decrypts data from ciphertext_string stored in GCS."""
    print("decrypt_with_kms()")
    # Creates an API client for the KMS API.
    kms_client = googleapiclient \
        .discovery \
        .build(
        "cloudkms",
        "v1",
        cache=MemoryCache()
    )

    # The resource name of the CryptoKey.
    name = \
        "projects/{}/locations/{}/keyRings/{}/cryptoKeys/{}" \
            .format(
            project_id,
            location_id,
            key_ring_id,
            crypto_key_id
        )

    # Use the KMS API to decrypt the data.
    crypto_keys = \
        kms_client \
            .projects() \
            .locations() \
            .keyRings() \
            .cryptoKeys()

    request = crypto_keys.decrypt(
        name=name,
        body={
            "ciphertext": base64.b64encode(
                ciphertext_string
            ).decode(
                "ascii"
            )
        }
    )
    response = request.execute()
    plaintext = base64.b64decode(
        response["plaintext"]
            .encode(
            "ascii"
        )
    ) \
        .decode() \
        .strip("\n")

    return plaintext


def get_service_configs(service=None, project_name=None):
    """Utility function to set configurations for the service."""
    print("get_service_configs()")
    if service == "clearbit":
        try:
            # set configs from the env vars of the machine
            PROJECT_ID = os.environ["GCP_PROJECT_ID"]
            LOCATION_ID = os.environ["GCP_LOCATION_ID"]
            KEYRING_ID = os.environ["GCP_KEYRING_ID"]
            CRYPTO_KEY_ID = os.environ["GCP_KEY_ID"]
            CIPHERTEXT_BLOB = os.environ["GCP_CIPHERTEXT_BLOB"]
            BUCKET_NAME = os.environ["GCS_BUCKET"]

            # DEPRECATED
            # set clearbit api versions
            # clearbit.Person.set_version("2018-06-06")
            # clearbit.Company.set_version("2017-09-12")
            # clearbit.Reveal.set_version("2018-03-28")
            # # not in use
            # clearbit.Watchlist.set_version("2015-11-13")
            # # not in use
            # clearbit.Prospector.set_version("2016-10-04")

            fs = gcsfs.GCSFileSystem(
                project=project_name,
                access="full_control",
                token="cloud",
                # consistency="md5",
                cache_timeout=None,
                secure_serialize=True,
                check_connection=True
            )

            fs.retries = 7
            fs.connect(method="cloud")

            cipher_string = fs.cat(BUCKET_NAME + "/" + CIPHERTEXT_BLOB)

            # DEPRECATED
            # download the file as a string in-memory
            # st_client = storage.Client()
            # bucket = st_client.get_bucket(BUCKET_NAME)
            # cipher_blob = bucket.blob(CIPHERTEXT_BLOB)
            # cipher_string = cipher_blob.download_as_string()

            # decrypt the kms key stored in gcs and set the key attr
            clearbit.key = decrypt_with_kms(
                project_id=PROJECT_ID,
                location_id=LOCATION_ID,
                key_ring_id=KEYRING_ID,
                crypto_key_id=CRYPTO_KEY_ID,
                ciphertext_string=cipher_string
            )
            print("configs_set: True")
        # catch-all
        except Exception as e:
            print("config_set: False")
            error = {
                "error_message": e,
                "status_code": "Unknown"
            }
            print(error)
    # flags for services
    if service == "crawler":
        # NOT IMPLEMENTED/NEEDED
        pass


# TODO: to rftk.clearbit_service module
def make_clearbit_company_gcs_payload(request=None):
    """Utility function to flatten and parse the fields we need in
    BQ."""
    print("make_clearbit_company_gcs_payload()")
    r = request["company"].copy()
    p = MetadataMixin()

    # add the metadata we injected to the request along the way
    p["refinery_company_id"] = request["refinery_company_id"]
    p["refinery_person_id"] = request["refinery_person_id"]
    p["refined_at"] = request["refined_at"]
    p["refined_date"] = request["refined_date"]
    p["sfdc_lead_id"] = request["sfdc_lead_id"]
    p["sfdc_contact_id"] = request["sfdc_contact_id"]
    p["sfdc_asset_id"] = request["sfdc_asset_id"]
    p["sfdc_acct_id"] = request["sfdc_acct_id"]
    p["sfdc_oppty_id"] = request["sfdc_oppty_id"]
    p["app_name"] = request["app_name"]
    p["url"] = request["url"]
    p["domain"] = request["domain"]
    p["ip_revealed"] = request["ip_revealed"]
    p["fuzzy_match"] = request["fuzzy_match"]
    p["ip_address"] = request["ip_address"]

    # add the company data returned by clearbit
    p["clearbit_company_id"] = r["id"]
    p["company_name"] = r["name"]
    p["legal_name"] = r["legalName"]
    p["company_domain"] = r["domain"]
    p["domain_aliases"] = " >>> ".join(
        r["domainAliases"]
    )

    # category
    p["industry"] = r["category"]["industry"]
    p["industry_group"] = r["category"]["industryGroup"]
    p["naics_code"] = r["category"]["naicsCode"]
    p["sector"] = r["category"]["sector"]
    p["sic_code"] = r["category"]["sicCode"]
    p["sub_industry"] = r["category"]["subIndustry"]

    # p["tags"] = r["tags"]
    # TODO: parse this to remove /r
    if r["description"] is not None:
        p["description"] = r["description"].replace("\r", " ")
    else:
        p["description"] = r["description"]
    p["year_founded"] = r["foundedYear"]
    p["location"] = r["location"]
    p["time_zone"] = r["timeZone"]
    p["utc_offset"] = r["utcOffset"]

    # geo
    p["street_number"] = r["geo"]["streetNumber"]
    p["street_name"] = r["geo"]["streetName"]
    p["sub_premise"] = r["geo"]["subPremise"]
    p["city"] = r["geo"]["city"]
    p["postal_code"] = r["geo"]["postalCode"]
    p["state"] = r["geo"]["state"]
    p["state_code"] = r["geo"]["stateCode"]
    p["country"] = r["geo"]["country"]
    p["country_code"] = r["geo"]["countryCode"]
    p["latitude"] = r["geo"]["lat"]
    p["longitude"] = r["geo"]["lng"]

    p["company_logo"] = r["logo"]

    # fakebook
    p["facebook_handle"] = r["facebook"]["handle"]
    p["facebook_likes"] = r["facebook"]["likes"]

    # linkedin
    p["linkedin_handle"] = r["linkedin"]["handle"]

    # twitter
    # TODO: parse the text from bio to eliminate /r
    p["twitter_handle"] = r["twitter"]["handle"]
    p["twitter_id"] = r["twitter"]["id"]
    if r["twitter"]["bio"] is not None:
        p["twitter_bio"] = r["twitter"]["bio"].replace("\r", " ")
    else:
        p["twitter_bio"] = r["twitter"]["bio"]
    p["twitter_follower_count"] = r["twitter"]["followers"]
    p["twitter_following_count"] = r["twitter"]["following"]
    p["twitter_location"] = r["twitter"]["location"]
    p["twitter_site_url"] = r["twitter"]["site"]
    p["twitter_avatar"] = r["twitter"]["avatar"]

    # crunchbase
    p["crunchbase_handle"] = r["crunchbase"]["handle"]

    p["is_email_provider"] = r["emailProvider"]
    p["company_type"] = r["type"]
    p["ticker_symbol"] = r["ticker"]
    p["tax_ein"] = r["identifiers"]["usEIN"]
    p["company_phone"] = r["phone"]
    p["clearbit_indexed_at"] = r["indexedAt"]

    # metrics
    p["alexa_us_rank"] = r["metrics"]["alexaUsRank"]
    p["alexa_global_rank"] = r["metrics"]["alexaGlobalRank"]
    p["number_of_employees"] = r["metrics"]["employees"]
    p["number_of_employees_range"] = r["metrics"]["employeesRange"]
    p["market_cap"] = r["metrics"]["marketCap"]
    p["total_raised"] = r["metrics"]["raised"]
    p["annual_revenue"] = r["metrics"]["annualRevenue"]
    p["estimated_annual_revenue"] = r["metrics"][
        "estimatedAnnualRevenue"]
    p["fiscal_year_ends"] = r["metrics"]["fiscalYearEnd"]

    # p["tech"] = r["tech"]
    p["parent_domain"] = r["parent"]["domain"]
    return p


def make_clearbit_person_gcs_payload(request=None):
    """Utility function to flatten and parse the fields we need in
    BQ."""
    print("make_clearbit_person_gcs_payload()")
    r = request["person"].copy()
    p = MetadataMixin()

    # add the metadata we injected to the request along the way
    p["refinery_person_id"] = request["refinery_person_id"]
    p["refinery_company_id"] = request["refinery_company_id"]
    p["refined_at"] = request["refined_at"]
    p["refined_date"] = request["refined_date"]
    p["sfdc_lead_id"] = request["sfdc_lead_id"]
    p["sfdc_contact_id"] = request["sfdc_contact_id"]
    p["sfdc_asset_id"] = request["sfdc_asset_id"]
    p["sfdc_acct_id"] = request["sfdc_acct_id"]
    p["sfdc_oppty_id"] = request["sfdc_oppty_id"]
    p["app_name"] = request["app_name"]
    p["url"] = request["url"]
    p["domain"] = request["domain"]
    p["ip_revealed"] = request["ip_revealed"]

    p["clearbit_person_id"] = r["id"]
    p["clearbit_indexed_at"] = r["indexedAt"]
    p["full_name"] = r["name"]["fullName"]
    p["first_name"] = r["name"]["givenName"]
    p["last_name"] = r["name"]["familyName"]
    p["email"] = r["email"]

    # geo
    p["location"] = r["location"]
    p["time_zone"] = r["timeZone"]
    p["utc_offset"] = r["utcOffset"]
    p["city"] = r["geo"]["city"]
    p["state"] = r["geo"]["state"]
    p["state_code"] = r["geo"]["stateCode"]
    p["country"] = r["geo"]["country"]
    p["country_code"] = r["geo"]["countryCode"]
    p["latitude"] = r["geo"]["lat"]
    p["longitude"] = r["geo"]["lng"]

    # social
    if r["bio"] is not None:
        p["bio"] = r["bio"].replace("\r", " ")
    else:
        p["bio"] = r["bio"]
    p["site"] = r["site"]
    p["avatar"] = r["avatar"]

    # employment
    p["employment_domain"] = r["employment"]["domain"]
    p["employment_name"] = r["employment"]["name"]
    p["employment_title"] = r["employment"]["title"]
    p["employment_role"] = r["employment"]["role"]

    # more social
    p["employment_seniority"] = r["employment"]["seniority"]
    p["facebook_handle"] = r["facebook"]["handle"]
    p["github_handle"] = r["github"]["handle"]
    p["github_avatar"] = r["github"]["avatar"]
    p["github_company"] = r["github"]["company"]
    p["github_blog"] = r["github"]["blog"]
    p["github_followers"] = r["github"]["followers"]
    p["github_following"] = r["github"]["following"]
    p["twitter_handle"] = r["twitter"]["handle"]
    p["twitter_id"] = r["twitter"]["id"]
    p["twitter_bio"] = r["twitter"]["bio"]
    p["twitter_followers"] = r["twitter"]["followers"]
    p["twitter_following"] = r["twitter"]["following"]
    p["twitter_location"] = r["twitter"]["location"]
    p["twitter_site"] = r["twitter"]["site"]
    p["twitter_avatar"] = r["twitter"]["avatar"]
    p["linkedin_handle"] = r["linkedin"]["handle"]
    p["googleplus_handle"] = r["googleplus"]["handle"]
    p["gravatar_handle"] = r["gravatar"]["handle"]
    p["gravatar_url_titles"] = list()
    p["gravatar_urls"] = list()
    if r["gravatar"]["urls"] is not None:
        for d in r["gravatar"]["urls"]:
            try:
                p["gravatar_url_titles"].append(d["title"])
            except KeyError as e:
                p["gravatar_url_titles"].append(None)
            try:
                p["gravatar_urls"].append(d["value"])
            except KeyError as e:
                p["gravatar_urls"].append(None)

    if len(p["gravatar_url_titles"]) != 0:
        if None in p["gravatar_url_titles"]:
            p["gravatar_url_titles"] = \
                list(set(p["gravatar_url_titles"]))
            p["gravatar_url_titles"].remove(None)
            if len(p["gravatar_url_titles"]) != 0:
                p["gravatar_url_titles"] = " >>> ".join(
                    p["gravatar_url_titles"]
                )
            else:
                p["gravatar_url_titles"] = None
        else:
            p["gravatar_url_titles"] = " >>> ".join(
                p["gravatar_url_titles"]
            )
    else:
        p["gravatar_url_titles"] = None

    if len(p["gravatar_urls"]) != 0:
        if None in p["gravatar_urls"]:
            p["gravatar_urls"] = list(set(p["gravatar_urls"]))
            p["gravatar_urls"].remove(None)
            if len(p["gravatar_urls"]) != 0:
                p["gravatar_urls"] = " >>> ".join(
                    p["gravatar_urls"]
                )
            else:
                p["gravatar_urls"] = None
        else:
            p["gravatar_urls"] = " >>> ".join(
                p["gravatar_urls"]
            )
    else:
        p["gravatar_urls"] = None

    p["gravatar_avatar"] = r["gravatar"]["avatar"]
    p["gravatar_avatar_types"] = list()
    p["gravatar_avatar_urls"] = list()
    if len(r["gravatar"]["avatars"]) != 0:
        for d in r["gravatar"]["avatars"]:
            try:
                p["gravatar_avatar_types"].append(d["type"])
            except KeyError as e:
                p["gravatar_avatar_types"].append(None)
            try:
                p["gravatar_avatar_urls"].append(d["url"])
            except KeyError as e:
                p["gravatar_avatar_urls"].append(None)

    if len(p["gravatar_avatar_types"]) != 0:
        if None in p["gravatar_avatar_types"]:
            p["gravatar_avatar_types"] = \
                list(set(p["gravatar_avatar_types"]))
            p["gravatar_avatar_types"].remove(None)
            if len(p["gravatar_avatar_types"]) != 0:
                p["gravatar_avatar_types"] = " >>> ".join(
                    p["gravatar_avatar_types"]
                )
            else:
                p["gravatar_avatar_types"] = None
        else:
            p["gravatar_avatar_types"] = " >>> ".join(
                p["gravatar_avatar_types"]
            )
    else:
        p["gravatar_avatar_types"] = None

    if len(p["gravatar_avatar_urls"]) != 0:
        if None in p["gravatar_avatar_urls"]:
            p["gravatar_avatar_urls"] = \
                list(set(p["gravatar_avatar_urls"]))
            p["gravatar_avatar_urls"].remove(None)
            if len(p["gravatar_avatar_urls"]) != 0:
                p["gravatar_avatar_urls"] = " >>> ".join(
                    p["gravatar_avatar_urls"]
                )
            else:
                p["gravatar_avatar_urls"] = None
        else:
            p["gravatar_avatar_urls"] = " >>> ".join(
                p["gravatar_avatar_urls"]
            )
    else:
        p["gravatar_avatar_urls"] = None

    p["fuzzy_match"] = r["fuzzy"]
    p["is_email_provider"] = r["emailProvider"]
    return p


# TODO: can we abstract this to fit all cases (tags, tech, wp)
def make_clearbit_tags_payload(request=None):
    """Utility function that creates a payload for the Wordpress
    bucket."""
    print("make_clearbit_tags_payload()")
    print("request: {}".format(request))
    r = request.copy()
    p = MetadataMixin()

    p["refinery_company_id"] = r["refinery_company_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["ip_revealed"] = r["ip_revealed"]
    p["fuzzy_match"] = r["fuzzy_match"]
    p["tags"] = r["company"]["tags"]
    return p


# TODO: can we abstract this to fit all cases (tags, tech, wp)
def make_clearbit_tech_payload(request=None):
    """Utility function that creates a payload for the Wordpress
    bucket."""
    print("make_clearbit_tech_payload()")
    print("request: {}".format(request))
    r = request.copy()
    p = MetadataMixin()

    p["refinery_company_id"] = r["refinery_company_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["ip_revealed"] = r["ip_revealed"]
    p["fuzzy_match"] = r["fuzzy_match"]
    p["tech"] = r["company"]["tech"]
    return p


# TODO: can we abstract this to fit all cases (tags, tech, wp)
def make_clearbit_emails_payload(request=None):
    """Utility function that creates a payload for the Wordpress
    bucket."""
    print("make_clearbit_emails_payload()")
    print("request: {}".format(request))
    r = request.copy()
    p = MetadataMixin()

    p["refinery_company_id"] = r["refinery_company_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["ip_revealed"] = r["ip_revealed"]
    p["fuzzy_match"] = r["fuzzy_match"]
    p["emails"] = r["company"]["site"]["emailAddresses"]
    return p


# TODO: can we abstract this to fit all cases (tags, tech, wp)
def make_clearbit_phones_payload(request=None):
    """Utility function that creates a payload for the Wordpress
    bucket."""
    print("make_clearbit_phones_payload()")
    print("request: {}".format(request))
    r = request.copy()
    p = MetadataMixin()

    p["refinery_company_id"] = r["refinery_company_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["ip_revealed"] = r["ip_revealed"]
    p["fuzzy_match"] = r["fuzzy_match"]
    p["phones"] = r["company"]["site"]["phoneNumbers"]
    return p


def check_clearbit_rate_limit(response=None):
    """Determines whether we've exceeded the rate limit."""
    print("check_clearbit_rate_limit()")
    rate_limit = response.headers["x-ratelimit-limit"]
    remaining = response.headers["x-ratelimit-remaining"]
    reset_time = response.headers["x-ratelimit-reset"]

    rate_limit_exceeded = False

    if remaining == "0":
        rate_limit_exceeded = True

    print("rate limit exceeded: {}".format(rate_limit_exceeded))
    results = {
        "rate_limit_exceeded": rate_limit_exceeded,
        "reset_time": reset_time,
    }
    print(results)

    return results


def clearbit_routines(request=None, streaming=False):
    """Enrichment routines that wrap the Clearbit API."""
    print("clearbit_routines()")
    # TODO: add functionality to enable revealing and then enriching
    #  make the appropriate endpoint request
    # TODO: make sure to return the expected payload here

    for n in range(MAX_RETRIES):
        try:
            if request["clearbit_reveal"] is True:
                print("Reveal API")
                # ip_address = request["ip_address"]
                print("ip_address: {}".format(request["ip_address"]))

                # TODO: find out if there is a streaming endpoint for
                #  Reveal
                if streaming is True:
                    resp = requests.get(
                        url="https://reveal.clearbit.com/v1/companies"
                            "/find",
                        params={"ip": request["ip_address"]},
                        auth=(clearbit.key, ""),
                        headers={
                            "API-Version": "2018-03-28"
                        }
                    )
                else:
                    resp = requests.get(
                        url="https://reveal.clearbit.com/v1/companies"
                            "/find",
                        params={"ip": request["ip_address"]},
                        auth=(clearbit.key, ""),
                        headers={"API-Version": "2018-03-28"}
                    )
                # DEPRECATED
                # resp = clearbit.Reveal.find(ip=ip_address,
                #                             streaming=streaming)

                # rate limit check (we'll pause with this request to
                # control the flow of future requests
                results = check_clearbit_rate_limit(
                    response=resp
                )
                if results["rate_limit_exceeded"] is True:
                    reset_time = results["reset_time"]
                    current_time = time.time()
                    sleep_time = reset_time - current_time
                    if sleep_time < 0:
                        time.sleep(sleep_time + 1)
                        continue
                    else:
                        pass

                print("request sent")
                print("status: {}".format(resp))
                # 202 (async lookup; try again momentarily)
                if "pending" in resp.keys():
                    print("request is pending.")
                    time.sleep(SLEEP_LENGTH)
                    continue

                # 404
                if resp is None:
                    print("resp: {}".format(resp))
                    err = {
                        "error_message": "Person/Company Not Found",
                        "status_code": "404"
                    }
                    print(err)

                    # we still need to return the expected payload
                    resp = {
                        "error": "Person/Company Not Found",
                        "status": "404",
                        "company": None,
                        "person": None
                    }

                break
            elif request["clearbit_enrich"] is True:
                # TODO: NOTE: big "gotcha" here as the email address
                #  takes precedent over the domain if provided,
                #  so using something like
                #  jason.wolosonovich@infusionsoft.com with a domain
                #  of 'cxmybiz.com' will return person info on jason
                #  as well as company info on infusionsoft (instead
                #  of cxmybiz.com)
                print("Enrichment API")
                print("email_address: {}".format(request["email"]))
                params = {
                    "email": request["email"],
                    "domain": request["domain"]
                }

                # determine from the payload which endpoint to hit
                enrichment_api = "person" if request["email"] is not \
                                             None else "company"
                print("enrichment api: {}".format(enrichment_api))
                print("sending request")
                # TODO: implement manual streaming
                if streaming is True:
                    if enrichment_api == "person":
                        resp = requests.get(
                            url="https://person-stream.clearbit.com/v2"
                                "/combined/find",
                            params={**params},
                            auth=(clearbit.key, ""),
                            headers={
                                "API-Version": "2018-06-06"
                            }
                        )

                    elif enrichment_api == "company":
                        resp = requests.get(
                            url="https://company-stream.clearbit.com/v2"
                                "/companies/find",
                            params={**params},
                            auth=(clearbit.key, ""),
                            headers={
                                "API-Version": "2017-09-12"
                            }
                        )
                else:
                    if enrichment_api == "person":
                        resp = requests.get(
                            url="https://person.clearbit.com/v2/combined/find",
                            params={**params},
                            auth=(clearbit.key, ""),
                            headers={
                                "API-Version": "2018-06-06"
                            }
                        )
                    elif enrichment_api == "company":
                        resp = requests.get(
                            url="https://company.clearbit.com/v2/companies/find",
                            params={**params},
                            auth=(clearbit.key, ""),
                            headers={
                                "API-Version": "2017-09-12"
                            }
                        )

                    resp.raise_for_status()

                # rate limit check (we'll pause with this request to
                # control the flow of future requests
                results = check_clearbit_rate_limit(
                    response=resp
                )

                if results["rate_limit_exceeded"] is True:
                    reset_time = results["reset_time"]
                    current_time = time.time()
                    sleep_time = reset_time - current_time
                    if sleep_time < 0:
                        time.sleep(sleep_time + 1)
                        continue
                    else:
                        pass

                print("request sent")
                print("status: {}".format(resp))

                # 202 (async lookup; try again momentarily)
                if resp.status_code == 201 or resp.status_code == 202:
                    print("request is pending.")
                    time.sleep(SLEEP_LENGTH)
                    continue
                # if "pending" in resp.keys():
                #     print("request is pending.")
                #     time.sleep(SLEEP_LENGTH)
                #     continue

                # 404
                if resp is None:
                    print("resp: {}".format(resp))
                    err = {
                        "error_message": "Person/Company Not Found",
                        "status_code": "404"
                    }
                    print(err)

                    # we still need to return the expected payload
                    resp = {
                        "error": "Person/Company Not Found",
                        "status": "404",
                        "company": None,
                        "person": None
                    }
                break
            elif request["clearbit_reveal"] is False and request[
                "clearbit_enrich"] is False:
                print("either `clearbit_reveal` or `clearbit_enrich` "
                      "must be True")
                try:
                    r = requests.Response()
                    r.status_code = 422
                    r.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print("Unprocessable Entity, 422")
                    raise(requests.exceptions.HTTPError(e))
        except requests.exceptions.HTTPError as e:
            print(e)
            status = str(e.response.status_code)
            if status == "400":
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "Bad Request",
                        "status": "400",
                        "company": None,
                        "person": None
                    }
                    print(resp)
                    break
                continue
            if status == "401":
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "Invalid API Key",
                        "status": "401",
                        "company": None,
                        "person": None
                    }
                    print(resp)
                    break
                continue
            if status == "402":
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "Quota Exceeded",
                        "status": "402",
                        "company": None,
                        "person": None,
                        "quota_info": resp.headers
                    }
                    print(resp)
                    break
                continue
            if status == "404":
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "Person/Company Not Found",
                        "status": "404",
                        "company": None,
                        "person": None
                    }
                    print(resp)
                    break
                continue

            if status == "422":
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "Unprocessable Entity",
                        "status": "422",
                        "company": None,
                        "person": None
                    }
                    print(resp)
                    break
                continue
            elif status == "429":
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "Client Error: Too Many Requests",
                        "status": "429",
                        "company": None,
                        "person": None
                    }
                    print(resp)
                    break
                continue
            elif status[0] == "5":
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "Internal Server Error",
                        "status": "5xx",
                        "company": None,
                        "person": None
                    }
                    print(resp)
                    break
                continue
            else:
                if n == MAX_RETRIES - 1:
                    # we still need to return the expected payload
                    resp = {
                        "error": "{}".format(status),
                        "status": "{}".format(status),
                        "company": None,
                        "person": None
                    }
                    print(resp)
                    break
                continue
        except UnboundLocalError as e:
            print(e)
            if n == MAX_RETRIES - 1:
                resp = {
                    "error": "Person/Company Not Found",
                    "status": "404",
                    "company": None,
                    "person": None
                }
                print(resp)
                break
            continue
        # catch-all for python exceptions
        except Exception as e:
            print(e)
            if n == MAX_RETRIES - 1:
                resp = {
                    "error": "Person/Company Not Found",
                    "status": "404",
                    "company": None,
                    "person": None
                }
                print(resp)
                break
            continue          
    
        # TODO: this is really a 404 error but the clearbit
        # library makes it unclear that this is the case
        # ref: https://github.com/clearbit/clearbit-python/blob
        # /master/clearbit/resource.py
    try:
        if resp.status_code == 200 or resp.status_code == 201 or \
                resp.status_code == 202:
            resp = resp.json()
    except AttributeError as e:
        pass
    return resp
