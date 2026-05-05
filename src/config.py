"""Configuration constants for TFT Augment Recommender."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ===Path====

PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED = PROJECT_ROOT / 'data' / 'processed'

#===RIOT API===

RIOT_API_KEY = os.getenv('RIOT_API_KEY')
RIOT_REGION = os.getenv('RIOT_REGION', 'europe')
RIOT_PLATFORM = os.getenv('RIOT_PLATFORM', 'euw1')

#===Riot API base urls===

RIOT_REGIONAL_URL = f'https://{RIOT_REGION}.api.riotgames.com'
RIOT_PLATFORM_URL = f'https://{RIOT_PLATFORM}.api.riotgames.com'

#===Limits===

RATE_LIMIT_PER_SECOND = 20
RATE_LIMIT_PER_2_MINUTES = 100

#===TFT Specific===

TFT_GAME_TYPE = 'standard'
TFT_QUEUE_TYPE = 'RANKED_TFT'
K = 3  # number of items to recommend per champion
PT = 2 # placement threshold parameeter: number of player's placement as a filter for data: placement <= 2 - taken, > 2 - skipped

#===Validation===

if RIOT_API_KEY is None:
    raise ValueError("RIOT_API_KEY not found."
        "Create a .env file in the project root with RIOT_API_KEY=your-key")