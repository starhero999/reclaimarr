import requests
from typing import Any
from ..config import JELLYSTAT_URL, JELLYSTAT_API_KEY
from ..utils.logger import setup_logger

# Initialize logger
logger = setup_logger()


class JellystatClient:
    """
    A client for interacting with the Jellystat API.
    """

    def __init__(self, base_url: str = JELLYSTAT_URL, api_key: str = JELLYSTAT_API_KEY):
        """
        Initializes the JellystatClient.

        Args:
            base_url (str): The base URL of the Jellystat server.
            api_key (str): The API key for authentication.
        """
        if not base_url or not api_key:
            raise ValueError("Jellystat URL and API key must be provided.")

        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "x-api-token": self.api_key,
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any | None:
        """
        Performs a GET request to a Jellystat API endpoint.

        Args:
            endpoint (str): The API endpoint to call.
            params (dict[str, Any] | None): Query parameters for the request.

        Returns:
            Any | None: The JSON response from the API, or None if an error occurs.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Jellystat API endpoint {endpoint}: {e}")
            return None

    def get_playback_history(self) -> list[dict[str, Any]]:
        """
        Fetches all playback history from the Jellystat server.

        Returns:
            list[dict[str, Any]]: A list of playback activity records.
        """
        logger.info("Fetching playback history from Jellystat...")

        data = self._get("/stats/getPlaybackActivity")

        history = data if isinstance(data, list) else []

        logger.info(f"Found {len(history)} playback records in Jellystat.")
        return history


if __name__ == '__main__':
    import json

    logger = setup_logger(verbose=True)
    logger.info("--- Testing Jellystat Playback History ---")

    try:
        client = JellystatClient()
        playback_history = client.get_playback_history()

        if not playback_history:
            logger.warning("No playback history found.")
        else:
            logger.info(f"Successfully fetched {len(playback_history)} playback records.")
            logger.info("--- First Playback Record ---")
            logger.info(json.dumps(playback_history, indent=2))

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
