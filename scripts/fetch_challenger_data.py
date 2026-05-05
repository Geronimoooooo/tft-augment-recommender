"""Fetch matches from Master tier players (Set 17 only).

Saves intermediate progress to allow resumption after failures.
"""

import json
import argparse
from pathlib import Path

from src.riot_client import RiotClient


def main() -> None:
    client = RiotClient()

    print('Fetching Master league...')
    league = client.get_master_league()
    if league is None:
        print('Failed to fetch league.')
        return

    entries = league['entries']
    entries.sort(key=lambda e: e['leaguePoints'], reverse=True)
    top_players = entries[:100]
    print(f'Using top {len(top_players)} Master players by LP')

    parser = argparse.ArgumentParser(description='Fetch Master league TFT matches')
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw/challenger',
        help='Directory to save matches (default: data/raw/challenger)',
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    
    # Checkpoint file for resumption
    progress_file = output_dir / '_progress.json'
    processed_puuids = set()
    if progress_file.exists():
        with open(progress_file) as f:
            processed_puuids = set(json.load(f))
        print(f'Resuming: {len(processed_puuids)} players already processed')

    saved_count = len(list(output_dir.glob('*.json'))) - (1 if progress_file.exists() else 0)
    skipped_old_set = 0

    for i, player in enumerate(top_players):
        puuid = player['puuid']
        lp = player['leaguePoints']

        if puuid in processed_puuids:
            print(f'[{i+1}/{len(top_players)}] Skipping (already processed)')
            continue

        print(f'\n[{i+1}/{len(top_players)}] Player LP={lp}')

        match_ids = client.get_match_history(puuid, count=20)
        if not match_ids:
            processed_puuids.add(puuid)
            continue

        for match_id in match_ids:
            output_file = output_dir / f'{match_id}.json'
            if output_file.exists():
                continue  # already saved

            match = client.get_match(match_id)
            if match is None:
                continue

            set_number = match['info'].get('tft_set_number')
            if set_number != 17:
                skipped_old_set += 1
                continue

            with open(output_file, 'w') as f:
                json.dump(match, f, indent=2)
            saved_count += 1

        processed_puuids.add(puuid)

        # Save checkpoint after every player
        with open(progress_file, 'w') as f:
            json.dump(list(processed_puuids), f)

    print(f'\n=== Done ===')
    print(f'Total Set 17 matches in directory: {saved_count}')
    print(f'Old set matches skipped: {skipped_old_set}')
    print(f'Players processed: {len(processed_puuids)}')


if __name__ == '__main__':
    main()