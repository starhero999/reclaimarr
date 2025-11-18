import logging
import sys


def setup_logger(verbose: bool = False) -> logging.Logger:
    """
    Set up and configure the application logger.

    Args:
        verbose (bool): If True, the log level is set to DEBUG. 
                        Otherwise, it is set to INFO.

    Returns:
        logging.Logger: A configured logger instance.
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create logger
    logger = logging.getLogger("reclaimarr")
    logger.setLevel(log_level)

    # Prevent duplicate handlers if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handler and formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Add handler to the logger
    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    # Example usage

    # 1. Default logger (INFO level)
    print("--- Testing INFO level logger ---")
    info_logger = setup_logger(verbose=False)
    info_logger.debug("This is a debug message. It should NOT be visible.")
    info_logger.info("This is an info message. It should be visible.")
    info_logger.warning("This is a warning message. It should be visible.")
    print("-" * 30)

    # 2. Verbose logger (DEBUG level)
    print("\n--- Testing DEBUG level logger ---")
    debug_logger = setup_logger(verbose=True)
    debug_logger.debug("This is a debug message. It should now be visible.")
    debug_logger.info("This is another info message.")
    print("-" * 30)
