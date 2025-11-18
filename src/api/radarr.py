from pprint import pp
import requests
from typing import Any
from ..config import RADARR_URL, RADARR_API_KEY
from ..utils.logger import setup_logger

# Initialize logger
logger = setup_logger()


class RadarrClient:
    """
    A client for interacting with the Radarr API.
    """

    def __init__(self, base_url: str = RADARR_URL, api_key: str = RADARR_API_KEY):
        """
        Initializes the RadarrClient.

        Args:
            base_url (str): The base URL of the Radarr server.
            api_key (str): The API key for authentication.
        """
        if not base_url or not api_key:
            raise ValueError("Radarr URL and API key must be provided.")

        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        # Note: Radarr uses `X-Api-Key` in the header, not a query parameter by default
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any | None:
        """
        Performs a GET request to a Radarr API endpoint.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Radarr GET endpoint {endpoint}: {e}")
            return None

    def _delete(self, endpoint: str, params: dict[str, Any] | None = None) -> bool:
        """
        Performs a DELETE request to a Radarr API endpoint.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.delete(url, headers=self.headers, params=params, timeout=60)  # Longer timeout for deletion
            response.raise_for_status()
            logger.info(f"Successfully executed DELETE on Radarr endpoint {endpoint}.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Radarr DELETE endpoint {endpoint}: {e}")
            return False

    def get_all_movies(self) -> list[dict[str, Any]]:
        """
        Fetches all movies from the Radarr server.

        Returns:
            list[dict[str, Any]]: A list of movie records.
        """
        logger.info("Fetching all movies from Radarr...")
        # The endpoint in the plan is /api/v3/movie, which is correct.
        data = self._get("/api/v3/movie")
        movies = data if isinstance(data, list) else []
        logger.info(f"Found {len(movies)} movies in Radarr.")
        return movies

    def delete_movie(self, radarr_id: int, delete_files: bool = True) -> bool:
        """
        Deletes a movie from Radarr.

        Args:
            radarr_id (int): The ID of the movie in Radarr.
            delete_files (bool): If True, also delete the movie file from disk.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        logger.warning(f"Attempting to delete movie with Radarr ID: {radarr_id} (delete_files={delete_files})")
        endpoint = f"/api/v3/movie/{radarr_id}"
        params = {"deleteFiles": str(delete_files).lower()}

        return self._delete(endpoint, params=params)


if __name__ == '__main__':
    # Example usage for testing the client
    # Note: This requires a running Radarr instance and a valid .env file.

    logger = setup_logger(verbose=True)

    try:
        client = RadarrClient()

        # Test fetching movies
        all_movies = client.get_all_movies()
        if all_movies:
            logger.info(f"Successfully fetched {len(all_movies)} movies from Radarr.")
            # Log the first movie if available
            first_movie = all_movies[0]
            logger.debug(f"First movie title: {first_movie.get('title')}, ID: {first_movie.get('id')}")
            pp(first_movie)

            # Example of how deletion would be called (DO NOT RUN UNLESS INTENDED)
            # logger.info("This is a dry-run example. No actual deletion will occur.")
            # success = client.delete_movie(first_movie.get('id'), delete_files=False) # Dry run
            # if success:
            #     logger.info("Simulated deletion call was successful.")
            # else:
            #     logger.error("Simulated deletion call failed.")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during testing: {e}")
