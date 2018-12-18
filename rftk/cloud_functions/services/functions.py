"""
functions.py: Utility functions used throughout the services within the
              Refinery.
"""
from __future__ import print_function, division, unicode_literals, \
    absolute_import

import time
import re
import base64
import json

import requests
from google.cloud import pubsub
from google.cloud import bigquery as bq
import validators

from .crawler_service import HEADERS

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"


def upload_to_gcs(fs_client=None, payload=None, bucket_name=None,
                  file_name=None, file_suffix=None):
    """Utility function to upload the json to GCS."""
    # TODO: add `content_type` and `content_encoding` when they become
    #  available to the `metadata` kwarg
    print("upload_to_gcs()")

    try:
        with fs_client.open(bucket_name + "/" + file_name + file_suffix,
                     "w") as f:
            f.write(json.dumps(payload))
        print("payload: {}".format(payload))
        return "OK, 200"
    except Exception as e:
        err = {
            "error_message": e,
            "status_code": "error uploading to gcs."
        }
        print(err)

    # DEPRECATED
    # i = 0
    # while i < 7:
    #     try:
    #         client = storage.Client()
    #         bucket = client.get_bucket(bucket_name)
    #         blob = bucket.blob(file_name + file_suffix)
    #         blob.upload_from_string(
    #             json.dumps(
    #                 payload
    #             ),
    #             content_type="application/json"
    #         )
    #         print("payload: {}".format(payload))
    #         return "OK, 200"
    #
    #     # TODO: what should we do here?
    #     except Exception as e:
    #         i += 1
    #         err = {
    #             "error_message": e,
    #             "status_code": "error uploading to gcs."
    #         }
    #         print(err)
    #         continue
    return "SEE ERROR LOGS"


def download_from_gcs(fs_client=None, bucket_name=None,
                      project_name=None, file_name=None):
    """Utility function to upload the json to GCS."""
    print("download_from_gcs()")
    try:
        # return the payload as a byte string since we don't know what
        # native format it might be in
        payload = fs_client.cat(bucket_name + "/" + file_name)
        return payload

    except Exception as e:
        err = {
            "error_message": e,
            "status_code": "error uploading to gcs."
        }
        print(err)

    return "SEE ERROR LOGS"


    # # DEPRECATED
    # client = storage.Client()
    # bucket = client.get_bucket(bucket_name)
    # blob = bucket.blob(file_name)
    #
    # try:
    #     payload = json.loads(
    #         blob.download_as_string(
    #             client=client
    #         ),
    #         encoding="utf-8"
    #     )
    #
    #     print("payload: {}".format(payload))
    #     return payload
    #
    # # TODO: what should we do here?
    # except Exception as e:
    #     err = {
    #         "error_message": e,
    #         "status_code": "unknown"
    #     }
    #
    #     print(err)
    # return


def callback(future):
    """Callback function to ensure the future has completed."""
    message_id = future.result()
    print("message_id: {} received.".format(message_id))
    return "OK, 200"


