"""
deployment.py: Contains deployment configurations for each of the
functions.
"""

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 Clause"


ENDPOINT_CONFIGS = {
    "name": "the_refinery",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery",
    "region": "us-central1",
    "timeout": "540s",
    "memory": "512MB",
    "runtime": "python37",
    "trigger": "the_refinery",
    "entry_point": "run_the_refinery",
    "source": "/cloud_functions/services/the_refinery/",
}


CLEARBIT_CONFIGS = {
    "name": "the_refinery_clearbit_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_clearbit_service",
    "region": "us-central1",
    "timeout": "540s",
    "memory": "512MB",
    "runtime": "python37",
    "trigger": "the_refinery_clearbit_service",
    "entry_point": "run_clearbit_service",
    "source": "/cloud_functions/services/clearbit_service/",
}


CRAWLER_CONFIGS = {
    "name": "the_refinery_crawler_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_crawler_service",
    "region": "us-central1",
    "timeout": "540s",
    "memory": "512MB",
    "runtime": "python37",
    "trigger": "the_refinery_crawler_service",
    "entry_point": "run_crawler_service",
    "source": "/cloud_functions/services/crawler_service/",
}


MOBILE_CONFIGS = {
    "name": "the_refinery_mobile_friendly_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_mobile_friendly_service",
    "region": "us-central1",
    "timeout": "540s",
    "memory": "512MB",
    "runtime": "python37",
    "trigger": "the_refinery_mobile_friendly_service",
    "entry_point": "run_mobile_friendly_service",
    "source": "/cloud_functions/services/mobile_friendly_service/",
}


WP_PLUGIN_LOOKUP_CONFIGS = {
    "name": "the_refinery_wordpress_plugin_lookup_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_wordpress_plugin_lookup_service",
    "region": "us-central1",
    "timeout": "540s",
    "memory": "512MB",
    "runtime": "python37",
    "trigger": "the_refinery_wordpress_plugin_lookup_service",
    "entry_point": "run_wordpress_plugin_lookup_service",
    "source": "/cloud_functions/services"
              "/wordpress_plugin_lookup_service/",
}


EMAIL_PROVIDER_LOOKUP_CONFIGS = {
    "name": "the_refinery_email_provider_lookup_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_email_provider_lookup_service",
    "region": "us-central1",
    "timeout": "540s",
    "memory": "512MB",
    "runtime": "python37",
    "trigger": "the_refinery_email_provider_lookup_service",
    "entry_point": "run_email_provider_lookup_service",
    "source": "/cloud_functions/services"
              "/email_provider_lookup_service/",
}