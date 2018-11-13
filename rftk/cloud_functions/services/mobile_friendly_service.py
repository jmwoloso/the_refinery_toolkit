"""
mobile_friendly_service.py: Utility functions used by the service that
                            checks whether a site is mobile-friendly.
"""

__author__ = "Jason Wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

import requests
import time


# TODO: this needs more thorough investigation/testing to see how/why
# we keep getting 502 errors
def check_mobile_friendly(request=None):
    """Utility function to test whether the supplied domain is mobile
    friendly."""
    print("check_mobile_friendly()")
    # pause to avoid being rate-limited
    time.sleep(1)
    headers = {"Content-Type": "application/json"}
    json_data = {"url": request["url"]}
    api_url = \
        "https://searchconsole.googleapis.com/v1/urlTestingTools" \
        "/mobileFriendlyTest:run?key" \
        "=AIzaSyCl4UW5RRovdGSf0xyjlwMpJ754n4_CcvM"
    print("sending request for: {}".format(request["url"]))
    success = False
    i = 0
    while success is False and i < 5:
        try:
            resp = requests.post(
                url=api_url,
                headers=headers,
                json=json_data
            )
            resp.raise_for_status()

            print("response: {}".format(resp))
            success = True
            continue
        except requests.exceptions.HTTPError as e:
            print("attempt {} failed.".format(i + 1))
            i += 1
            resp = str(e.response.status_code) + ": " + e
            continue

    resp_ = {
        "refinery_id": request["refinery_id"],
        "refined_at": request["refined_at"],
        "refined_date": request["refined_date"],
        "domain": request["domain"],
        "url": request["url"]
    }

    # we never were able to successfully test the url
    if success is False:
        resp_["test_results"] = str(resp.status) + ": " + resp.reason

    else:
        # tests passed successfully
        if resp.json()["testStatus"]["status"] == "COMPLETE":
            resp_["test_results"] = resp.json()[
                "mobileFriendliness"].lower()

        # even errors seem to return a 200 status code?
        elif resp.json()["testStatus"]["status"] != "COMPLETE":
            if "details" in resp.json()["testStatus"].keys():
                resp_["test_results"] = \
                    resp.json()["testStatus"]["status"] + \
                    " : " + \
                    resp.json()["testStatus"]["details"]
            else:
                resp_["test_results"] = \
                    resp.json()["testStatus"]["status"]
    return resp_
