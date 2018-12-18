"""
deployment.py: Contains deployment configurations for each of the
functions.
"""
from __future__ import print_function, division, unicode_literals, \
    absolute_import
from builtins import str

__author__ = u"Jason Wolosonovich <jason@avaland.io>"
__license__ = u"BSD 3 Clause"


ENDPOINT_CONFIGS = {
    u"name": u"the_refinery",
    u"full_name": u"projects/infusionsoft-looker-poc/locations/uc"
                 u"-central1/functions/the_refinery",
    u"region": u"us-central1",
    u"timeout": u"540s",
    u"memory": u"512MB",
    u"runtime": u"python37",
    u"trigger": u"the_refinery",
    u"entry_point": u"run_the_refinery",
    u"source": u"/cloud_functions/services/the_refinery/",
}


CLEARBIT_CONFIGS = {
    u"name": u"the_refinery_clearbit_service",
    u"full_name": u"projects/infusionsoft-looker-poc/locations/uc"
                 u"-central1/functions/the_refinery_clearbit_service",
    u"region": u"us-central1",
    u"timeout": u"540s",
    u"memory": u"512MB",
    u"runtime": u"python37",
    u"trigger": u"the_refinery_clearbit_service",
    u"entry_point": u"run_clearbit_service",
    u"source": u"/cloud_functions/services/clearbit_service/",
}


CRAWLER_CONFIGS = {
    u"name": u"the_refinery_crawler_service",
    u"full_name": u"projects/infusionsoft-looker-poc/locations/uc"
                 u"-central1/functions/the_refinery_crawler_service",
    u"region": u"us-central1",
    u"timeout": u"540s",
    u"memory": u"512MB",
    u"runtime": u"python37",
    u"trigger": u"the_refinery_crawler_service",
    u"entry_point": u"run_crawler_service",
    u"source": u"/cloud_functions/services/crawler_service/",
}


MOBILE_CONFIGS = {
    u"name": u"the_refinery_mobile_friendly_service",
    u"full_name": u"projects/infusionsoft-looker-poc/locations/uc"
                 u"-central1/functions/the_refinery_mobile_friendly_service",
    u"region": u"us-central1",
    u"timeout": u"540s",
    u"memory": u"512MB",
    u"runtime": u"python37",
    u"trigger": u"the_refinery_mobile_friendly_service",
    u"entry_point": u"run_mobile_friendly_service",
    u"source": u"/cloud_functions/services/mobile_friendly_service/",
}


WP_PLUGIN_LOOKUP_CONFIGS = {
    u"name": u"the_refinery_wordpress_plugin_lookup_service",
    u"full_name": u"projects/infusionsoft-looker-poc/locations/uc"
                 u"-central1/functions/the_refinery_wordpress_plugin_lookup_service",
    u"region": u"us-central1",
    u"timeout": u"540s",
    u"memory": u"512MB",
    u"runtime": u"python37",
    u"trigger": u"the_refinery_wordpress_plugin_lookup_service",
    u"entry_point": u"run_wordpress_plugin_lookup_service",
    u"source": u"/cloud_functions/services"
              u"/wordpress_plugin_lookup_service/",
}


EMAIL_PROVIDER_LOOKUP_CONFIGS = {
    u"name": u"the_refinery_email_provider_lookup_service",
    u"full_name": u"projects/infusionsoft-looker-poc/locations/uc"
                 u"-central1/functions/the_refinery_email_provider_lookup_service",
    u"region": u"us-central1",
    u"timeout": u"540s",
    u"memory": u"512MB",
    u"runtime": u"python37",
    u"trigger": u"the_refinery_email_provider_lookup_service",
    u"entry_point": u"run_email_provider_lookup_service",
    u"source": u"/cloud_functions/services"
              u"/email_provider_lookup_service/",
}