"""
functions.py: Utility functions used throughout the services within the
              Refinery.
"""

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

import base64
import json
import requests

from google.cloud import storage, pubsub
from google.cloud import bigquery as bq
import validators


def upload_to_gcs(payload=None, bucket_name=None, file_name=None,
                  file_suffix=None):
    """Utility function to upload the json to GCS."""
    print("upload_to_gcs()")
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name + file_suffix)

    try:
        blob.upload_from_string(
            json.dumps(
                payload
            ),
            content_type="application/json"
        )
        print("payload: {}".format(payload))
        return payload

    # TODO: what should we do here?
    except Exception as e:
        err = {
            "error_message": e,
            "status_code": "unknown"
        }

    print(err)


def publish_to_endpoint(topic, message):
    print("publish_to_endpoint()")
    pubsub_client = pubsub.PublisherClient()
    # TODO: find a universal way to encode the message so we don't
    #  have to write different decoding functions in the_refinery to
    #  deal with different publishers; this produces a dict,
    #  but product and marketing will be delivering different payloads
    byte_encoded_message = str.encode(
        json.dumps(
            message
        )
    )
    print("topic: {}".format(topic))
    topic = pubsub_client.topic_path("infusionsoft-looker-poc",
                                     topic)
    resp = pubsub_client.publish(topic,
                                 byte_encoded_message)


def decode_event(event):
    """Utility function for decoding the request."""
    # decode the message string
    print("decode_event()")
    request = base64.b64decode(
        event["data"]
    ).decode(
        'utf-8'
    )
    # TODO: see if there is some in-built way in flask to handle all
    #  this in a one-liner
    # convert the message string to a dict
    request = json.loads(request)
    print("event: {}".format(request))
    return request


def get_service_params(request=None):
    """Utility function to find the publisher, services and urls of the
    services to be used."""
    print("get_service_params()")
    # lookup dictionary
    service_lookup = {
        "analytics": {
            "clearbit_service":
                "https://us-central1-infusionsoft-looker-poc"
                ".cloudfunctions.net/the_refinery_clearbit_service",
            "crawler_service":
                "https://us-central1-infusionsoft-looker-poc"
                ".cloudfunctions.net/the_refinery_crawler_service"
        },
        "product": None,
        "marketing": None
    }

    publisher = request["publisher"]
    services = request["services_requested"]
    service_urls = [service_lookup[publisher][service]
                    for service in services]
    return publisher, services, service_urls


def get_valid_url(domain=None):
    """Utility function that produces (when possible) a valid url
    from a domain name."""
    # TODO: add more robust exception handling
    print("get_valid_url()")
    # NOTE: probably not robust to edge-cases
    # this may already be a valid url
    is_valid_url = validators.url(domain)

    if is_valid_url is True:
        url = domain
        # there are edge-cases where this will still pass
        try:
            resp = requests.get(url)
            # one last check for status
            if resp.status_code != 200:
                url = "the_supplied_domain_is_invalid"
        except requests.exceptions.HTTPError as e:
            url = "the_supplied_domain_is_invalid"
        except Exception as e:
            url = "the_supplied_domain_is_invalid"

    # validation failed
    else:
        # check to see if it is a valid domain that we can use to
        # construct a url from
        is_valid_domain = validators.domain(domain)
        # we can't construct a valid url without a valid domain
        if is_valid_domain is not True:
            url = "the_supplied_domain_is_invalid"
        else:
            # try to construct a valid url
            if domain.lower().startswith("www."):
                url = "http://" + domain.lower()
            else:
                url = "http://www." + domain.lower()

            # one more validation check then try to open the url
            is_valid_url = validators.url(url)
            if is_valid_url is not True:
                url = "the_supplied_domain_is_invalid"

            # now try to open the url as a final check
            try:
                resp = requests.get(url)
                # one last check for status
                if resp.status_code != 200:
                    url = "the_supplied_domain_is_invalid"
            except requests.exceptions.HTTPError as e:
                url = "the_supplied_domain_is_invalid"
            except Exception as e:
                url = "the_supplied_domain_is_invalid"
    return url


