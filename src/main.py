import json
import sys
import time
from dataclasses import asdict
from datetime import datetime

from croniter import croniter
from .utils.logger import setup_logger
from .services.collector import DataCollector
from .services.analyzer import MediaAnalyzer
from .services.deleter import MediaDeleter
from .config import (
    ConfigError, MEDIA_PATH, TARGET_USAGE, MIN_AGE_DAYS, DRY_RUN, VERBOSE, CRON_SCHEDULE
)


def run_once():
    """
    Executes a single run of the media deletion logic.
    """
    logger = setup_logger(verbose=VERBOSE)
    logger.info("--- Reclaimarr Run Started ---")
    logger.info(f"Configuration: Target Usage={TARGET_USAGE}%, Min Age={MIN_AGE_DAYS} days, Dry Run={DRY_RUN}")

    try:
        # 1. Initialize services
        logger.info("Initializing core services...")
        collector = DataCollector()
        analyzer = MediaAnalyzer(min_age_days=MIN_AGE_DAYS)
        deleter = MediaDeleter()

        # 2. Collect and merge data
        logger.info("Starting data collection...")
        all_media = collector.collect_all_media()

        # Dump all_media to a JSON file for debugging
        if VERBOSE:
            logger.info("Dumping all_media to all_media.json...")
            try:
                # Convert list of dataclass objects to list of dicts for serialization
                all_media_dicts = [asdict(m) for m in all_media]
                with open("all_media.json", "w", encoding="utf-8") as f:
                    json.dump(all_media_dicts, f, indent=2, default=str, ensure_ascii=False)
                logger.info("Successfully dumped all_media to all_media.json.")
            except Exception as e:
                logger.error(f"Failed to dump all_media to JSON: {e}")

        # 3. Analyze and sort media for deletion
        logger.info("Analyzing media for deletion priority...")
        sorted_media = analyzer.analyze_and_sort(all_media)

        # 4. Execute deletion logic
        logger.info("Starting deletion process...")
        deleter.delete_until_target(
            sorted_media=sorted_media,
            target_usage=TARGET_USAGE,
            media_path=MEDIA_PATH,
            dry_run=DRY_RUN
        )

    except ConfigError as e:
        logger.error(f"Configuration Error: {e}")
        logger.error("Please ensure your .env file is correctly configured.")
        # In a loop, we don't want to exit, just log and wait for the next run
    except Exception as e:
        logger.error(f"An unexpected error occurred during run: {e}", exc_info=True)

    logger.info("--- Reclaimarr Run Finished ---")


def main():
    """
    Main entry point for the Reclaimarr application.
    Handles the scheduling loop.
    """
    logger = setup_logger(verbose=VERBOSE)
    logger.info("--- Reclaimarr Service Started ---")

    if not CRON_SCHEDULE:
        logger.info("No CRON_SCHEDULE found. Running once.")
        run_once()
        logger.info("--- Reclaimarr Service Finished ---")
        return

    logger.info(f"Scheduling runs with cron expression: '{CRON_SCHEDULE}'")
    base_time = datetime.now()
    cron = croniter(CRON_SCHEDULE, base_time)

    while True:
        next_run_time = cron.get_next(datetime)
        sleep_seconds = (next_run_time - datetime.now()).total_seconds()

        if sleep_seconds > 0:
            logger.info(f"Next run scheduled for: {next_run_time}. Sleeping for {sleep_seconds / 3600:.2f} hours.")
            time.sleep(sleep_seconds)

        run_once()


if __name__ == "__main__":
    main()
