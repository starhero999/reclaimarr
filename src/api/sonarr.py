from pprint import pp
import requests
from typing import Any
from ..config import SONARR_URL, SONARR_API_KEY
from ..utils.logger import setup_logger

# Initialize logger
logger = setup_logger()


class SonarrClient:
    """
    A client for interacting with the Sonarr API.
    """

    def __init__(self, base_url: str = SONARR_URL, api_key: str = SONARR_API_KEY):
        """
        Initializes the SonarrClient.

        Args:
            base_url (str): The base URL of the Sonarr server.
            api_key (str): The API key for authentication.
        """
        if not base_url or not api_key:
            raise ValueError("Sonarr URL and API key must be provided.")

        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any | None:
        """
        Performs a GET request to a Sonarr API endpoint.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Sonarr GET endpoint {endpoint}: {e}")
            return None

    def _delete(self, endpoint: str, params: dict[str, Any] | None = None) -> bool:
        """
        Performs a DELETE request to a Sonarr API endpoint.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.delete(url, headers=self.headers, params=params, timeout=120)  # Longer timeout for series deletion
            response.raise_for_status()
            logger.info(f"Successfully executed DELETE on Sonarr endpoint {endpoint}.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Sonarr DELETE endpoint {endpoint}: {e}")
            return False

    def get_all_series(self) -> list[dict[str, Any]]:
        """
        Fetches all TV series from the Sonarr server.

        Returns:
            list[dict[str, Any]]: A list of series records.
        """
        logger.info("Fetching all series from Sonarr...")
        # The endpoint in the plan is /api/v3/series, which is correct.
        data = self._get("/api/v3/series")
        series = data if isinstance(data, list) else []
        logger.info(f"Found {len(series)} series in Sonarr.")
        return series

    def delete_series(self, sonarr_id: int, delete_files: bool = True) -> bool:
        """
        Deletes a series from Sonarr.

        Args:
            sonarr_id (int): The ID of the series in Sonarr.
            delete_files (bool): If True, also delete all series files from disk.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        logger.warning(f"Attempting to delete series with Sonarr ID: {sonarr_id} (delete_files={delete_files})")
        endpoint = f"/api/v3/series/{sonarr_id}"
        params = {"deleteFiles": str(delete_files).lower()}

        return self._delete(endpoint, params=params)


if __name__ == '__main__':
    # Example usage for testing the client
    # Note: This requires a running Sonarr instance and a valid .env file.

    logger = setup_logger(verbose=True)

    try:
        client = SonarrClient()

        # Test fetching series
        all_series = client.get_all_series()
        if all_series:
            logger.info(f"Successfully fetched {len(all_series)} series from Sonarr.")
            # Log the first series if available
            first_series = all_series[0]
            logger.debug(f"First series title: {first_series.get('title')}, ID: {first_series.get('id')}")
            pp(first_series)

            # Example of how deletion would be called (DO NOT RUN UNLESS INTENDED)
            # logger.info("This is a dry-run example. No actual deletion will occur.")
            # success = client.delete_series(first_series.get('id'), delete_files=False) # Dry run
            # if success:
            #     logger.info("Simulated deletion call was successful.")
            # else:
            #     logger.error("Simulated deletion call failed.")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during testing: {e}")
