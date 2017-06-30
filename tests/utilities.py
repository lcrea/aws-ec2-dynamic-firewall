"""This module shouldn't contain any tests.
"""
import os


def get_example_config_path(file_name='config.example.json'):
    """Automatically find the absolute path of the example config.json file

    :param file_name: Configuration filename
    :type file_name: str

    :return: Absolute path of the configuration file
    :rtype: str
    """
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_dir, file_name)
