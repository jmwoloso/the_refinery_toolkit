"""
RFTK: A python utility package for the Infusionsoft Refinery.
"""

__version__ = "0.5.1"
__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

from .classes import MetadataMixin

from .functions import get_service_params, get_valid_url, \
    upload_to_gcs, publish_to_endpoint, decode_event, \
    download_from_gcs, insert_one_to_bq, insert_many_to_bq, \
    is_valid_email, get_domain_from_email

from .schemas import MOBILE_FRIENDLY_SCHEMA, \
    CRAWLER_WORDPRESS_PLUGIN_HISTORY_SCHEMA, \
    CLEARBIT_TAGS_HISTORY_SCHEMA, \
    CLEARBIT_TECH_HISTORY_SCHEMA, CRAWLER_DOMAIN_SCHEMA, \
    CLEARBIT_PERSON_SCHEMA, CLEARBIT_EMAILS_HISTORY_SCHEMA, \
    CLEARBIT_PHONES_HISTORY_SCHEMA, CLEARBIT_COMPANY_SCHEMA, \
    WP_PLUGIN_LOOKUP_SCHEMA, WP_PLUGIN_LOOKUP_ERROR_SCHEMA, \
    EMAIL_PROVIDER_SCHEMA, IP_LOOKUP_SCHEMA

from .constants import MAX_RETRIES

from .crawler_service import HEADERS

from .deployment import CLEARBIT_CONFIGS, CRAWLER_CONFIGS, \
    ENDPOINT_CONFIGS, MOBILE_CONFIGS, WP_PLUGIN_LOOKUP_CONFIGS

from .wordpress_lookup_service import get_wp_plugin_info_online

from .email_provider_lookup_service import get_email_provider

# TODO: should follow the same versioning cadence as the_refinery
__all__ = [
    "get_valid_url",
    "is_valid_email",
    "get_domain_from_email",
    "get_service_params",
    "upload_to_gcs",
    "MOBILE_FRIENDLY_SCHEMA",
    "CRAWLER_WORDPRESS_PLUGIN_HISTORY_SCHEMA",
    "CLEARBIT_TECH_HISTORY_SCHEMA",
    "CLEARBIT_TAGS_HISTORY_SCHEMA",
    "CLEARBIT_PHONES_HISTORY_SCHEMA",
    "CLEARBIT_EMAILS_HISTORY_SCHEMA",
    "CRAWLER_DOMAIN_SCHEMA",
    "CLEARBIT_COMPANY_SCHEMA",
    "CLEARBIT_PERSON_SCHEMA",
    "WP_PLUGIN_LOOKUP_SCHEMA",
    "WP_PLUGIN_LOOKUP_ERROR_SCHEMA",
    "EMAIL_PROVIDER_SCHEMA",
    "IP_LOOKUP_SCHEMA",
    "MetadataMixin",
    "MAX_RETRIES",
    "HEADERS",
    "CLEARBIT_CONFIGS",
    "CRAWLER_CONFIGS",
    "MOBILE_CONFIGS",
    "ENDPOINT_CONFIGS",
    "WP_PLUGIN_LOOKUP_CONFIGS",
    "get_wp_plugin_info_online",
    "get_email_provider",
    "insert_one_to_bq",
    "insert_many_to_bq",
    "publish_to_endpoint"
]
