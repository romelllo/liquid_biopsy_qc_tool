"""
Module for connecting to a Google Sheet and getting the data from it.
"""

import gspread
import pandas as pd

from spreadsheet.spreadsheet_utilities import get_google_sheet_service_account_dict


def connect_to_google_sheet(
    credentials: str | None, sheet_title: str
) -> gspread.spreadsheet.Spreadsheet:
    """
    Connect to a Google Sheet using the gspread library.

    :param credentials: The credentials for the Google Sheet API.
    :type credentials: str
    :param sheet_title: The title of the Google Sheet.
    :type sheet_title: str
    :return: The Google Sheet.
    :rtype: gspread.spreadsheet.Spreadsheet
    """
    config = get_google_sheet_service_account_dict(credentials)
    # Authorize the client
    client = gspread.service_account_from_dict(config)
    # Open the Google Sheet by its title or URL
    sheet = client.open(sheet_title).sheet1

    return sheet


def get_sheet_data(sheet: gspread.spreadsheet.Spreadsheet) -> list:
    """
    Get the data from a Google Sheet.

    :param sheet: The Google Sheet.
    :type sheet: gspread.models.Spreadsheet
    :return: The data from the Google Sheet.
    :rtype: list
    """
    # Get all values from the sheet
    data = sheet.get_all_values()

    return data


def sheet_data_to_df(data: list) -> pd.DataFrame:
    """
    Convert the data from a Google Sheet to a pandas DataFrame.

    :param data: The data from the Google Sheet.
    :type data: list
    :return: The data as a pandas DataFrame.
    :rtype: pd.DataFrame
    """
    # Create a pandas DataFrame from the data
    df = pd.DataFrame(data[1:], columns=data[0])

    return df


def get_sample_data(sample_id: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Get the data for a specific sample from the DataFrame.

    :param sample_id: The id of the sample.
    :type sample_id: str
    :param df: The DataFrame.
    :type df: pd.DataFrame
    :return: The data for the sample.
    :rtype: pd.DataFrame
    """
    # Filter the DataFrame for the sample
    sample_data = df[df["Sample sheet_Sample_ID"] == sample_id]

    return sample_data
