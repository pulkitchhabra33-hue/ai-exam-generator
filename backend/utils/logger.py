import logging

LOGGER_NAME= "exam-ai"

logger= logging.getLogger(LOGGER_NAME)

if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter= logging.Formatter(
        "[%(levelname)s] %(asctime)s - %(message)s",
        datefmt= "%H:%M:%S"
    )

    console_handler= logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
