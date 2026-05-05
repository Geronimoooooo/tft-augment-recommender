"""Debug new traits column in DataFrame after preprocessing update."""

from pathlib import Path

from src.preprocessing import load_all_matches, matches_to_unit_records


def main() -> None:
    matches = load_all_matches(Path('data/raw/challenger'))
    df = matches_to_unit_records(matches)

    print('Columns:', df.columns.tolist())
    print()
    print('Sample traits column values:')
    print(df['traits'].head(10))
    print()
    print(f'Unique trait combinations: {df["traits"].nunique()}')
    print()
    print('Top 5 most common combinations:')
    print(df['traits'].value_counts().head(5))


if __name__ == '__main__':
    main()