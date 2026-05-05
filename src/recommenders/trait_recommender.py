"""Trait-aware frequency recommender."""

from collections import Counter

import pandas as pd

from src.context import Context
from src.recommenders.frequency import FrequencyRecommender


class TraitFrequencyRecommender(FrequencyRecommender):
    """Frequency recommender grouped by (champion, single_trait) pairs.
    
    For each player, iterates over all active team traits and 
    aggregates item occurrences per (champion, trait) pair.
    
    On recommend, votes are collected from all traits in the team
    context: items present in top-K for multiple traits are favored.
    Falls back to champion-only frequency if no relevant data.
    """
    
    def __init__(
        self,
        top_k: int = 3,
        placement_threshold: int = 2,
    ) -> None:
        super().__init__(top_k=top_k, placement_threshold=placement_threshold)
        self.champion_trait_items: dict[tuple[str, str], list[str]] = {}

    def fit(self, df: pd.DataFrame) -> None:
        """Learn (champion, trait) → top-K items mapping from data.
        
        Args:
            df: DataFrame with columns 'character_id', 'placement', 
                'num_items', 'itemNames', 'traits'.
        """
        super().fit(df)

        filtered = df[
            (df['placement'] <= self.placement_threshold) &
            (df['num_items'] > 0)
        ]

        pair_counters: dict[tuple[str, str], Counter] = {}
        for _, row in filtered.iterrows():
            champion = row['character_id']
            items = row['itemNames']
            traits_team = row['traits']
            for trait in traits_team:
                key = (champion, trait)
                if key not in pair_counters:
                    pair_counters[key] = Counter()
                pair_counters[key].update(items)
        
        self.champion_trait_items = {
            key: [item for item, _ in counter.most_common(self.top_k)]
            for key, counter in pair_counters.items()
        }

    def recommend(self, context: Context) -> list[str]:
        """Return top-K items aggregated across context traits.
        
        For each trait in context, looks up top-K items for 
        (context.champion, trait). Items appearing in top-K of 
        multiple traits get more votes.
        
        Args:
            context: Context with champion, tier, and traits.
        
        Returns:
            List of K item IDs. Falls back to champion-only 
            recommendation if traits are empty or no relevant data.
        """
        if not context.traits:
            return super().recommend(context)
        
        votes: Counter = Counter()
        for trait in context.traits:
            key = (context.champion, trait)
            if key in self.champion_trait_items:
                for item in self.champion_trait_items[key]:
                    votes[item] += 1
        
        if not votes:
            return super().recommend(context)
        
        return [item for item, _ in votes.most_common(self.top_k)]
    
    def __repr__(self) -> str:
        n = len(self.champion_trait_items)
        return f'TraitFrequencyRecommender(top_k={self.top_k}, fitted_on={n}_pairs)'