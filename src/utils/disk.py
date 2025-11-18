import shutil
from ..utils.logger import setup_logger

logger = setup_logger()


def get_disk_usage(path: str) -> float | None:
    """
    Calculates the disk usage of the specified path as a percentage.

    Args:
        path (str): The file system path to check.

    Returns:
        float | None: The usage percentage (0-100) or None if an error occurs.
    """
    try:
        total, used, _ = shutil.disk_usage(path)
        if total == 0:
            logger.warning(f"Total disk space reported as zero for path: {path}")
            return 0.0

        usage_percent = (used / total) * 100
        logger.debug(f"Disk usage for '{path}': {usage_percent:.2f}%")
        return usage_percent
    except FileNotFoundError:
        logger.error(f"Error getting disk usage: The path '{path}' does not exist.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting disk usage for '{path}': {e}")
        return None


if __name__ == '__main__':
    # Example usage for testing the disk utility
    # Note: This will check the disk usage of the root directory '/'.

    logger.info("--- Testing Disk Utility ---")

    # Test with a valid path (e.g., root directory)
    # In a real scenario, this would be the media library path.
    path_to_check = "/"
    usage = get_disk_usage(path_to_check)
    if usage is not None:
        logger.info(f"Disk usage for '{path_to_check}': {usage:.2f}%")

    # Test with an invalid path
    logger.info("\n--- Testing with invalid path ---")
    invalid_path = "/non/existent/path"
    get_disk_usage(invalid_path)

    logger.info("----------------------------")
