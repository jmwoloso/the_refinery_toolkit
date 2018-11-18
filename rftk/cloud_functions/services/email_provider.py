import re

import dns.resolver


def get_email_provider(domain=None):
    """Performs the MX lookup for the specified domain."""
    # perform the lookup and coalesce the results
    email_providers = list()
    mx_records = list()

    try:
        print("getting email providers for: {}"
              .format(domain))
        # TODO: verify where the domain is being stored in the request
        for record in dns.resolver.query(domain, "MX"):
            # get the current result and parse out the index value
            result = re.sub("\d+\s",
                            "",
                            record.to_text())

            # append the raw record
            mx_records.append(result)

            # take the last 2 pieces and remove the trailing .
            email_provider = result.split(".")[-3:-1]

            # combine the two parts
            email_provider = ".".join(email_provider)

            # append to the list
            email_providers.append(email_provider)

        # now coalesce the records
        email_providers = list(set(email_providers))

    except Exception as e:
        print("error with {}: {}".format(domain,
                                         e))
        email_providers = []
        mx_records = []

    return email_providers, mx_records
