import logging


def config_logger():
    log_format = "%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s" # noqa

    logging.basicConfig(level=logging.INFO, format=log_format)

    return logging.getLogger()