def publish_to_endpoint(messages=None,
                        max_bytes=10000000,
                        max_latency=0.05, max_messages=1000,
                        delay_length_in_seconds=None):
    print("publish_to_endpoint()")
    messages_published = 0
    start = time.time()
    # apply the batch settings if specified
    batch_settings = pubsub.types.BatchSettings(
        max_bytes=max_bytes,
        max_latency=max_latency,
        max_messages=max_messages
    )
    pubsub_client = pubsub.PublisherClient(
        batch_settings=batch_settings
    )
    # TODO: find a universal way to encode the message so we don't
    #  have to write different decoding functions in the_refinery to
    #  deal with different publishers; this produces a dict,
    #  but product and marketing will be delivering different payloads
    n = 1
    if isinstance(messages, list):
        pass
    else:
        messages = [messages]
    for message in messages:
        byte_encoded_message = str.encode(
            json.dumps(
                message
            )
        )
        print("topic: {}".format(message["topic"]))
        topic = pubsub_client.topic_path("infusionsoft-looker-poc",
                                         message["topic"])
        future = pubsub_client.publish(topic,
                                       byte_encoded_message)

        # attach the callback
        future.add_done_callback(callback)

        # add some rate-limiting
        if delay_length_in_seconds is not None:
            if n % max_messages == 0:
                time.sleep(delay_length_in_seconds)

        # increment our counter
        n += 1
        messages_published += 1
        print("messages published: {}".format(messages_published))
        print("time elapsed (seconds): {0:.1f}"
              .format(time.time() - start))

    end = time.time()
    print("total publishing time: {0:.1f}".format((end - start) / 60.))
    return "OK, 200"


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
        print("domain is a valid url")
        url = domain
        # there are edge-cases where this will still pass
        try:
            resp = requests.get(url,
                                headers=HEADERS)
            print("status code: {}".format(resp.status_code))
            # one last check for status
            if resp.status_code != 200:
                print("could not get url: {}".format(url))
                url = None
        except requests.exceptions.HTTPError as e:
            url = None
        except Exception as e:
            url = None

    # validation failed
    else:
        # check to see if it is a valid domain that we can use to
        # construct a url from
        is_valid_domain = validators.domain(domain)
        print("is_valid_domain: {}".format(is_valid_domain))
        # we can't construct a valid url without a valid domain
        if is_valid_domain is not True:
            print("domain is not valid")
            url = None
        else:
            # try to construct a valid url
            if domain.lower().startswith("www."):
                url = "http://" + domain.lower()
            else:
                url = "http://www." + domain.lower()
            print("constructed url: {}".format(url))

            # one more validation check then try to open the url
            is_valid_url = validators.url(url)

            print("is_valid_url: {}".format(is_valid_url))
            # now try to open the url as a final check
            try:
                resp = requests.get(url,
                                    headers=HEADERS)
                print("status code: {}".format(resp.status_code))
                # one last check for status
                if resp.status_code != 200:
                    print("could not get url: {}".format(url))
                    # try https then
                    # try to construct a valid url
                    print("trying https instead")
                    if domain.lower().startswith("www."):
                        url = "https://" + domain.lower()
                    else:
                        url = "https://www." + domain.lower()
                    try:
                        resp = requests.get(url,
                                            headers=HEADERS)
                        print("status code: {}"
                              .format(resp.status_code))
                        if resp.status_code != 200:
                            print("could not get https url: {}"
                                  .format(url))
                            url = None
                    except requests.exceptions.HTTPError as e:
                        url = None
                    except Exception as e:
                        url = None
            except requests.exceptions.HTTPError as e:
                url = None
            except Exception as e:
                url = None
    return url


