"""
This module contains the utility functions for the Google Sheet API.
"""

import base64
import json


def get_google_sheet_service_account_dict(config: str) -> dict:
    """
    Generate credentials for Google Sheet API:decode the base64 encoded credentials and convert it to a dict.

    :param config: The credentials for the Google Sheet API.
    :type config: str
    :return: The credentials for the Google Sheet API.
    :rtype: dict
    """
    return json.loads(base64.b64decode(config))
