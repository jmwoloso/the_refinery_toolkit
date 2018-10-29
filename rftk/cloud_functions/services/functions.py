"""
functions.py: Utility functions used throughout the services within the
              Refinery.
"""

__author__ = "jason wolosonovich <jason@avaland.io>"
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
    # TODO: what should we do here?
    except Exception as e:
        pass


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

        return payload

    # TODO: what should we do here?
    except Exception as e:
        pass


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

    # try to create the table if it doesn't exist
    # try:
    #     table = client.create_table(table)
    #     print("creating table.")
    # except exceptions.Conflict as e:
    #     print("table exists.")
    # TODO: update the logic in this as it evolves for clearbit stuff

    # get the static identifying properties
    refinery_id = payload["refinery_id"]
    refined_at = payload["refined_at"]
    refined_date = payload["refined_date"]
    domain = payload["domain"]
    url = payload["url"]

    if payload_type == "wp":
        if len(payload["wp_themes"]) != 0:
            for theme in payload["wp_themes"]:
                row = [
                    [
                        refinery_id,
                        refined_at,
                        refined_date,
                        domain,
                        url,
                        theme,
                        "theme"
                    ]
                ]

                errors = client.create_rows(
                    table=table,
                    rows=row,
                    selected_fields=schema
                )
                # newer versions of the library
                # errors = bq_client.insert_rows(
                #     table,
                #     row,
                #     selected_fields=schema
                # )
                if len(errors) != 0:
                    print(errors)

        if len(payload["wp_plugins"]) != 0:
            for plugin in payload["wp_plugins"]:
                row = [
                    [
                        refinery_id,
                        refined_at,
                        refined_date,
                        domain,
                        url,
                        plugin,
                        "plugin"
                    ]
                ]

                errors = client.create_rows(
                    table=table,
                    rows=row,
                    selected_fields=schema
                )

                # # newer versions of the library
                # errors = client.insert_rows(
                #     table,
                #     row,
                #     selected_fields=schema
                # )

                if len(errors) != 0:
                    print(errors)

    if payload_type == "tags":
        for tag in payload["tags"]:
            row = [
                [
                    refinery_id,
                    refined_at,
                    refined_date,
                    domain,
                    url,
                    tag
                ]
            ]

            errors = client.create_rows(
                table=table,
                rows=row,
                selected_fields=schema
            )

            # # newer versions of the library
            # errors = client.insert_rows(
            #     table,
            #     row,
            #     selected_fields=schema
            # )

            if len(errors) != 0:
                print(errors)

    if payload_type == "tech":
        for tech in payload["tech"]:
            row = [
                [
                    refinery_id,
                    refined_at,
                    refined_date,
                    domain,
                    url,
                    tech
                ]
            ]

            errors = client.create_rows(
                table=table,
                rows=row,
                selected_fields=schema
            )

            # # newer versions of the library
            # errors = client.insert_rows(
            #     table,
            #     row,
            #     selected_fields=schema
            # )

            if len(errors) != 0:
                print(errors)

    if payload_type == "mobile":
        row = [
            [
                refinery_id,
                refined_at,
                refined_date,
                domain,
                url,
                payload["test_results"]
            ]
        ]

        errors = client.create_rows(
            table=table,
            rows=row,
            selected_fields=schema
        )

        # # newer versions of the library
        # errors = client.insert_rows(
        #     table,
        #     row,
        #     selected_fields=schema
        # )

        if len(errors) != 0:
            print(errors)
