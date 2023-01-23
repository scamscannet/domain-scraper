import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8', level=logging.INFO)


def set_logger_to(level: int):
    logging.getLogger().setLevel(level)
