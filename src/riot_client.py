"""Riot API client with rate limiting and error handling."""

import time
from typing import Optional

import requests

from src.config import (
    RATE_LIMIT_PER_2_MINUTES,
    RATE_LIMIT_PER_SECOND,
    RIOT_API_KEY,
    RIOT_PLATFORM_URL,
    RIOT_REGIONAL_URL,
)

class RiotClient:
    """Wrapper around Riot Games API with built-in rate limiting."""

    def __init__(self) -> None:
        """Initialize the client with API key and rate limit tracking."""
        self.api_key = RIOT_API_KEY
        self.headers = {'X-Riot-Token': self.api_key}
        self._request_times: list[float] = []

    def _wait_for_rate_limit(self) -> None:
        """Sleep if necessary to respect rate limits."""
        now = time.time()
        self._request_times = [t for t in self._request_times if now - t < 120]

        if len(self._request_times) >= RATE_LIMIT_PER_2_MINUTES:
            sleep_time = 120 - (now - self._request_times[0]) + 0.1
            print(f'  Rate limit (2-min): sleeping {sleep_time:.1f}s')
            time.sleep(sleep_time)

        recent = [t for t in self._request_times if now - t < 1]
        if len(recent) >= RATE_LIMIT_PER_SECOND:
            time.sleep(0.1)

    def _request(self, url: str, max_retries: int = 3) -> Optional[dict]:
        """Make a GET request with rate limiting, error handling, and retries.

        Args:
        url: Full URL to request.
        max_retries: Number of retries for network errors.

        Returns:
        JSON response as dict, or None if request failed permanently.
        """
        for attempt in range(max_retries):
            self._wait_for_rate_limit()

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                self._request_times.append(time.time())
            except requests.exceptions.ConnectionError as e:
                wait = 5 * (attempt + 1)  # 5s, 10s, 15s
                print(f'  Network error (attempt {attempt+1}/{max_retries}): {e}')
                print(f'  Waiting {wait}s before retry...')
                time.sleep(wait)
                continue
            except requests.exceptions.Timeout:
                print(f'  Timeout (attempt {attempt+1}/{max_retries})')
                time.sleep(5)
                continue

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 30))
                print(f'  429 Too Many Requests. Waiting {retry_after}s...')
                time.sleep(retry_after)
                continue
            elif response.status_code == 404:
                print(f'  404 Not Found: {url}')
                return None
            else:
                print(f'  Error {response.status_code}: {response.text[:200]}')
                return None

        print(f'  All {max_retries} retries exhausted for {url}')
        return None
        
    def get_match(self, match_id: str) -> Optional[dict]:
        """Fetch a TFT match by its ID.

        Args:
            match_id: Match ID like 'EUW1_7234567890'.

        Returns:
            Match JSON or None if not found.
        """
        url = f'{RIOT_REGIONAL_URL}/tft/match/v1/matches/{match_id}'
        return self._request(url)
    
    def get_summoner_by_name(self, summoner_name: str) -> Optional[dict]:
        """Fetch a summoner by their game name and tagline.

        Args:
            summoner_name: Format 'GameName#TagLine' (e.g., 'PlayerName#EUW').

        Returns:
            Summoner data with PUUID, or None.
        """
        if '#' not in summoner_name:
            raise ValueError("Summoner name must include tagline, e.g. 'Name#EUW'")
        name, tag = summoner_name.split('#', 1)
        url =f'{RIOT_REGIONAL_URL}/riot/account/v1/accounts/by-riot-id/{name}/{tag}'
        return self._request(url)
    
    def get_match_history(self, puuid: str, count: int = 20) -> Optional[list[str]]:
        """Fetch a player's recent TFT match IDs.

        Args:
            puuid: Player's PUUID (from get_summoner_by_name).
            count: Number of matches to fetch (max 100).

        Returns:
            List of match IDs.
        """
        url = (
            f'{RIOT_REGIONAL_URL}/tft/match/v1/matches/by-puuid/{puuid}/ids'
            f'?start=0&count={count}'
        )
        return self._request(url)
    
    def get_challenger_league(self) -> Optional[dict]:
        """Get current Challenger tier league for ranked TFT.

        Returns:
        Dict with 'entries' list of top players, each having 'puuid', 
        'leaguePoints', 'wins', etc.
        """
        url = f'{RIOT_PLATFORM_URL}/tft/league/v1/challenger'
        return self._request(url)
    
    def get_master_league(self) -> Optional[dict]:
        """Get current Master tier league for ranked TFT.

        Returns:
        Dict with 'entries' list of all Master players.
        Master tier is always populated, unlike Challenger
        which can be empty after a set transition.
        """
        url = f'{RIOT_PLATFORM_URL}/tft/league/v1/master'
        return self._request(url)