# coding: utf8
import os
import sys
import logging
import yaml


def log_init(log_filename, script_dir=None):
    """

    :param log_filename:
    :param script_dir:
    :return:
    """
    if not script_dir:
        script_dir = os.path.dirname(sys.argv[0])

    log_config = os.path.join(script_dir, 'conf/logging_conf.yaml')
    log_config_handler = yaml.load(open(log_config))
    if not os.path.exists(log_config_handler['logging']['log_path']):
        os.mkdir(log_config_handler['logging']['log_path'])

    log_filename = os.path.join(log_config_handler['logging']['log_path'], log_filename)
    logger = logging.getLogger('ops')

    # file output
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format=log_config_handler['logging']['log_format']
    )

    # console output
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_config_handler['logging']['log_format']))
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
    return logger



