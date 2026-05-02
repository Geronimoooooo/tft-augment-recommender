"""Quick smoke test: fetch a match and print its key fields.

Usage:
    python -m scripts.fetch_match --summoner 'YourName#YourTag'
    python -m scripts.fetch_match --match-id 'EUW1_7234567890'
"""

import argparse
import json

from src.riot_client import RiotClient

def main() -> None:
    parser = argparse.ArgumentParser(description='Fetch a TFT match for testing')
    parser.add_argument('--summoner', help='Summoner name format "Name#Tag"')
    parser.add_argument('--match-id', help='Direct match ID')
    args = parser.parse_args()

    client = RiotClient()

    if args.match_id:
        match = client.get_match(args.match_id)
    elif args.summoner:
        print(f'Looking up: {args.summoner}')
        summoner = client.get_summoner_by_name(args.summoner)
        if summoner is None:
            print('Summoner not found.')
            return
        
        puuid = summoner['puuid']
        print(f'  PUUID: {puuid[:20]}...')

        match_ids = client.get_match_history(puuid, count=1)
        if not match_ids:
            print('No matches found')
            return
        
        match_id = match_ids[0]
        print(f'  Latest match: {match_id}')
        match = client.get_match(match_id)
    else:
        print('Provide --summoner or --match-id')
        return
    
    if match is None:
        print('Failed to fetch match.')
        return
    
    # Print key fields
    info = match['info']
    print(f'\n=== Match Info ===')
    print(f'Game type:   {info.get("tft_game_type")}')
    print(f'Set number:  {info.get("tft_set_number")}')
    print(f'Game length: {info.get("game_length"):.0f}s')
    print(f'Participants: {len(info["participants"])}')

    # First participant: list augments
    p = info['participants'][0]
    print(f'\n=== First Participant ===')
    print(f'Placement:  {p["placement"]}')
    print(f'Level:      {p["level"]}')
    print(f'Augments:   {p.get("augments", [])}')

    # Save raw response
    with open('data/raw/sample_match.json', 'w') as f:
        json.dump(match, f, indent=2)
    print('\nRaw match saved to data/raw/sample_match.json')

if __name__ == '__main__':
    main()