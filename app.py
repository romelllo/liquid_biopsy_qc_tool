"""
Main module og the qc_tool service.
"""

from dotenv import dotenv_values

from complete_stages import complete_qc_stages
from service_settings.service_config import QCToolConfig, ServiceConfig
from spreadsheet.spreadsheet_client import (
    connect_to_google_sheet,
    get_sheet_data,
    sheet_data_to_df,
)
from utilities import create_logger, save_qc_tool_result_locally

# Constants
# The title of the Google Sheet
SHEET_TITLE = "cfDNA_samples"

# Create the logger
service_config = ServiceConfig()
logger = create_logger(
    name=service_config.logger_name,
    file_path=service_config.logger_file_path,
    file_name=service_config.logger_file_name,
)

# Create the QCToolConfig object
qctool_config = QCToolConfig()

# Load the environment variables
config = dotenv_values(".env")

# Get the credentials for the Google Sheet API
spreadsheet_credentials = config["GDRIVE_API_CREDENTIALS"]

# Connect to the Google Sheet
sheet = connect_to_google_sheet(spreadsheet_credentials, SHEET_TITLE)
logger.info("Connected to the Google Sheet.")

# Get the data from the Google Sheet
data = get_sheet_data(sheet)

# Convert the data to a pandas DataFrame
df = sheet_data_to_df(data)


def main():
    """
    The main function.
    """
    for sample in df["Sample sheet_Sample_ID"]:
        result = complete_qc_stages(sample, df, qctool_config, logger)
        logger.info("The checking and estimation stages are completed.")

        # Save the result of the qc_tool to a file
        save_qc_tool_result_locally(
            result,
            service_config.result_file_path,
            f"{result['meta']['sample_id']}_qc_tool_result.json",
        )
        logger.info("The result is saved to a file.")


if __name__ == "__main__":
    main()