def download_from_gcs(bucket_name=None, file_name=None):
    """Utility function to upload the json to GCS."""
    print("download_from_gcs()")
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        payload = json.loads(
            blob.download_as_string(
                client=client
            ),
            encoding="utf-8"
        )

        print("payload: {}".format(payload))
        return payload

    # TODO: what should we do here?
    except Exception as e:
        err = {
            "error_message": e,
            "status_code": "unknown"
        }

        print(err)


def insert_bq_row(dataset=None, table=None, schema=None,
                  payload=None, payload_type=None):
    """Utility function for inserting json rows into the specified
    table."""
    print("insert_bq_row()")
    # configs for bq
    client = bq.Client()
    job_config = bq.LoadJobConfig()
    job_config.schema = schema
    job_config.source_format = \
        bq.job.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.write_disposition = bq.job.WriteDisposition.WRITE_APPEND

    dataset_ref = client.dataset(dataset)
    dataset = bq.Dataset(dataset_ref)
    table_ref = dataset.table(table)
    table = bq.Table(table_ref,
                     schema=schema)

    print("dataset: {}".format(dataset))
    print("table: {}".format(table))
    print("schema: {}".format(schema))
    print("payload: {}".format(payload))
    print("payload type: {}".format(payload_type))

    # get the static identifying properties
    refinery_id = payload["refinery_id"]
    refined_at = payload["refined_at"]
    refined_date = payload["refined_date"]
    domain = payload["domain"]
    url = payload["url"]

    if payload_type == "crawler_tech":
        keys = payload.keys()
        if "wp_themes" in keys:
            print("inserting themes.")
            for theme in payload["wp_themes"]:
                row = [
                    (
                        refinery_id,
                        refined_at,
                        refined_date,
                        domain,
                        url,
                        theme,
                        "theme"
                    )
                ]

                errors = client.insert_rows(
                    table,
                    row,
                    selected_fields=schema
                )
                if len(errors) != 0:
                    print(errors)

        if "wp_plugins" in keys:
            print("inserting plugins.")
            for plugin in payload["wp_plugins"]:
                row = [
                    (
                        refinery_id,
                        refined_at,
                        refined_date,
                        domain,
                        url,
                        plugin,
                        "plugin"
                    )
                ]

                errors = client.insert_rows(
                    table,
                    row,
                    selected_fields=schema
                )

                if len(errors) != 0:
                    print(errors)

    if payload_type == "tags":
        for tag in payload["tags"]:
            print("inserting tags.")
            row = [
                (
                    refinery_id,
                    refined_at,
                    refined_date,
                    domain,
                    url,
                    tag
                )
            ]

            errors = client.insert_rows(
                table,
                row,
                selected_fields=schema
            )

            if len(errors) != 0:
                print(errors)

    if payload_type == "tech":
        for tech in payload["tech"]:
            print("inserting tech.")
            row = [
                (
                    refinery_id,
                    refined_at,
                    refined_date,
                    domain,
                    url,
                    tech
                )
            ]

            errors = client.insert_rows(
                table,
                row,
                selected_fields=schema
            )

            if len(errors) != 0:
                print(errors)

    if payload_type == "mobile":
        print("inserting mobile test results.")
        row = [
            (
                refinery_id,
                refined_at,
                refined_date,
                domain,
                url,
                payload["test_results"]
            )
        ]

        errors = client.insert_rows(
            table,
            row,
            selected_fields=schema
        )

        if len(errors) != 0:
            print(errors)

    if payload_type == "crawler":
        print("inserting crawler results.")
        row = [
            (
                refinery_id,
                refined_at,
                refined_date,
                payload["sfdc_lead_id"],
                payload["sfdc_contact_id"],
                domain,
                url,
                payload["all_links"],
                payload["internal_links"],
                payload["external_links"],
                payload["href_emails"],
                payload["href_phones"],
                payload["href_socials"],
                payload["meta_keywords"],
                payload["meta_description"],
                payload["tier1_classification"],
                payload["tier2_classification"],
                payload["tier3_classification"],
                payload["classification_confidence"],
                payload["html_string"]
            )
        ]

        errors = client.insert_rows(
            table,
            row,
            selected_fields=schema
        )

        if len(errors) != 0:
            print(errors)

    if payload_type == "person":
        print("inserting clearbit person results.")
        row = [
            (
                refinery_id,
                refined_at,
                refined_date,
                payload["sfdc_lead_id"],
                payload["sfdc_contact_id"],
                domain,
                url,
                payload["clearbit_person_id"],
                payload["clearbit_indexed_at"],
                payload["full_name"],
                payload["first_name"],
                payload["last_name"],
                payload["email"],
                payload["location"],
                payload["time_zone"],
                payload["utc_offset"],
                payload["city"],
                payload["state"],
                payload["state_code"],
                payload["country"],
                payload["country_code"],
                payload["latitude"],
                payload["longitude"],
                payload["bio"],
                payload["site"],
                payload["avatar"],
                payload["employment_domain"],
                payload["employment_name"],
                payload["employment_title"],
                payload["employment_role"],
                payload["employment_seniority"],
                payload["facebook_handle"],
                payload["github_handle"],
                payload["github_avatar"],
                payload["github_company"],
                payload["github_blog"],
                payload["github_followers"],
                payload["github_following"],
                payload["twitter_handle"],
                payload["twitter_id"],
                payload["twitter_bio"],
                payload["twitter_followers"],
                payload["twitter_following"],
                payload["twitter_location"],
                payload["twitter_site"],
                payload["twitter_avatar"],
                payload["linkedin_handle"],
                payload["googleplus_handle"],
                payload["gravatar_handle"],
                payload["gravatar_url_titles"],
                payload["gravatar_urls"],
                payload["gravatar_avatar"],
                payload["gravatar_avatar_types"],
                payload["gravatar_avatar_urls"],
                payload["fuzzy_match"],
                payload["is_email_provider"],

            )
        ]

        errors = client.insert_rows(
            table,
            row,
            selected_fields=schema
        )

        if len(errors) != 0:
            print(errors)

    if payload_type == "company":
        print("inserting clearbit company results.")
        row = [
            (
                refinery_id,
                refined_at,
                refined_date,
                payload["sfdc_lead_id"],
                payload["sfdc_contact_id"],
                domain,
                url,
                payload["clearbit_company_id"],
                payload["clearbit_indexed_at"],
                payload["company_name"],
                payload["legal_name"],
                payload["company_domain"],
                payload["domain_aliases"],
                payload["phone_numbers"],
                payload["email_addresses"],
                payload["industry"],
                payload["industry_group"],
                payload["sub_industry"],
                payload["sector"],
                payload["sic_code"],
                payload["naics_code"],
                payload["description"],
                payload["year_founded"],
                payload["location"],
                payload["street_number"],
                payload["street_name"],
                payload["sub_premise"],
                payload["city"],
                payload["state"],
                payload["state_code"],
                payload["postal_code"],
                payload["country"],
                payload["country_code"],
                payload["latitude"],
                payload["longitude"],
                payload["time_zone"],
                payload["utc_offset"],
                payload["company_phone"],
                payload["number_of_employees"],
                payload["number_of_employees_range"],
                payload["fiscal_year_ends"],
                payload["market_cap"],
                payload["total_raised"],
                payload["company_type"],
                payload["ticker_symbol"],
                payload["tax_ein"],
                payload["annual_revenue"],
                payload["estimated_annual_revenue"],
                payload["company_logo"],
                payload["crunchbase_handle"],
                payload["alexa_us_rank"],
                payload["alexa_global_rank"],
                payload["parent_domain"],
                payload["facebook_handle"],
                payload["facebook_likes"],
                payload["linkedin_handle"],
                payload["twitter_handle"],
                payload["twitter_avatar"],
                payload["twitter_bio"],
                payload["twitter_follower_count"],
                payload["twitter_following_count"],
                payload["twitter_id"],
                payload["twitter_location"],
                payload["twitter_site_url"],
                payload["is_email_provider"]

            )
        ]

        errors = client.insert_rows(
            table,
            row,
            selected_fields=schema
        )

        if len(errors) != 0:
            print(errors)
