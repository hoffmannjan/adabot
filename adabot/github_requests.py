# The MIT License (MIT)
#
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_adabot`
====================================================

TODO(description)

* Author(s): Scott Shawcroft
"""

import datetime
import os
import requests
import time


def _fix_url(url):
    if url.startswith("/"):
        url = "https://api.github.com" + url
    return url

def _fix_kwargs(kwargs):
    api_version = "application/vnd.github.scarlet-witch-preview+json;application/vnd.github.hellcat-preview+json"
    if "headers" in kwargs:
        if "Accept" in kwargs["headers"]:
            kwargs["headers"]["Accept"] += ";" + api_version
        else:
            kwargs["headers"]["Accept"] = api_version
    else:
        kwargs["headers"] = {"Accept": "application/vnd.github.hellcat-preview+json"}
    if "ADABOT_GITHUB_ACCESS_TOKEN" in os.environ and "auth" not in kwargs:
        access_token = os.environ["ADABOT_GITHUB_ACCESS_TOKEN"]
        if "params" in kwargs:
            kwargs["params"]["access_token"] = access_token
        else:
            kwargs["params"] = {"access_token": access_token}
    return kwargs

def get(url, **kwargs):
    response = requests.get(_fix_url(url), timeout=30, **_fix_kwargs(kwargs))
    if "X-RateLimit-Remaining" in response.headers:
        remaining = int(response.headers["X-RateLimit-Remaining"])
        if remaining <= 1:
            rate_limit_reset = datetime.datetime.fromtimestamp(int(response.headers["X-RateLimit-Reset"]))
            print("GitHub API Rate Limit reached. Pausing until Rate Limit reset.")
            while datetime.datetime.now() < rate_limit_reset:
                print("Rate Limit will reset at: {}".format(rate_limit_reset))
                if "TRAVIS" in os.environ:
                    # only pause for 5 minutes so that Travis doesn't timeout
                    # due to idle console output.
                    time.sleep(300)
                else:
                    reset_diff = rate_limit_reset - datetime.datetime.now()

                    print("Sleeping {} seconds".format(reset_diff.seconds))
                    time.sleep(reset_diff.seconds + 1)
        if remaining % 100 == 0:
            print(remaining, "requests remaining this hour")
    return response

def post(url, **kwargs):
    return requests.post(_fix_url(url), timeout=30, **_fix_kwargs(kwargs))

def put(url, **kwargs):
    return requests.put(_fix_url(url), timeout=30, **_fix_kwargs(kwargs))

def patch(url, **kwargs):
    return requests.patch(_fix_url(url), timeout=30, **_fix_kwargs(kwargs))

def delete(url, **kwargs):
    return requests.delete(_fix_url(url), timeout=30, **_fix_kwargs(kwargs))
