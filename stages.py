"""
This module contains the functions for the qc_tool check stages.
"""

from pathlib import Path

import pandas as pd

from utilities import (
    download_file_from_s3,
    get_genes_list_with_low_coverage,
    get_inset_size_fraction_below_150,
    get_size_count_dict,
    normalize_size_count_dict,
    remove_files_in_dir,
    unarchive_tar_gz_file,
)
from values import BUCKET_NAME


def average_coverage_v1_v2_ratio_check(
    sample_df: pd.DataFrame,
    check_stage: dict,
) -> dict:
    """
    Check the ratio of the average coverage v1 and v2.
    If the ratio is less than the threshold, the check fails, otherwise it passes.

    :param sample_df: The data for the sample.
    :type sample_df: pd.DataFrame
    :param check_stage: The check stage.
    :type check_stage: dict
    :return: The result of the check.
    :rtype: dict
    """
    check_result = {}
    check_result["uid"] = check_stage["uid"]
    check_result["name"] = check_stage["name"]

    try:
        average_coverage_v1 = float(sample_df["average_coverage_v1"].iloc[0])
        average_coverage_v2 = float(sample_df["average_coverage_v2"].iloc[0])
        ratio = average_coverage_v1 / average_coverage_v2
    except (ZeroDivisionError, ValueError) as e:
        raise ValueError("The average coverage v1 or v2 is not a number.") from e

    if ratio < check_stage["params"]["threshold"]:
        check_result["status"] = check_stage["failed_status"]
        check_result["message"] = check_stage["failed_message"]
    else:
        check_result["status"] = check_stage["passed_status"]
        check_result["message"] = check_stage["passed_message"]

    return check_result


def average_coverage_completeness_v1_v2_check(
    sample_df: pd.DataFrame,
    check_stage: dict,
) -> dict:
    """
    Check the values of the average coverage completeness v1 and v2.
    If either value is less than the threshold, the check fails, otherwise it passes.

    :param sample_df: The data for the sample.
    :type sample_df: pd.DataFrame
    :param check_stage: The check stage.
    :type check_stage: dict
    :return: The result of the check.
    :rtype: dict
    """
    check_result = {}
    check_result["uid"] = check_stage["uid"]
    check_result["name"] = check_stage["name"]

    # Get the average coverage completeness v1 and v2
    try:
        average_coverage_completeness_v1 = float(
            sample_df["average_coverage_completeness_v1"].iloc[0],
        )
        average_coverage_completeness_v2 = float(
            sample_df["average_coverage_completeness_v2"].iloc[0],
        )
    except ValueError as e:
        raise ValueError(
            "The average coverage completeness v1 or v2 is not a number.",
        ) from e

    # If either value is less than the threshold, the check fails
    if (
        average_coverage_completeness_v1 < check_stage["params"]["threshold"]
        or average_coverage_completeness_v2 < check_stage["params"]["threshold"]
    ):
        run_name = sample_df["Run"].iloc[0]
        sample_id = sample_df["Sample sheet_Sample_ID"].iloc[0]
        tumor_normal = sample_df["Tumor/Normal"].iloc[0]

        try:
            sample_name_on_s3 = sample_id.split("-")[-1]
        except IndexError as e:
            raise ValueError("The sample id is not in the correct format.") from e

        # Path to the temporaty directory for storing the files
        files_dir = f"{Path(__file__).parent.resolve()}/tmp"
        # The path to the files on the S3 bucket
        object_key_prefix = f"{run_name}/{sample_name_on_s3}/output/ROI_QC/"

        if (
            average_coverage_completeness_v1 < check_stage["params"]["threshold"]
            and average_coverage_completeness_v2 < check_stage["params"]["threshold"]
        ):
            # The path to the local files
            v1_file_name = f"cfDNA-{tumor_normal}.V1.coverage-stats.genes.txt"
            v2_file_name = f"cfDNA-{tumor_normal}.V2.coverage-stats.genes.txt"
            # The path to the files on the S3 bucket
            object_key_v1 = f"{object_key_prefix}{v1_file_name}"
            object_key_v2 = f"{object_key_prefix}{v2_file_name}"
            # Download the file from the S3 bucket
            download_file_from_s3(
                BUCKET_NAME,
                object_key_v1,
                f"{files_dir}/{v1_file_name}",
            )
            download_file_from_s3(
                BUCKET_NAME,
                object_key_v2,
                f"{files_dir}/{v2_file_name}",
            )
            # Get the genes with low coverage
            v1_genes = get_genes_list_with_low_coverage(f"{files_dir}/{v1_file_name}")
            v2_genes = get_genes_list_with_low_coverage(f"{files_dir}/{v2_file_name}")
            # Remove the files in the temporary directory
            remove_files_in_dir(files_dir)

            check_result["status"] = check_stage["failed_status"]
            check_result["message"] = (
                f"average_coverage_completeness_v1 and average_coverage_completeness_v2 are {check_stage['failed_message']}"
            )
            check_result["data"] = {
                "v1_genes": v1_genes,
                "v2_genes": v2_genes,
            }

        elif average_coverage_completeness_v1 < check_stage["params"]["threshold"]:
            # The path to the local file
            file_name = f"cfDNA-{tumor_normal}.V1.coverage-stats.genes.txt"
            # The path to the file on the S3 bucket
            object_key = f"{object_key_prefix}{file_name}"
            # Download the file from the S3 bucket
            download_file_from_s3(BUCKET_NAME, object_key, f"{files_dir}/{file_name}")
            # Get the genes with low coverage
            v1_genes = get_genes_list_with_low_coverage(f"{files_dir}/{file_name}")

            # Remove the files in the temporary directory
            remove_files_in_dir(files_dir)

            check_result["status"] = check_stage["failed_status"]
            check_result["message"] = f"average_coverage_completeness_v1 is {check_stage['failed_message']}"
            check_result["data"] = {"v1_genes": v1_genes}

        elif average_coverage_completeness_v2 < check_stage["params"]["threshold"]:
            # The path to the local file
            file_name = f"cfDNA-{tumor_normal}.V2.coverage-stats.genes.txt"
            # The path to the file on the S3 bucket
            object_key = f"{object_key_prefix}{file_name}"
            # Download the file from the S3 bucket
            download_file_from_s3(BUCKET_NAME, object_key, f"{files_dir}/{file_name}")
            # Get the genes with low coverage
            v2_genes = get_genes_list_with_low_coverage(f"{files_dir}/{file_name}")
            # Remove the files in the temporary directory
            remove_files_in_dir(files_dir)

            check_result["status"] = check_stage["failed_status"]
            check_result["message"] = f"average_coverage_completeness_v2 is {check_stage['failed_message']}"
            check_result["data"] = {"v2_genes": v2_genes}

    else:
        check_result["status"] = check_stage["passed_status"]
        check_result["message"] = check_stage["passed_message"]

    return check_result


