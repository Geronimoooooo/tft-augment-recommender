"""Fetch multiple recent matches and check augment availability."""

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
    match_ids = client.get_match_history(puuid, count=5)
    print(f'Got {len(match_ids)} match IDs')

    Path('data/raw/check').mkdir(parents=True, exist_ok=True)

    for i, match_id in enumerate(match_ids):
        print(f'\n--- Match {i+1}/{len(match_ids)}: {match_id} ---')
        match = client.get_match(match_id)
        if match is None:
            continue

        info = match['info']
        print(f'  queue_id:        {info.get("queue_id")}')
        print(f'  tft_game_type:   {info.get("tft_game_type")}')
        print(f'  tft_set_number:  {info.get("tft_set_number")}')

        # Check augments availability
        match_str = json.dumps(match)
        augment_count = match_str.lower().count('augment')
        print(f'  "augment" mentions: {augment_count}')

        # Save
        with open(f'data/raw/check/match_{i+1}.json', 'w') as f:
            json.dump(match, f, indent=2)

    print('\nAll matches saved to data/raw/check/')


if __name__ == '__main__':
    main()