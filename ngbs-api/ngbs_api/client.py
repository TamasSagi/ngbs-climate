import asyncio
import logging
from datetime import timedelta
from time import perf_counter
from typing import Optional, Self

import httpx

from .models import GeneralData, ThermostatData

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

    def __init__(self, ip: str, username: str, password: str) -> None:
        self.base_url = f"http://{ip}"
        self.username = username
        self.password = password
        self.client: Optional[httpx.AsyncClient] = None
        self._logged_in = False
        self._login_attempts = 0
        self._max_retries = 3

    async def __aenter__(self) -> Self:
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers=self.HEADERS,
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None

        self._logged_in = False

    async def _ensure_client(self):
        if self.client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

    async def _login(self) -> bool:
        """Login to the NGBS system. Returns True if successful."""
        await self._ensure_client()

        # Already logged in, skip
        if self._logged_in:
            logger.debug("Already logged in, skipping login")

            return True

        # Too many attempts, wait
        if self._login_attempts >= self._max_retries:
            logger.warning("Too many login attempts, waiting before retry")
            await asyncio.sleep(30)
            self._login_attempts = 0

        self._login_attempts += 1

        try:
            response = await self.client.post(
                f"{self.base_url}/index.php",
                data={"sysid": self.username, "password": self.password, "lang": "hu", "tab": "login"},
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("result") == "success":
                    logger.info("✅ Login successful!")
                    self._logged_in = True
                    self._login_attempts = 0

                    return True

                else:
                    logger.error(f"Login failed: {result}")

                    return False

            else:
                logger.error(f"Login HTTP error: {response.status_code}")

                return False

        except Exception as e:
            logger.error(f"Login exception: {e}")

            return False

    async def _check_session(self) -> bool:
        """Check if current session is still valid."""
        await self._ensure_client()

        if not self._logged_in:
            return False

        try:
            # Make a lightweight request to check session
            response = await self.client.post(f"{self.base_url}/index.php", data={"tab": "datapoll"}, timeout=5)

            if response.status_code == 200:
                data = response.json()
                # If we get valid data, session is good
                if "DP" in data or "SYSID" in data:
                    return True

        except Exception:
            pass

        # Session invalid
        self._logged_in = False
        logger.warning("Session expired, will re-login on next fetch")

        return False

    async def _ensure_logged_in(self) -> bool:
        """Ensure we're logged in, re-login if needed."""
        # Check if session is still valid
        if self._logged_in:
            if await self._check_session():
                return True

        # Attempt login
        return await self._login()

    async def _fetch_data(self) -> tuple[list[ThermostatData], GeneralData]:
        """Fetch thermostat and general data."""
        await self._ensure_client()

        # Ensure we're logged in first
        if not await self._ensure_logged_in():
            raise Exception("Failed to login")

        t0 = perf_counter()
        response = await self.client.post(f"{self.base_url}/index.php", data={"tab": "datapoll"})
        logger.debug(f"Got data in: {timedelta(seconds=(perf_counter() - t0))}")

        if response.status_code != 200:
            # If unauthorized, clear login state for next attempt
            if response.status_code in (401, 403):
                self._logged_in = False
            raise ValueError(f"Failed to fetch data: {response.status_code}")

        response_dict = response.json()

        # Check if we got an error response
        if response_dict.get("result") == "failure":
            logger.warning(f"API returned failure: {response_dict}")
            # Clear login state, will retry on next fetch
            self._logged_in = False
            raise Exception(f"API error: {response_dict}")

        thermostats = []
        if "DP" in response_dict:
            for dp_key, dp_value in response_dict["DP"].items():
                icon_id, thermo_id = dp_key.split(".")

                # Ignoring unused thermostat slots
                if dp_value.get("LIVE", 0):
                    thermostats.append(ThermostatData.from_response_dict(dp_value, int(icon_id), int(thermo_id)))
                else:
                    logger.debug(f"Ignoring thermostat {dp_key}, disabled!")
        else:
            logger.warning("Thermostat data is missing from iCON response!")

        # Sort by icon_id then thermostat id
        thermostats.sort(key=lambda t: (t.icon_id, t.thermo_id))

        general = GeneralData.from_response_dict(response_dict)

        return thermostats, general

    async def logout(self):
        """Logout from the system."""
        if self.client and self._logged_in:
            try:
                await self.client.post(f"{self.base_url}/index.php", data={"logout": "true"})
                logger.info("Logged out")
            except Exception as e:
                logger.error(f"Logout failed: {e}")
            finally:
                self._logged_in = False