def is_valid_email(email=None):
    """Validates whether the email provided is syntactically correct."""
    # source: https://stackoverflow.com/questions/201323/how-to-validate-an-email-address-using-a-regular-expression
    # TODO: implement the python equivalent of the state machine
    #  found here: https://github.com/cubiclesoft/ultimate-email
    r = re.compile(
        """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    )
    try:
        is_valid = False if re.match(r, email) is None else True
    except Exception as e:
        print(e)
        is_valid = False
    return is_valid


def get_domain_from_email(email=None):
    """Returns the domain from the provided email address."""
    r = re.compile(
        """^(.*@)([\w.]+)"""
    )
    try:
        domain = re.match(r, email).group(2)
        print("domain: {}".format(domain))
    except Exception as e:
        print(e)
        domain = None
    return domain


def insert_one_to_bq(bq_client=None, dataset=None, table=None,
                     schema=None, payload=None, payload_type=None):
    """Utility function for inserting json rows into the specified
    table."""
    print("insert_one_to_bq()")

    # when an email/domain fails to be enriched we'll keep track
    if payload_type == "error_lookup":
        print("inserting enrichment errors.")
        row = [
            (
                payload["refined_at"],
                payload["refined_date"],
                payload["sfdc_lead_id"],
                payload["sfdc_contact_id"],
                payload["sfdc_asset_id"],
                payload["sfdc_oppty_id"],
                payload["sfdc_acct_id"],
                payload["app_name"],
                payload["domain"],
                payload["email"]
            )
        ]


    if payload_type == "mobile":
        print("inserting mobile test results.")
        row = [
            (
                payload["refinery_company_id"],
                payload["refined_at"],
                payload["refined_date"],
                payload["domain"],
                payload["url"],
                payload["ip_revealed"],
                payload["fuzzy_match"],
                payload["test_results"]
            )
        ]

    if payload_type == "crawler":
        print("inserting crawler results.")
        row = [
            (
                payload["refinery_company_id"],
                payload["refined_at"],
                payload["refined_date"],
                payload["refinery_person_id"],
                payload["sfdc_lead_id"],
                payload["sfdc_contact_id"],
                payload["sfdc_asset_id"],
                payload["sfdc_oppty_id"],
                payload["sfdc_acct_id"],
                payload["app_name"],
                payload["domain"],
                payload["url"],
                payload["ip_revealed"],
                payload["fuzzy_match"],
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

    if payload_type == "person":
        print("inserting clearbit person results.")
        row = [
            (
                payload["refinery_person_id"],
                payload["refined_at"],
                payload["refined_date"],
                payload["refinery_company_id"],
                payload["sfdc_lead_id"],
                payload["sfdc_contact_id"],
                payload["sfdc_asset_id"],
                payload["sfdc_oppty_id"],
                payload["sfdc_acct_id"],
                payload["app_name"],
                payload["domain"],
                payload["url"],
                payload["ip_revealed"],
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

    if payload_type == "company":
        print("inserting clearbit company results.")
        row = [
            (
                payload["refinery_company_id"],
                payload["refined_at"],
                payload["refined_date"],
                payload["refinery_person_id"],
                payload["sfdc_lead_id"],
                payload["sfdc_contact_id"],
                payload["sfdc_asset_id"],
                payload["sfdc_oppty_id"],
                payload["sfdc_acct_id"],
                payload["app_name"],
                payload["domain"],
                payload["url"],
                payload["ip_address"],
                payload["ip_revealed"],
                payload["clearbit_company_id"],
                payload["clearbit_indexed_at"],
                payload["company_name"],
                payload["legal_name"],
                payload["company_domain"],
                payload["domain_aliases"],
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
                payload["fuzzy_match"],
                payload["is_email_provider"]

            )
        ]

    if payload_type == "wp_lookup_error":
        print("updating wp plugin error table.")
        row = [
            (
                payload["plugin"],
                payload["refined_at"],
                payload["refined_date"]
            )
        ]

    if payload_type == "ip_lookup":
        print("adding row to ip lookup table.")
        row = [
            (
                payload["refined_at"],
                payload["refined_date"],
                payload["ip_address"],
                payload["reason"],
                payload["source"]
            )
        ]

    max_retries = 7
    for n in range(max_retries):
        try:
            # configs for bq

            # job_config = bq.LoadJobConfig()
            # job_config.schema = schema
            # job_config.source_format = \
            #     bq.job.SourceFormat.NEWLINE_DELIMITED_JSON
            # job_config.write_disposition = \
            #     bq.job.WriteDisposition.WRITE_APPEND

            dataset_ref = bq_client.dataset(dataset)
            dataset = bq.Dataset(dataset_ref)
            table_ref = dataset.table(table)
            table = bq.Table(table_ref,
                             schema=schema)

            print("dataset: {}".format(dataset))
            print("table: {}".format(table))
            print("schema: {}".format(schema))
            print("payload: {}".format(payload))
            print("payload type: {}".format(payload_type))

            # attempt to insert the record
            errors = bq_client.insert_rows(
                table,
                row,
                selected_fields=schema,

            )

            if len(errors) != 0:
                print(errors)
                continue
            success = True
            break
        except Exception as e:
            if n == max_retries - 1:
                print(e)
                success = False
                break
            time.sleep(2 ** n)
            continue
    return "success: {}".format(success)


def insert_many_to_bq(bq_client=None, dataset=None, table=None,
                      schema=None, payload=None, payload_type=None):
    """Utility function for inserting json rows into the specified
    table."""
    print("insert_many_to_bq()")

    # configs for bq
    # client = bq.Client()
    # job_config = bq.LoadJobConfig()
    # job_config.schema = schema
    # job_config.source_format = \
    #     bq.job.SourceFormat.NEWLINE_DELIMITED_JSON
    # job_config.write_disposition = \
    #     bq.job.WriteDisposition.WRITE_APPEND

    dataset_ref = bq_client.dataset(dataset)
    dataset = bq.Dataset(dataset_ref)
    table_ref = dataset.table(table)
    table = bq.Table(table_ref,
                     schema=schema)

    print("dataset: {}".format(dataset))
    print("table: {}".format(table))
    print("schema: {}".format(schema))
    print("payload: {}".format(payload))
    print("payload type: {}".format(payload_type))

    if payload_type == "crawler_tech":
        keys = payload.keys()
        if "wp_themes" in keys:
            print("inserting themes.")
            for theme in payload["wp_themes"]:
                row = [
                    (
                        payload["refinery_company_id"],
                        payload["refined_at"],
                        payload["refined_date"],
                        payload["domain"],
                        payload["url"],
                        payload["ip_revealed"],
                        payload["fuzzy_match"],
                        theme,
                        "theme",
                        "wordpress"
                    )
                ]

                max_retries = 7
                for n in range(max_retries):
                    try:
                        # attempt to insert the record
                        errors = bq_client.insert_rows(
                            table,
                            row,
                            selected_fields=schema,

                        )

                        if len(errors) != 0:
                            print(errors)
                            continue
                        success = True
                        break
                    except Exception as e:
                        if n == max_retries - 1:
                            print(e)
                            success = False
                            break
                        time.sleep(2 ** n)
                        continue

        if "wp_plugins" in keys:
            print("inserting plugins.")
            for plugin in payload["wp_plugins"]:
                row = [
                    (
                        payload["refinery_company_id"],
                        payload["refined_at"],
                        payload["refined_date"],
                        payload["domain"],
                        payload["url"],
                        payload["ip_revealed"],
                        payload["fuzzy_match"],
                        plugin,
                        "plugin",
                        "wordpress"
                    )
                ]

                max_retries = 7
                for n in range(max_retries):
                    try:
                        # attempt to insert the record
                        errors = bq_client.insert_rows(
                            table,
                            row,
                            selected_fields=schema,

                        )

                        if len(errors) != 0:
                            print(errors)
                            continue
                        success = True
                        break
                    except Exception as e:
                        if n == max_retries - 1:
                            print(e)
                            success = False
                            break
                        time.sleep(2 ** n)
                        continue

    if payload_type == "clearbit_emails":
        for email in payload["emails"]:
            print("inserting emails.")
            row = [
                (
                    payload["refinery_company_id"],
                    payload["refined_at"],
                    payload["refined_date"],
                    payload["domain"],
                    payload["url"],
                    payload["ip_revealed"],
                    payload["fuzzy_match"],
                    email
                )
            ]

            max_retries = 7
            for n in range(max_retries):
                try:
                    # attempt to insert the record
                    errors = bq_client.insert_rows(
                        table,
                        row,
                        selected_fields=schema,

                    )

                    if len(errors) != 0:
                        print(errors)
                        continue
                    success = True
                    break
                except Exception as e:
                    if n == max_retries - 1:
                        print(e)
                        success = False
                        break
                    time.sleep(2 ** n)
                    continue

    if payload_type == "clearbit_phones":
        for phone in payload["phones"]:
            print("inserting phones.")
            row = [
                (
                    payload["refinery_company_id"],
                    payload["refined_at"],
                    payload["refined_date"],
                    payload["domain"],
                    payload["url"],
                    payload["ip_revealed"],
                    payload["fuzzy_match"],
                    phone
                )
            ]
            max_retries = 7
            for n in range(max_retries):
                try:
                    # attempt to insert the record
                    errors = bq_client.insert_rows(
                        table,
                        row,
                        selected_fields=schema,

                    )

                    if len(errors) != 0:
                        print(errors)
                        continue
                    success = True
                    break
                except Exception as e:
                    if n == max_retries - 1:
                        print(e)
                        success = False
                        break
                    time.sleep(2 ** n)
                    continue

    if payload_type == "clearbit_tags":
        for tag in payload["tags"]:
            print("inserting tags.")
            row = [
                (
                    payload["refinery_company_id"],
                    payload["refined_at"],
                    payload["refined_date"],
                    payload["domain"],
                    payload["url"],
                    payload["ip_revealed"],
                    payload["fuzzy_match"],
                    tag
                )
            ]

            max_retries = 7
            for n in range(max_retries):
                try:
                    # attempt to insert the record
                    errors = bq_client.insert_rows(
                        table,
                        row,
                        selected_fields=schema,

                    )

                    if len(errors) != 0:
                        print(errors)
                        continue
                    success = True
                    break
                except Exception as e:
                    if n == max_retries - 1:
                        print(e)
                        success = False
                        break
                    time.sleep(2 ** n)
                    continue

    if payload_type == "clearbit_tech":
        for tech in payload["tech"]:
            print("inserting tech.")
            row = [
                (
                    payload["refinery_company_id"],
                    payload["refined_at"],
                    payload["refined_date"],
                    payload["domain"],
                    payload["url"],
                    payload["ip_revealed"],
                    payload["fuzzy_match"],
                    tech
                )
            ]

            max_retries = 7
            for n in range(max_retries):
                try:
                    # attempt to insert the record
                    errors = bq_client.insert_rows(
                        table,
                        row,
                        selected_fields=schema,

                    )

                    if len(errors) != 0:
                        print(errors)
                        continue
                    success = True
                    break
                except Exception as e:
                    if n == max_retries - 1:
                        print(e)
                        success = False
                        break
                    time.sleep(2 ** n)
                    continue

    if payload_type == "wp_lookup":
        print("updating wp plugin lookup table.")
        for tag in payload["tags"]:
            row = [
                (
                    payload["plugin"],
                    payload["refined_at"],
                    payload["refined_date"],
                    payload["name"],
                    tag,
                    payload["description"]
                )
            ]

            max_retries = 7
            for n in range(max_retries):
                try:
                    # attempt to insert the record
                    errors = bq_client.insert_rows(
                        table,
                        row,
                        selected_fields=schema,

                    )

                    if len(errors) != 0:
                        print(errors)
                        continue
                    success = True
                    break
                except Exception as e:
                    if n == max_retries - 1:
                        print(e)
                        success = False
                        break
                    time.sleep(2 ** n)
                    continue

    if payload_type == "email_provider":
        print("inserting email provider lookup results.")
        for email_provider, mx_record in zip(
                payload["email_providers"], payload["mx_records"]):
            row = [
                (
                    payload["refinery_company_id"],
                    payload["refined_at"],
                    payload["refined_date"],
                    payload["domain"],
                    mx_record,
                    email_provider
                )
            ]

            max_retries = 7
            for n in range(max_retries):
                try:
                    # attempt to insert the record
                    errors = bq_client.insert_rows(
                        table,
                        row,
                        selected_fields=schema,

                    )

                    if len(errors) != 0:
                        print(errors)
                        continue
                    success = True
                    break
                except Exception as e:
                    if n == max_retries - 1:
                        print(e)
                        success = False
                        break
                    time.sleep(2 ** n)
                    continue

    return "success: {}".format(success)
