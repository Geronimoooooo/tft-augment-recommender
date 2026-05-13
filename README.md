# TFT Item Recommender

A recommender system for items in Teamfight Tactics (Set 17),
trained on Master tier ranked matches via Riot API.

## Result

### Best configuration: trained on combined data, evaluated on new patch

| Recommender | Recall@3 | Precision@3 |
|---|---|---|
| Random (floor baseline) | 0.023 | 0.019 |
| Popularity | 0.131 | 0.114 |
| Frequency (per-champion) | 0.399 | 0.339 |
| Frequency + tier | 0.425 | 0.371 |
| Frequency + trait | 0.414 | 0.358 |
| **Hybrid (30/70)** | **0.4453** | **0.3815** |

Hybrid achieves **+32% relative Recall@3 improvement** over Frequency 
baseline (0.3363 → 0.4453) and **+19x relative Precision@3 improvement** 
over Random (0.019 → 0.3815) on the most realistic deployment configuration 
(combined training, fresh patch evaluation).

### Distribution shift testing

Tested 6 train/test combinations × 6 recommenders to measure model 
robustness across data distributions (pre-patch vs post-patch data).

Key findings:
1. Frequency-based models are patch-resilient (low degradation)
2. Tier feature value depends on sample size (negative on small, positive on large)
3. Combined training (old + new data) outperforms single-distribution training
4. Hybrid (composition) wins 6 of 7 configurations

## Project Story

Originally planned as augment recommender, pivoted to item recommender 
after discovering Riot API for Set 17 doesn't return augment data. 
Built incrementally with measurable improvements at each iteration:

- **Iteration 1:** Random / Popularity / Frequency baselines
- **Iteration 2:** Added tier feature (negative result)
- **Iteration 3:** Added traits feature (+2.3% Recall@3)
- **Distribution shift testing:** Combined training improves robustness
- **Iteration 4:** Hybrid recommender (composition pattern, weighted combination, +2.1%)

## Key Findings

**Distribution shift insight.** Combined training (old + new data) provides 
a more robust model than training on just one dataset. Frequency + tier 
model reached Recall@3 = 0.4246 on Combined → New, +4.6% vs single-distribution 
baseline. This contradicts the hypothesis that old data would introduce noise — 
in TFT meta changes gradually, and old data complements fresh patterns rather 
than contradicting them. Practical implication: for production, supplement 
pre-patch data with post-patch for robustness rather than discarding it.

**Hybrid via composition pattern.** Combined Tier and Trait recommenders 
through weighted score fusion. Grid search across 15 weight configurations 
identified (tier=0.3, trait=0.7) as fair optimum — Trait signal dominates 
(synergies define champion role), but Tier contributes meaningfully (build 
progression hints). Final Hybrid achieves Recall@3 = 0.4453.

**Architectural side effect.** Grid search revealed an interesting edge case: 
pure Trait through Hybrid (tier_weight=0) achieved Recall@3 = 0.4501, slightly 
above (0.3, 0.7). This is because composition pattern unions item candidates 
from both sub-recommenders, expanding what gets ranked. Chose non-zero tier 
weights for fair comparison.

## Stack

- **Language:** Python 3.12
- **ML:** scikit-learn, pandas
- **Data source:** Riot API (custom client with retries + checkpointing)
- **Dataset:** 731 Master tier matches across two collection windows 
  (April 28: 195 matches, May 5: 536 matches), Set 17 RU server

## Project Structure

```
tft-item-recommender/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── 00_data_discovery.ipynb
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── context.py
│   ├── evaluation.py
│   ├── preprocessing.py
│   ├── riot_client.py
│   └── recommenders/
│       ├── __init__.py
│       ├── frequency.py
│       ├── tier_frequency.py
│       ├── trait_recommender.py
│       ├── hybrid.py
│       ├── popularity_recommender.py
│       └── random_recommender.py
├── scripts/
│   ├── fetch_challenger_data.py
│   ├── distribution_combine_test.py
│   ├── find_best_weights.py
│   └── train_baseline.py
├── README.md
└── requirements.txt
```

## Iterations Log

| Iteration | Description | Recall@3 | vs prev |
|---|---|---|---|
| I1 | Frequency baseline (per-champion) | 0.3363 | — |
| I2 | Added tier feature | 0.3316 | -0.005 |
| I3 | Added traits feature | 0.3591 | +0.023 |
| Distribution shift | Combined training | 0.4246 | +0.066 |
| **I4** | **Hybrid (composition, 30/70)** | **0.4453** | **+0.021 (best)** |

Note: Combined → New configuration. Hybrid uses composition pattern 
with grid-searched weights (Trait dominates at 0.7, Tier contributes 0.3).

## Setup

```bash
git clone https://github.com/Geronimoooooo/tft-item-recommender.git
cd tft-item-recommender

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

echo "RIOT_API_KEY=your_key" > .env
```

## Usage

```bash
python -m scripts.fetch_challenger_data       # collect data
python -m scripts.train_baseline              # train + evaluate
python -m scripts.distribution_combine_test   # distribution shift testing
```

## About this project

Built as portfolio project demonstrating end-to-end ML engineering:
data collection (Riot API), preprocessing pipelines, baseline modeling,
feature engineering, hyperparameter optimization, distribution shift 
testing, and architectural patterns (inheritance, composition).
