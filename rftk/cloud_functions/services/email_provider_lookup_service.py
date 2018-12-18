from __future__ import print_function, division, unicode_literals, \
    absolute_import
import re

import dns.resolver
import dns.exception


def get_email_provider(domain=None):
    """Performs the MX lookup for the specified domain."""
    # perform the lookup and coalesce the results
    email_providers = list()
    mx_records = list()

    max_retries = 15
    for n in range(max_retries):
        try:
            print("getting email providers for: {}"
                  .format(domain))

            print("adjusting resolver params")
            # adjust the timeout settings (quicker)
            # https://github.com/rthalley/dnspython/issues/22
            dns.resolver.get_default_resolver().timeout = 10.0
            dns.resolver.get_default_resolver().lifetime = 10.0

            # TODO: verify where the domain is being stored in the request
            for record in dns.resolver.query(domain, "MX"):
                print("attempt: {}".format(n+1))
                # get the current result and parse out the index value
                result = re.sub("\d+\s",
                                "",
                                record.to_text())
                print("mx_record: {}".format(result))

                # append the raw record
                mx_records.append(result)

                # take the last 2 pieces and remove the trailing .
                email_provider = result.split(".")[-3:-1]

                # combine the two parts
                email_provider = ".".join(email_provider)

                print("email_provider: {}".format(email_provider))
                # append to the list
                email_providers.append(email_provider)

            break
        except dns.exception.Timeout as e:
            print("error with {}: {}".format(domain,
                                             e))
            if n == max_retries - 1:
                email_providers = "error"
                mx_records = "error"
                return email_providers, mx_records
            continue
        except dns.exception.FormError as e:
            print("error with {}: {}".format(domain,
                                             e))
            if n == max_retries - 1:
                email_providers = "error"
                mx_records = "error"
                return email_providers, mx_records
            continue
        except dns.exception.UnexpectedEnd as e:
            print("error with {}: {}".format(domain,
                                             e))
            if n == max_retries - 1:
                email_providers = "error"
                mx_records = "error"
                return email_providers, mx_records
            continue
        except dns.exception.TooBig as e:
            print("error with {}: {}".format(domain,
                                             e))
            if n == max_retries - 1:
                email_providers = "error"
                mx_records = "error"
                return email_providers, mx_records
            continue
        except dns.exception.SyntaxError as e:
            print("error with {}: {}".format(domain,
                                             e))
            if n == max_retries - 1:
                email_providers = "error"
                mx_records = "error"
                return email_providers, mx_records
            continue
        except dns.exception.DNSException as e:
            print("error with {}: {}".format(domain,
                                             e))
            if n == max_retries - 1:
                email_providers = "error"
                mx_records = "error"
                return email_providers, mx_records
            continue

    return email_providers, mx_records
