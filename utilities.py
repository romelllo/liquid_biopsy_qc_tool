"""
Module for utility functions.
"""

import json
import logging
import os

import boto3


def create_logger(
    name: str, file_path: str = None, file_name: str = None
) -> logging.Logger:
    """
    Create a logger.

    :param name: The name of the logger.
    :type name: str
    :param file_path: The path to the log file.
    :type file_path: str
    :param file_name: The name of the log file.
    :type file_name: str
    :return: The logger.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if file_path:
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        file_handler = logging.FileHandler(os.path.join(file_path, file_name), mode="w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def save_qc_tool_result_locally(result: dict, file_path: str, file_name: str) -> None:
    """
    Save the result of the qc_tool to a file.

    :param result: The result of the qc_tool.
    :type result: dict
    :param file_path: The path to the file.
    :type file_path: str
    :param file_name: The name of the file.
    :type file_name: str
    :return: None
    """
    with open(os.path.join(file_path, file_name), "w") as result_file:
        json.dump(result, result_file, indent=4)
    return None


def download_file_from_s3(
    bucket_name: str,
    object_key: str,
    local_file_path: str,
) -> None:
    """
    Download a file from an S3 bucket.

    :param bucket_name: The name of the bucket.
    :type bucket_name: str
    :param object_key: The key of the object.
    :type object_key: str
    :param local_file_path: The path to the local file.
    :type local_file_path: str
    """
    s3 = boto3.client("s3")
    try:
        s3.download_file(bucket_name, object_key, local_file_path)
    except Exception as e:
        raise Exception("An error occurred while downloading the file from S3.") from e


def unarchive_tar_gz_file(file_path: str, save_path: str) -> None:
    """
    Unarchive a .tar.gz file.

    :param file_path: The path to the file.
    :type file_path: str
    :param save_path: The path to save the extracted file.
    :type save_path: str
    """
    try:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        os.system(f"tar -xzf {file_path} -C {save_path}")
        os.remove(file_path)
    except Exception as e:
        raise Exception("An error occurred while unarchiving the file.") from e
    return None


def get_size_count_dict(files_dir: str) -> dict[int, int]:
    """
    Get the size count dictionary from a picard output file.

    :param files_dir: The path to the directory with the picard output files.
    :type files_dir: str
    :return: The size count dictionary.
    :rtype: dict[int, int]
    """
    for file in os.listdir(files_dir):
        if file.endswith("insert_size_metrics_2"):
            file_path = os.path.join(files_dir, file)
            break

    with open(file_path, "r") as f:
        lines = f.readlines()[1:]
        size_count = {}
        try:
            for line in lines:
                line = line.strip()
                # The size is the key and the count is the value
                size_count[int(line.split("\t")[1])] = int(line.split("\t")[2])
        except Exception as e:
            raise Exception("An error occurred while reading the file.") from e
        return size_count


def normalize_size_count_dict(
    size_count: dict[int, int], average_coverage_v1: float
) -> dict[int, float]:
    """
    Normalize the counts data to a average_coverage_v1.

    :param size_count: The size count dictionary.
    :type size_count: dict[int, int]
    :param average_coverage_v1: The average coverage for v1.
    :type average_coverage_v1: float
    :return: The normalized size count dictionary.
    :rtype: dict[int, float]
    """
    size_count_normalized = {}
    for insert, count in size_count.items():
        size_count_normalized[insert] = count / average_coverage_v1

    return size_count_normalized


def get_inset_size_fraction_below_150(size_count: dict[int, float]) -> float:
    """
    Get the fraction of the insert sizes below 150.

    :param size_count: The normalized size count dictionary.
    :type size_count: dict[int, float]
    :return: The fraction of the insert sizes below 150.
    :rtype: float
    """
    total_count = sum(size_count.values())
    count_below_150 = sum(
        [count for insert, count in size_count.items() if insert < 150]
    )
    return count_below_150 / total_count


def get_genes_list_with_low_coverage(file_path: str) -> list[str]:
    """
    Get the list of genes marked as False in a good column in the coverage-stats.genes.txt.

    :param file_path: The path to the file.
    :type file_path: str
    :return: The list of genes marked as False in a good column.
    :rtype: list[str]
    """
    with open(file_path, "r") as f:
        genes_list = []
        try:
            for line in f.readlines():
                if line.split()[-1] == "False":
                    genes_list.append(line.split()[0])
        except Exception as e:
            raise Exception("An error occurred while reading the file.") from e
        return genes_list


def remove_files_in_dir(dir_path: str) -> None:
    """
    Remove all files in a directory.

    :param dir_path: The path to the directory.
    :type dir_path: str
    :return: None
    """
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return None
