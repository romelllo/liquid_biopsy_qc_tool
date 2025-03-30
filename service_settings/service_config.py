"""
Module for storing classes used for service configufractionn.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, ClassVar

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from stages import (
    average_coverage_completeness_v1_v2_check,
    average_coverage_v1_v2_ratio_check,
    insert_size_fraction_estimation,
    number_of_reads_check,
    off_target_check,
    total_deduplicated_percentage_check,
    vaf_lod_estimation,
)

with (Path(__file__).resolve().parent / "qc_tool_config.json").open("r") as conf_obj:
    config = json.load(conf_obj)


@dataclass
class ServiceConfig:
    """
    Class for storing some service specific information:
    service name, logger name, logger file name.
    """

    service_name: str = "qc_tool"

    logger_name: str = None
    logger_file_name: str = None
    logger_file_path: str = None
    result_file_path: str = None

    def __post_init__(self):
        self.logger_name = self.service_name
        self.logger_file_name = f"{self.service_name}.log"
        self.logger_file_path = "logs"
        self.result_file_path = "results"


class RegressionModelsConfig:
    """
    Class for storing the configufractionn for the regression models based on the coverage:
        - regression for vaf;
        - regression for lod.
    """

    def hyperbola(self, x: float, a: float, b: float, c: float) -> float:
        """
        Get the hyperbola function.

        :param x: The x value.
        :type x: float
        :param a: The a parameter.
        :type a: float
        :param b: The b parameter.
        :type b: float
        :param c: The c parameter.
        :type c: float
        :return: The y value.
        : rtype: float
        """
        return a / (x + b) + c

    def _get_regression_model(self, data: pd.DataFrame, lod_or_vaf: str) -> np.ndarray:
        """
        Get the regression model for the estimation of the lod or vaf based on the coverage.
        The hyperbola function is used for the regression model.

        :param data: The data for the regression model.
        :type data: pd.DataFrame
        :param lod_or_vaf: The y-column name for the regression model.
        :type lod_or_vaf: str
        :return: The regression model for the estimation of the lod or vaf.
        :rtype: np.ndarray
        """
        x = data["coverage"]
        y = data[lod_or_vaf]

        # Fit the hyperbola function to the data
        popt, _ = curve_fit(self.hyperbola, x, y)

        return popt

    def vaf_regression_model(self) -> np.ndarray:
        """
        Get the regression model for the estimation of the vaf based on the coverage.
        The hyperbola function is used for the regression model.

        :return: The regression model for the estimation of the vaf.
        :rtype: np.ndarray
        """
        df = pd.read_csv(
            f"{Path(__file__).parent.resolve()}/regression_models_data/vaf_data_for_regression.csv",
        )
        return self._get_regression_model(df, "vaf")

    def lod_tumor_regression_model(self) -> np.ndarray:
        """
        Get the regression model for the estimation of the lod based on the coverage.
        The hyperbola function is used for the regression model.

        :return: The regression model for the estimation of the lod.
        :rtype: np.ndarray
        """
        df = pd.read_csv(
            f"{Path(__file__).parent.resolve()}/regression_models_data/lod_data_for_regression.csv",
        )
        return self._get_regression_model(df, "lod")


class QCToolConfig:
    """
    Class for storing the configufractionn for the qc_tool.
    """

    # Dictionary for storing the stages functions

    uid_stage_name_dict: ClassVar[dict[str, Callable]] = {
        "f104e31c-b3f5-4a4c-8f3f-4cb164f8e2ea": average_coverage_v1_v2_ratio_check,
        "36ebebff-9f66-4278-8acd-1021081b0e73": average_coverage_completeness_v1_v2_check,
        "03d48698-caf1-4f03-9960-8bc643edfdc6": total_deduplicated_percentage_check,
        "cf5a1b22-1cc7-458d-b8df-0820be40fb96": off_target_check,
        "fdc7f9b6-9c4a-4301-a5fb-c0196e5ef969": number_of_reads_check,
        "e9a5fe97-d7b9-4bb9-917d-1d5b6396236c": vaf_lod_estimation,
        "1dbf8a3d-5b7b-42c3-bbb5-4b9f40823500": insert_size_fraction_estimation,
    }

    # Regression models configufractionn
    regression_models_config = RegressionModelsConfig()

    # Dictionary for storing the regression function and models
    regression_models: ClassVar[dict] = {
        "function": regression_models_config.hyperbola,
        "models": {
            "vaf": regression_models_config.vaf_regression_model(),
            "lod": regression_models_config.lod_tumor_regression_model(),
        },
    }

    def __init__(self):
        self.config = config

    @property
    def config_version(self) -> str:
        """
        Get the version of the configufractionn.

        :return: The version of the configufractionn.
        :rtype: str
        """
        return self.config["meta"]["config_version"]

    @property
    def check_stages(self) -> list:
        """
        Get the check stages of the qc_tool.

        :return: The checks of the qc_tool.
        :rtype: list
        """
        return self.config["stages"]["checks"]

    @property
    def estimation_stages(self) -> list:
        """
        Get the estimation stages of the qc_tool.

        :return: The check stages of the qc_tool.
        :rtype: list
        """
        return self.config["stages"]["estimations"]
