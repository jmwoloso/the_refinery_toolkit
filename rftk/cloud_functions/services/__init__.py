"""
RFTK: A python utility package for the Infusionsoft Refinery.
"""

__version__ = "0.4.0"
__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

from .classes import MetadataMixin

from .functions import get_service_params, get_valid_url, \
    upload_to_gcs, publish_to_endpoint, decode_event, \
    download_from_gcs, insert_bq_row

from .schemas import MOBILE_FRIENDLY_SCHEMA, \
    CRAWLER_TECH_HISTORY_SCHEMA, TAGS_HISTORY_SCHEMA, \
    TECH_HISTORY_SCHEMA, CRAWLER_SCHEMA, CLEARBIT_PERSON_SCHEMA, \
    CLEARBIT_COMPANY_SCHEMA

# TODO: should follow the same versioning cadence as the_refinery
__all__ = [
    "get_valid_url",
    "get_service_params",
    "upload_to_gcs",
    "MOBILE_FRIENDLY_SCHEMA",
    "CRAWLER_TECH_HISTORY_SCHEMA",
    "TECH_HISTORY_SCHEMA",
    "TAGS_HISTORY_SCHEMA",
    "CRAWLER_SCHEMA",
    "CLEARBIT_COMPANY_SCHEMA",
    "CLEARBIT_PERSON_SCHEMA",
    "MetadataMixin",
]
