"""
Module for completing the checking stages for a sample.
"""

import logging
from datetime import datetime

import pandas as pd

from service_settings.service_config import QCToolConfig
from spreadsheet.spreadsheet_client import get_sample_data
from values import MINIMAL_VAF_AND_LOD_ESTIMATION_STAGE_UID


def complete_qc_stages(
    sample_id: str,
    df: pd.DataFrame,
    qc_tool_config: QCToolConfig,
    logger: logging.Logger,
) -> dict:
    """
    Complete the checking and estimation QC stages for a sample.

    :param sample_id: The id of the sample.
    :type sample_id: str
    :param df: The data from the Google Sheet.
    :type df: pd.DataFrame
    :param qc_tool_config: The configufractionn for the qc_tool.
    :type qc_tool_config: QCToolConfig
    :param logger: The logger.
    :type logger: logging.Logger
    :return: The result of the check.
    :rtype: dict
    """
    # Get the sample data
    logger.info("Checking sample: %s", sample_id)
    sample_df = get_sample_data(sample_id, df)

    # Get the check stages
    check_stages = qc_tool_config.check_stages
    # Get the estimation stages
    estimation_stages = qc_tool_config.estimation_stages
    # Get the regression models
    regression_models = qc_tool_config.regression_models

    # Create the result dictionary
    result = {}

    # Add the meta information to the result: sample name, config version, and date
    result["meta"] = {
        "sample_id": sample_id,
        "config_version": qc_tool_config.config_version,
        "date": datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
    }

    # Add the stages to the result
    result["stages"] = {"checks": [], "estimations": []}

    # Complete the check stages
    for check_stage in check_stages:
        logger.info("Check stage: %s", check_stage["name"])
        # Get the check function
        check_function = qc_tool_config.uid_stage_name_dict[check_stage["uid"]]
        # Check the sample
        try:
            result["stages"]["checks"].append(check_function(sample_df, check_stage))
        except Exception as e:
            logger.error("Error in stage: %s", check_stage["name"])
            logger.error(e)
            result["stages"]["checks"].append(
                {
                    "uid": check_stage["uid"],
                    "name": check_stage["name"],
                    "status": "error",
                    "message": f"Error in stage '{check_stage['name']}': {e}",
                }
            )

        logger.info(f"Check stage result: {result['stages']['checks'][-1]}")

    # Complete the estimation stages
    for estimation_stage in estimation_stages:
        logger.info("Estimation stage: %s", estimation_stage["name"])
        # Get the estimation function
        estimation_function = qc_tool_config.uid_stage_name_dict[
            estimation_stage["uid"]
        ]
        # Estimate the value
        try:
            if estimation_stage["uid"] == MINIMAL_VAF_AND_LOD_ESTIMATION_STAGE_UID:
                result["stages"]["estimations"].append(
                    estimation_function(sample_df, estimation_stage, regression_models)
                )
            else:
                result["stages"]["estimations"].append(
                    estimation_function(sample_df, estimation_stage)
                )
        except Exception as e:
            logger.error("Error in stage: %s", estimation_stage["name"])
            logger.error(e)
            result["stages"]["estimations"].append(
                {
                    "uid": estimation_stage["uid"],
                    "name": estimation_stage["name"],
                    "status": "error",
                    "message": f"Error in stage '{estimation_stage['name']}': {e}",
                }
            )

        logger.info(f"Estimation stage result: {result['stages']['estimations'][-1]}")

    return result
