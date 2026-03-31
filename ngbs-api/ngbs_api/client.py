import logging
from datetime import timedelta
from time import perf_counter

import httpx

from .models import GeneralData, ThermostatsData

logger = logging.getLogger(__name__)


class NGBSClient:
    """Async NGBS API Client with session persistence."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,hu;q=0.8",
        "X-Requested-With": "XMLHttpRequest",
    }

    TIMEOUT = 30.0
    RETRIES = 3

    def __init__(self, ip: str, username: str, password: str) -> None:
        self.base_url = f"http://{ip}"
        self.username = username
        self.password = password  # FIXME: do not store plain text password? :)

        self.logged_in = False
        self.client = self.client = httpx.AsyncClient(timeout=self.TIMEOUT, headers=self.HEADERS)

    async def login(self) -> None:
        """Login to NGBS system with provided credentials"""
        response = await self.client.post(
            f"{self.base_url}/index.php",
            data={"sysid": self.username, "password": self.password, "lang": "hu", "tab": "login"},
        )

        if response.status_code == 200 and response.json().get("result") == "success":
            logger.info("✅ Login successful!")
            self.logged_in = True

            return

        logger.error(f"Login error! Response:\n{response}")

    async def _fetch_data(self) -> tuple[ThermostatsData, GeneralData]:
        """Fetch thermostat and general data."""
        if not self.logged_in:
            await self.login()

        t0 = perf_counter()
        response = await self.client.post(f"{self.base_url}/index.php", data={"tab": "datapoll"})
        logger.debug(f"Got data in: {timedelta(seconds=(perf_counter() - t0))}")

        if response.status_code != 200:
            # If unauthorized, clear login state for next attempt
            if response.status_code in (401, 403):
                self.logged_in = False

            raise ValueError(f"Failed to fetch data! Response:\n{response}")

        response_json = response.json()

        # Check if we got an error response
        if response_json.get("result") == "failure":
            logger.warning(f"API returned failure! Response JSON:\n{response_json}")

            # Clear login state, will retry on next fetch
            self.logged_in = False
            raise Exception(f"API error: {response_json}")

        thermostats = ThermostatsData.from_response(response_json)
        general = GeneralData.from_response_json(response_json)

        return thermostats, general
