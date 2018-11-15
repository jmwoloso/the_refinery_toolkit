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
    "timeout": "60s",
    "memory": "128MB",
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
    "timeout": "60s",
    "memory": "128MB",
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
    "timeout": "60s",
    "memory": "128MB",
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
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_mobile_friendly_service",
    "entry_point": "run_mobile_friendly_service",
    "source": "/cloud_functions/services/mobile_friendly_service/",
}


CLEARBIT_COMPANY_CONFIGS = {
    "name": "the_refinery_clearbit_company_to_bq_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_clearbit_company_to_bq_service",
    "region": "us-central1",
    "timeout": "60s",
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_clearbit_company_to_bq_service",
    "entry_point": "run_clearbit_company_to_bq_service",
    "source": "/cloud_functions/services"
              "/clearbit_company_to_bq_service/",
}


CLEARBIT_PERSON_CONFIGS = {
    "name": "the_refinery_clearbit_person_to_bq_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_clearbit_person_to_bq_service",
    "region": "us-central1",
    "timeout": "60s",
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_clearbit_person_to_bq_service",
    "entry_point": "run_clearbit_person_to_bq_service",
    "source": "/cloud_functions/services"
              "/clearbit_person_to_bq_service/",
}


CRAWLER_DOMAIN_BQ_CONFIGS = {
    "name": "the_refinery_crawler_domain_to_bq_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_crawler_domain_to_bq_service",
    "region": "us-central1",
    "timeout": "60s",
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_crawler_domain_to_bq_service",
    "entry_point": "run_crawler_to_bq_service",
    "source": "/cloud_functions/services"
              "/crawler_domain_to_bq_service/",
}


MOBILE_TO_BQ_CONFIGS = {
    "name": "the_refinery_mobile_friendly_to_bq_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_mobile_friendly_to_bq_service",
    "region": "us-central1",
    "timeout": "60s",
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_mobile_friendly_to_bq_service",
    "entry_point": "run_mobile_friendly_to_bq_service",
    "source": "/cloud_functions/services"
              "/mobile_friendly_to_bq_service/",
}


CLEARBIT_TAGS_BQ_CONFIGS = {
    "name": "the_refinery_clearbit_tags_history_to_bq_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_clearbit_tags_history_to_bq_service",
    "region": "us-central1",
    "timeout": "60s",
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_clearbit_tags_history_to_bq_service",
    "entry_point": "run_clearbit_tags_history_to_bq_service",
    "source": "/cloud_functions/services"
              "/clearbit_tags_history_to_bq_service/",
}


CLEARBIT_TECH_BQ_CONFIGS = {
    "name": "the_refinery_clearbit_tech_history_to_bq_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_clearbit_tech_history_to_bq_service",
    "region": "us-central1",
    "timeout": "60s",
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_clearbit_tech_history_to_bq_service",
    "entry_point": "run_clearbit_tech_history_to_bq_service",
    "source": "/cloud_functions/services"
              "/clearbit_tech_history_to_bq_service/",
}


CRAWLER_TECH_BQ_CONFIGS = {
    "name": "the_refinery_crawler_tech_history_to_bq_service",
    "full_name": "projects/infusionsoft-looker-poc/locations/uc"
                 "-central1/functions/the_refinery_crawler_tech_history_to_bq_service",
    "region": "us-central1",
    "timeout": "60s",
    "memory": "128MB",
    "runtime": "python37",
    "trigger": "the_refinery_crawler_tech_history_to_bq_service",
    "entry_point": "run_crawler_tech_history_to_bq_service",
    "source": "/cloud_functions/services"
              "/crawler_tech_history_to_bq_service/",
}