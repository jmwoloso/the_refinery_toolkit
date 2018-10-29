"""
clearbit_service.py: Utility functions used by the clearbit service.
"""

__author__ = "jason wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

import os
import base64

import googleapiclient.discovery
from google.cloud import storage
import clearbit

from .classes import MemoryCache, MetadataMixin


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


def get_service_configs(service=None):
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

            # set clearbit api versions
            clearbit.Person.version = "2018-06-06"
            clearbit.Company.version = "2017-09-12"
            clearbit.Reveal.version = "2018-03-28"
            # not in use
            clearbit.Watchlist.version = "2015-11-13"
            # not in use
            clearbit.Prospector.version = "2016-10-04"

            # download the file as a string in-memory
            st_client = storage.Client()
            bucket = st_client.get_bucket(BUCKET_NAME)
            cipher_blob = bucket.blob(CIPHERTEXT_BLOB)
            cipher_string = cipher_blob.download_as_string()

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
        pass


def make_clearbit_company_gcs_payload(request=None):
    """Utility function to flatten and parse the fields we need in
    BQ."""
    print("make_clearbit_company_gcs_payload()")
    r = request["company"].copy()
    p = MetadataMixin()

    # add the metadata we injected to the request along the way
    p["refinery_id"] = request["refinery_id"]
    p["refined_at"] = request["refined_at"]
    p["refined_date"] = request["refined_date"]
    p["sfdc_lead_id"] = request["sfdc_lead_id"]
    p["sfdc_contact_id"] = request["sfdc_contact_id"]
    p["sfdc_account_id"] = request["sfdc_account_id"]
    p["sfdc_asset_id"] = request["sfdc_asset_id"]
    p["netsuite_contract_id"] = request["netsuite_contract_id"]
    p["marketo_lead_id"] = request["marketo_lead_id"]
    p["heap_id"] = request["heap_id"]
    p["amplitude_id"] = request["amplitude_id"]
    p["tealium_id"] = request["tealium_id"]
    p["cas_id"] = request["cas_id"]
    p["app_name"] = request["app_name"]
    p["url"] = request["url"]
    p["domain"] = request["domain"]

    # add the company data returned by clearbit
    p["clearbit_company_id"] = r["id"]
    p["company_name"] = r["name"]
    p["legal_name"] = r["legalName"]
    p["company_domain"] = r["domain"]
    p["domain_aliases"] = r["domainAliases"]

    # site
    p["phone_numbers"] = r["site"]["phoneNumbers"]
    p["email_addresses"] = r["site"]["emailAddresses"]

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

    p["logo"] = r["logo"]

    # fakebook
    p["facebook_handle"] = r["facebook"]["handle"]

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
    p["twitter_site"] = r["twitter"]["site"]
    p["twitter_avatar"] = r["twitter"]["avatar"]

    # crunchbase
    p["crunchbase_handle"] = r["crunchbase"]["handle"]

    p["is_email_provider"] = r["emailProvider"]
    p["company_type"] = r["type"]
    p["ticker_symbol"] = r["ticker"]
    p["us_ein"] = r["identifiers"]["usEIN"]
    p["phone"] = r["phone"]
    p["clearbit_indexed_at"] = r["indexedAt"]

    # metrics
    p["alexa_us_rank"] = r["metrics"]["alexaUsRank"]
    p["alexa_global_rank"] = r["metrics"]["alexaGlobalRank"]
    p["employees"] = r["metrics"]["employees"]
    p["employees_range"] = r["metrics"]["employeesRange"]
    p["market_cap"] = r["metrics"]["marketCap"]
    p["raised_funding"] = r["metrics"]["raised"]
    p["annual_revenue"] = r["metrics"]["annualRevenue"]
    p["estimated_annual_revenue"] = r["metrics"][
        "estimatedAnnualRevenue"]
    p["fiscal_year_end"] = r["metrics"]["fiscalYearEnd"]

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
    p["refinery_id"] = request["refinery_id"]
    p["refined_at"] = request["refined_at"]
    p["refined_date"] = request["refined_date"]
    p["sfdc_lead_id"] = request["sfdc_lead_id"]
    p["sfdc_contact_id"] = request["sfdc_contact_id"]
    p["sfdc_account_id"] = request["sfdc_account_id"]
    p["sfdc_asset_id"] = request["sfdc_asset_id"]
    p["netsuite_contract_id"] = request["netsuite_contract_id"]
    p["marketo_lead_id"] = request["marketo_lead_id"]
    p["heap_id"] = request["heap_id"]
    p["amplitude_id"] = request["amplitude_id"]
    p["tealium_id"] = request["tealium_id"]
    p["cas_id"] = request["cas_id"]
    p["app_name"] = request["app_name"]
    p["url"] = request["url"]
    p["domain"] = request["domain"]

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
    if len(r["gravatar"]["urls"]) != 0:
        for d in r["gravatar"]["urls"]:
            p["gravatar_url_titles"].append(d["value"])
            p["gravatar_urls"].append(d["title"])
    p["gravatar_avatar"] = r["gravatar"]["avatar"]
    p["gravatar_avatar_types"] = list()
    p["gravatar_avatar_urls"] = list()
    if len(r["gravatar"]["avatars"]) != 0:
        for d in r["gravatar"]["avatars"]:
            p["gravatar_avatar_types"].append(d["type"])
            p["gravatar_avatar_urls"].append(d["url"])

    p["fuzzy_match"] = r["fuzzy"]
    p["is_email_provider"] = r["emailProvider"]
    return p


# TODO: can we abstract this to fit all cases (tags, tech, wp)
def make_tags_payload(request=None):
    """Utility function that creates a payload for the Wordpress
    bucket."""
    print("make_tags_payload()")
    r = request.copy()
    p = MetadataMixin()

    p["refinery_id"] = r["refinery_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["tags"] = r["company"]["tags"]
    return p


# TODO: can we abstract this to fit all cases (tags, tech, wp)
def make_tech_payload(request=None):
    """Utility function that creates a payload for the Wordpress
    bucket."""
    print("make_tech_payload()")
    r = request.copy()
    p = MetadataMixin()

    p["refinery_id"] = r["refinery_id"]
    p["refined_at"] = r["refined_at"]
    p["refined_date"] = r["refined_date"]
    p["domain"] = r["domain"]
    p["url"] = r["url"]
    p["tech"] = r["company"]["tech"]
    return p
