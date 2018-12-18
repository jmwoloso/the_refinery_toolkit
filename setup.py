#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from rftk.cloud_functions import services

setup(name="the_refinery_toolkit",
      version=services.__version__,
      description="The Refinery Toolkit (RFTK)",
      author="Jason Wolosonovich",
      author_email="jason@avaland.io",
      url="https://github.com/jmwoloso/rftk",
      packages=["rftk.cloud_functions",
                "rftk.cloud_functions.services"],
      license="BSD 3 Clause",
      long_description="The Refinery Toolkit - "
                       "A Collection of Utilities for use "
                       "with The Refinery on GCP",
      install_requires=[
          "beautifulsoup4==4.6.3",
          "cachetools==2.1.0",
          "certifi==2018.10.15",
          "chardet==3.0.4",
          "clearbit==0.1.7",
          "Click==7.0",
          "decorator==4.3.0",
          "dnspython==1.15.0",
          "gcsfs==0.2.0",
          "google-auth-oauthlib==0.2.0",
          "google-api-core==1.6.0a1",
          "google-api-python-client==1.7.4",
          "google-auth==1.5.1",
          "google-auth-httplib2==0.0.3",
          "google-cloud-bigquery==1.6.0",
          "google-cloud-bigquery-datatransfer==0.1.1",
          "google-cloud-core==0.28.1",
          "google-cloud-language==1.1.0",
          "google-cloud-pubsub==0.38.0",
          "google-cloud-storage==1.13.0",
          "google-resumable-media==0.3.1",
          "googleapis-common-protos==1.5.5",
          "grpc-google-iam-v1==0.11.4",
          "grpcio==1.16.0",
          "httplib2==0.11.3",
          "idna==2.7",
          "oauthlib==2.1.0",
          "protobuf==3.6.1",
          "psutil==5.4.7",
          "pyasn1==0.4.4",
          "pyasn1-modules==0.2.2",
          "pytz==2018.6",
          "requests==2.20.0",
          "requests-oauthlib==1.0.0",
          "rsa==4.0",
          "six==1.11.0",
          "typed-ast==1.1.0",
          "uritemplate==3.0.0",
          "urllib3==1.24",
          "validators==0.12.2"
      ],
      classifiers=[
          "Development Status :: 3 - Alpha",
          # "Programming Language :: Python :: 2",
          # "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Topic :: Software Development :: Libraries :: Python "
          "Modules",
          "Topic :: Scientific/Engineering",
          "Operating System :: Unix",
          "Operating System :: MacOS",
          "Operating System :: POSIX",
          "Operating System :: Microsoft :: Windows",
          "Intended Audience :: Science/Research",
          "Intended Audience :: Other Audience",
          "Intended Audience :: Information Technology"
      ])
