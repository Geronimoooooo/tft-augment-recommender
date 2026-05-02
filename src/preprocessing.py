"""Data loading and preprocessing for TFT match data."""

import json
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import DATA_RAW

def load_match(path: Path) -> dict:
    """Load a single match JSON.
    
    Args:
        path: Path to match JSON file.
    
    Returns:
        Match data as dict.
    """
    with open(path, "r") as f:
        return json.load(f)
    
def load_all_matches(directory: Path) -> list[dict]:
    """Load all match JSONs from a directory.
    
    Args:
        directory: Path to folder containing JSON files.
    
    Returns:
        List of match dicts.
    """
    matches = []
    for file in directory.glob('*.json'):
        try:
            match = load_match(file)
            matches.append(match)
        except Exception as e:
            print(f'Error loading {file}: {e}')

    print(f'Loaded {len(matches)} matches from {directory}')
    return matches

def matches_to_unit_records(matches: list[dict]) -> pd.Dataframe:
    """Convert match data to a flat DataFrame: one row per (player, unit).
    
    Each row represents one champion in one player's final composition,
    with their items, the player's placement, and basic context.
    
    Args:
        matches: List of match dicts from Riot API.
    
    Returns:
        DataFrame with columns:
        - match_id, puuid, placement, level, last_round, queue_id
        - character_id (champion name)
        - tier (1-3 stars)
        - rarity (1-5 cost)
        - itemNames (list of item strings)
        - num_items (count)
    """
    rows = []
    for m in matches:
        match_id = m['metadata']['match_id']
        queue_id = m['info']['queue_id']
        for p in m['info']['participants']:
            puuid = p['puuid']
            placement = p['placement']
            level = p['level']
            last_round = p['last_round']
            for u in p.get('units', []):
                rows.append({
                    'match_id': match_id,
                    'puuid': puuid,
                    'queue_id': queue_id,
                    'placement': placement,
                    'level': level,
                    'last_round': last_round,
                    'character_id': u['character_id'],
                    'tier': u['tier'],
                    'rarity': u['rarity'],
                    'itemNames': u.get('itemNames', []),
                    'num_items': len(u.get('itemNames', []))
                })
    return pd.DataFrame(rows)