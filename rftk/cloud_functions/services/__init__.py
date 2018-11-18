"""
RFTK: A python utility package for the Infusionsoft Refinery.
"""

__version__ = "0.4.32"
__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

from .classes import MetadataMixin

from .functions import get_service_params, get_valid_url, \
    upload_to_gcs, publish_to_endpoint, decode_event, \
    download_from_gcs, insert_bq_row

from .schemas import MOBILE_FRIENDLY_SCHEMA, \
    CRAWLER_TECH_HISTORY_SCHEMA, TAGS_HISTORY_SCHEMA, \
    TECH_HISTORY_SCHEMA, CRAWLER_SCHEMA, CLEARBIT_PERSON_SCHEMA, \
    CLEARBIT_COMPANY_SCHEMA, WP_PLUGIN_LOOKUP_SCHEMA, \
    WP_PLUGIN_LOOKUP_ERROR_SCHEMA, EMAIL_PROVIDER_SCHEMA

from .constants import MAX_RETRIES

from .deployment import CLEARBIT_TECH_BQ_CONFIGS, \
    CLEARBIT_TAGS_BQ_CONFIGS, CLEARBIT_PERSON_CONFIGS, \
    CLEARBIT_COMPANY_CONFIGS, CLEARBIT_CONFIGS, \
    CRAWLER_TECH_BQ_CONFIGS, CRAWLER_CONFIGS, \
    CRAWLER_DOMAIN_BQ_CONFIGS, ENDPOINT_CONFIGS, MOBILE_TO_BQ_CONFIGS, \
    MOBILE_CONFIGS, WP_PLUGIN_LOOKUP_CONFIGS

from .wordpress import get_wp_plugin_info_online

from .email_provider import get_email_provider

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
    "WP_PLUGIN_LOOKUP_SCHEMA",
    "WP_PLUGIN_LOOKUP_ERROR_SCHEMA",
    "EMAIL_PROVIDER_SCHEMA",
    "MetadataMixin",
    "MAX_RETRIES",
    "CLEARBIT_CONFIGS",
    "CLEARBIT_COMPANY_CONFIGS",
    "CLEARBIT_PERSON_CONFIGS",
    "CLEARBIT_TAGS_BQ_CONFIGS",
    "CLEARBIT_TECH_BQ_CONFIGS",
    "CRAWLER_DOMAIN_BQ_CONFIGS",
    "CRAWLER_CONFIGS",
    "CRAWLER_TECH_BQ_CONFIGS",
    "MOBILE_CONFIGS",
    "MOBILE_TO_BQ_CONFIGS",
    "ENDPOINT_CONFIGS",
    "WP_PLUGIN_LOOKUP_CONFIGS",
    "get_wp_plugin_info_online",
    "get_email_provider"
]
