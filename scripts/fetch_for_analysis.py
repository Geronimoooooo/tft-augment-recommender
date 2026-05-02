"""Fetch ~50 matches for data discovery analysis.

Goal: collect a small dataset to understand what data is available
in Riot API responses for TFT Set 17 matches.
"""

import json
from pathlib import Path

from src.riot_client import RiotClient

def main() -> None:
    client = RiotClient()

    summoner_name = 'Geronimooooo#RUS'

    summoner = client.get_summoner_by_name(summoner_name)
    if summoner is None:
        print('Summoner not found.')
        return
    
    puuid = summoner['puuid']
    print(f'Summoner PUUID: {puuid[:20]}')

    match_ids = client.get_match_history(puuid, count=50)
    print(f'Got {len(match_ids)} match IDs')

    output_dir = Path('data/raw/discovery')
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_count = 0
    for i, match_id in enumerate(match_ids):
        print(f'[{i+1}/{len(match_ids)}] Fetching {match_id}...', end=' ')
        
        match = client.get_match(match_id)
        if match is None:
            print('FAILED')
            continue
        
        with open(output_dir / f'{match_id}.json', 'w') as f:
            json.dump(match, f, indent=2)
        
        saved_count += 1
        print('OK')
    
    print(f'\nSaved {saved_count} matches to {output_dir}')

if __name__ == '__main__':
    main()