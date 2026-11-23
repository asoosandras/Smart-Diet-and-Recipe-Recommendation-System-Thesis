# How to reproduce all results

## 1. Setup (once)

1. Install **Python 3.14**.
2. Run:
   ```
   python -m venv venv
   venv/Scripts/pip install -r requirements.txt
   ```
3. Put the Kaggle files (*Food.com Recipes and Interactions*) into this folder:
   - `RAW_recipes.csv`
   - `RAW_interactions.csv`
   - `PP_recipes.csv`
   - `ingr_map.pkl`

## 2. Run the notebooks in this order

| Order | Notebook | Reads | Writes |
|---|---|---|---|
| 1 | `thesis_code.ipynb` | raw files | EDA figures (Chapter 3.2) |
| 2 | `substitution_network.ipynb` | raw files, `merge_decisions.csv` | `substitution_edges.csv`, network figures, core list (Chapter 3.3) |
| 3 | `recommender.ipynb` | raw files, `substitution_edges.csv`, `merge_decisions.csv`, `pantry_rules.py` | `app_data/`, evaluation tables and figures (Chapter 3.4) |

To run one from the command line instead of opening it in Jupyter:
```
venv/Scripts/python -m jupyter nbconvert --to notebook --execute --inplace recommender.ipynb
```

Then start the app with `venv/Scripts/streamlit run app.py`.

## 3. Why the results are the same every time

- **No hidden randomness:**
  - every random step has a fixed seed (Louvain communities `seed=42`, network layout `seed=7`, validation sample `random_state=42`, simulation pantries `default_rng(42)`);
  - every ranking has a complete tie-breaker (recipe or ingredient id), so equal scores always appear in the same order.
- **Manual decisions are files, not memory:**
  - `merge_decisions.csv` (which ingredient names are merged);
  - `pantry_rules.py` (pantry groups, staples, categories, vegetarian rule);
  - `pantry_items.csv` (generated from the rules).
- **Editable decision files are kept on re-run:** `merge_decisions.csv` and `pantry_items.csv` are only created if missing. Your edits are kept; delete a file to regenerate it from the rules.
- **Fixed library versions:** `requirements.txt` pins the exact versions. Other versions will very likely give the same numbers, but only these were checked.

## 4. Check performed (2026-11-04)

- **`recommender.ipynb`:**
  - run twice from scratch (with `pantry_items.csv` deleted), with different Python hash seeds (`PYTHONHASHSEED=1` and `2`);
  - result: all 12 output files are byte-identical, figures included.
- **`substitution_network.ipynb`:**
  - re-run in a separate, empty folder;
  - result: its output files are identical to the ones in this folder.