def total_deduplicated_percentage_check(
    sample_df: pd.DataFrame,
    check_stage: dict,
) -> dict:
    """
    Check the Total Deduplicated Percentage.
    If the value is higher than the threshold, the check fails, otherwise it passes.

    :param sample_df: The data for the sample.
    :type sample_df: pd.DataFrame
    :param check_stage: The check stage.
    :type check_stage: dict
    :return: The result of the check.
    :rtype: dict
    """
    check_result = {}
    check_result["uid"] = check_stage["uid"]
    check_result["name"] = check_stage["name"]

    try:
        total_deduplicated_percent = float(
            sample_df["Total Deduplicated Percentage"].iloc[0],
        )
    except ValueError as e:
        raise ValueError("The Total Deduplicated Percentage is not a number.") from e

    if total_deduplicated_percent > check_stage["params"]["threshold"]:
        check_result["status"] = check_stage["failed_status"]
        check_result["message"] = check_stage["failed_message"]
    else:
        check_result["status"] = check_stage["passed_status"]
        check_result["message"] = check_stage["passed_message"]

    return check_result


def off_target_check(sample_df: pd.DataFrame, check_stage: dict) -> dict:
    """_
    Check the Off Target.
    If the value is higher than the threshold, the check fails, otherwise it passes.

    :param sample_df: The data for the sample.
    :type sample_df: pd.DataFrame
    :param check_stage: The check stage.
    :type check_stage: dict
    :return: The result of the check.
    :rtype: dict
    """
    check_result = {}
    check_result["uid"] = check_stage["uid"]
    check_result["name"] = check_stage["name"]

    try:
        off_target = float(sample_df["Off-target, %"].iloc[0])
    except ValueError as e:
        raise ValueError("The Off Target is not a number.") from e

    if off_target > check_stage["params"]["threshold"]:
        check_result["status"] = check_stage["failed_status"]
        check_result["message"] = check_stage["failed_message"]
    else:
        check_result["status"] = check_stage["passed_status"]
        check_result["message"] = check_stage["passed_message"]

    return check_result


def number_of_reads_check(sample_df: pd.DataFrame, check_stage: dict) -> dict:
    """
    Check the Number of Reads.
    If the value is less than the threshold, the check fails, otherwise it passes.

    :param sample_df: The data for the sample.
    :type sample_df: pd.DataFrame
    :param check_stage: The check stage.
    :type check_stage: dict
    :return: The result of the check.
    :rtype: dict
    """
    check_result = {}
    check_result["uid"] = check_stage["uid"]
    check_result["name"] = check_stage["name"]

    try:
        number_of_reads = float(sample_df["Number_of_Reads_mln"].iloc[0])
    except ValueError as e:
        raise ValueError("The Number of reads is not a number.") from e

    if number_of_reads < check_stage["params"]["threshold"]:
        check_result["status"] = check_stage["failed_status"]
        needed_reads = round(check_stage["params"]["threshold"] - number_of_reads, 1)
        check_result["message"] = f"{check_stage['failed_message']}; {needed_reads} mln more reads are needed"
        check_result["data"] = {
            "needed_reads": needed_reads,
        }

    else:
        check_result["status"] = check_stage["passed_status"]
        check_result["message"] = check_stage["passed_message"]

    return check_result


