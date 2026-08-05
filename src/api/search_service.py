# coding: utf-8
"""
Shared client for the external search service (iAHx / `search_json`).

All API resources that expose a `search` endpoint talk to the same service with
the same headers and the same error handling. Keeping that in one place avoids
the drift that caused the 403 regression documented in
`.ai/logs/2026-08-05-fix-bibliographic-search-403.md`.
"""
from django.conf import settings

import requests
import json


# The service is fronted by nginx, which rejects the request with 403 unless
# both of these are present:
#   - an explicit Content-Type: passing a str body makes requests omit it;
#   - a non-default User-Agent: `python-requests/*` and `curl/*` are blocklisted.
SEARCH_CONTENT_TYPE = 'application/json'
SEARCH_USER_AGENT = 'fi-admin'


def get_search_headers():
    """Headers required by the search service. Read at call time so that
    settings overrides (ex. in tests) are honoured."""
    return {'apikey': settings.SEARCH_SERVICE_APIKEY,
            'Content-Type': SEARCH_CONTENT_TYPE,
            'User-Agent': SEARCH_USER_AGENT}


def search_service_request(search_params):
    """POST `search_params` to the search service and return the decoded JSON.

    On a non-JSON body (ex. the nginx HTML error page) returns an error dict
    carrying the HTTP status instead of raising, so a failing search surfaces a
    diagnosable payload rather than a 500.
    """
    search_url = "%s/search_json" % settings.SEARCH_SERVICE_URL
    search_params_json = json.dumps(search_params)

    response = requests.post(search_url, data=search_params_json, headers=get_search_headers())
    try:
        return response.json()
    except ValueError:
        return {"type": "error",
                "message": "invalid output (status {})".format(response.status_code)}


def duplicate_response_to_match(response_json):
    """Duplicate "response" into a "match" element for old compatibility calls.

    No-op when the service returned an error payload, which has no
    `diaServerResponse` key.
    """
    if response_json and 'diaServerResponse' in response_json:
        response_json['diaServerResponse'][0]['match'] = response_json['diaServerResponse'][0]['response']

    return response_json