def vaf_lod_estimation(
    sample_df: pd.DataFrame,
    estimation_stage: dict,
    regression_models: dict,
) -> dict:
    """
    Estimate the VAF and LOD of the sample based on the coverage for the tumor samples.

    :param sample_df: The data for the sample.
    :type sample_df: pd.DataFrame
    :param estimation_stage: The estimation stage.
    :type estimation_stage: dict
    :param regression_models: The regression models.
    :type regression_models: dict
    :return: The result of the estimation.
    :rtype: dict
    """
    estimation_result = {}
    estimation_result["uid"] = estimation_stage["uid"]
    estimation_result["name"] = estimation_stage["name"]

    # Get the sample id and the average coverage v1 and v2
    sample_id = sample_df["Sample sheet_Sample_ID"].iloc[0]

    try:
        tumor_normal = sample_id.split("-")[1]
    except IndexError as e:
        raise ValueError("The sample id is not in the correct format.") from e

    # estomate the VAF and LOD only for the tumor samples
    if tumor_normal == "tumor":
        try:
            average_coverage_v1 = float(sample_df["average_coverage_v1"].iloc[0])
            average_coverage_v2 = float(sample_df["average_coverage_v2"].iloc[0])
        except ValueError as e:
            raise ValueError("The average coverage v1 or v2 is not a number.") from e

        # Get the regression function
        regression_function = regression_models["function"]

        # Estimate the VAF for v1 and v2
        vaf_v1 = regression_function(
            average_coverage_v1,
            *regression_models["models"]["vaf"],
        )
        vaf_v2 = regression_function(
            average_coverage_v2,
            *regression_models["models"]["vaf"],
        )

        # Estimate the LOD for v1 and v2
        lod_v1 = regression_function(
            average_coverage_v1,
            *regression_models["models"]["lod"],
        )
        lod_v2 = regression_function(
            average_coverage_v2,
            *regression_models["models"]["lod"],
        )

        if any([vaf_v1 < 0, vaf_v2 < 0, lod_v1 < 0, lod_v2 < 0]):
            raise ValueError(
                "The estimated parameters are negative. The average coverage is too low.",
            )

        estimation_result["status"] = estimation_stage["completed_status"]

        estimation_result["data"] = {
            "vaf_v1": round(vaf_v1, 4),
            "vaf_v2": round(vaf_v2, 4),
            "lod_v1": round(lod_v1, 2),
            "lod_v2": round(lod_v2, 2),
        }

    elif tumor_normal == "normal":
        estimation_result["status"] = estimation_stage["skipped_status"]
        estimation_result["message"] = estimation_stage["skipped_message"]

    else:
        raise ValueError("The tumor/normal value is not tumor or normal.")

    return estimation_result


def insert_size_fraction_estimation(
    sample_df: pd.DataFrame,
    estimation_stage: dict,
) -> dict:
    """
    Reads fraction with insert_size < 150 bp estimation.

    :param sample_df: The data for the sample.
    :type sample_df: pd.DataFrame
    :param estimation_stage: The estimation stage.
    :type estimation_stage: dict
    :return: The result of the estimation.
    :rtype: dict
    """

    estimation_result = {}
    estimation_result["uid"] = estimation_stage["uid"]
    estimation_result["name"] = estimation_stage["name"]

    # Path to the temporaty directory for storing the files
    files_dir = f"{Path(__file__).parent.resolve()}/tmp"

    run_name = sample_df["Run"].iloc[0]
    sample_id = sample_df["Sample sheet_Sample_ID"].iloc[0]

    try:
        sample_name_on_s3 = sample_id.split("-")[-1]
    except IndexError as e:
        raise ValueError("The sample id is not in the correct format.") from e

    tumor_normal = sample_df["Tumor/Normal"].iloc[0]

    try:
        average_coverage_v1 = float(sample_df["average_coverage_v1"].iloc[0])
    except ValueError as e:
        raise ValueError("The average coverage v1 is not a number.") from e

    # The path to the file on the S3 bucket
    object_key = f"{run_name}/{sample_name_on_s3}/output/QC/cfDNA-{tumor_normal}.picard_output.tar.gz"
    # The path to the local file
    tar_name = "picard_output.tar.gz"

    # Download the file from the S3 bucket
    download_file_from_s3(BUCKET_NAME, object_key, f"{files_dir}/{tar_name}")
    # Unarchive the file
    unarchive_tar_gz_file(f"{files_dir}/{tar_name}", files_dir)
    # Get the size count dictionary
    size_count = get_size_count_dict(files_dir)
    # Normalize the size count dictionary
    normalized_size_count = normalize_size_count_dict(size_count, average_coverage_v1)
    # Get the fraction of the fractions with insert_size < 150 bp
    fraction = get_inset_size_fraction_below_150(normalized_size_count)
    # Remove the files in the temporary directory
    remove_files_in_dir(files_dir)

    estimation_result["status"] = estimation_stage["completed_status"]
    estimation_result["data"] = {"fraction": round(fraction, 4)}

    return estimation_result
